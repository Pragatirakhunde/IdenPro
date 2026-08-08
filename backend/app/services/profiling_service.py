from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from app.metadata.factory import MetadataExtractorFactory
from app.models.datasource import DataSource
from app.profiling.database_profiler import DatabaseProfiler
from app.profiling.models import (
    DashboardSummary,
    DatabaseProfile,
    ProfilingReport,
)


class ProfilingService:
    """
    Orchestrates the complete dataset profiling workflow.

    Workflow:

        DataSource
            ↓
        Metadata Extractor
            ↓
        Load DataFrames
            ↓
        DatabaseProfiler
            ↓
        ProfilingReport
            ↓
        Dashboard Summary
    """

    def __init__(self):

        self.database_profiler = DatabaseProfiler()

    # ======================================================
    # Helper
    # ======================================================

    def _now(self) -> str:

        return datetime.utcnow().isoformat()

    # ======================================================
    # Load Extractor
    # ======================================================

    def _extractor(
        self,
        datasource: DataSource,
    ):

        return MetadataExtractorFactory.create(
            datasource
        )

    # ======================================================
    # Load Tables
    # ======================================================

    def _load_tables(
        self,
        datasource: DataSource,
    ) -> dict[str, pd.DataFrame]:
        """
        Load datasource data.

        Expected result:

        {
            "customers": DataFrame,
            "orders": DataFrame
        }
        """

        extractor = self._extractor(
            datasource
        )

        tables = extractor.load_data()

        if tables is None:
            raise ValueError(
                "Extractor returned no data."
            )

        if isinstance(tables, pd.DataFrame):

            return {
                datasource.name: tables
            }

        if not isinstance(tables, dict):

            raise ValueError(
                "Extractor must return either "
                "a pandas DataFrame or "
                "dict[str, DataFrame]."
            )

        for table_name, dataframe in tables.items():

            if not isinstance(
                dataframe,
                pd.DataFrame,
            ):

                raise ValueError(
                    f"Extractor returned invalid "
                    f"data for '{table_name}'. "
                    f"Expected pandas DataFrame."
                )

        return tables

    # ======================================================
    # Dashboard
    # ======================================================

    def _dashboard(
        self,
        database_profile: DatabaseProfile,
    ) -> DashboardSummary:

        total_columns = sum(
            table.statistics.total_columns
            for table in database_profile.tables
        )

        total_rows = sum(
            table.statistics.total_rows
            for table in database_profile.tables
        )

        duplicate_rows = sum(
            table.statistics.duplicate_rows
            for table in database_profile.tables
        )

        missing_cells = sum(
            table.statistics.missing_cells
            for table in database_profile.tables
        )

        pii_columns = sum(
            1
            for table in database_profile.tables
            for column in table.columns
            if column.pii.contains_pii
        )

        anomaly_columns = sum(
            1
            for table in database_profile.tables
            for column in table.columns
            if column.anomaly.has_outliers
        )

        return DashboardSummary(
            total_tables=database_profile.statistics.total_tables,
            total_columns=total_columns,
            total_rows=total_rows,
            average_quality_score=(
                database_profile.quality.overall_score
            ),
            pii_columns=pii_columns,
            anomaly_columns=anomaly_columns,
            duplicate_rows=duplicate_rows,
            missing_cells=missing_cells,
        )

    # ======================================================
    # Database Profiling
    # ======================================================

    def _database_profile(
        self,
        datasource: DataSource,
        tables: dict[str, pd.DataFrame],
    ) -> DatabaseProfile:

        return self.database_profiler.profile_database(
            tables=tables,
            database_name=datasource.name,
        )

    # ======================================================
    # Profiling Report
    # ======================================================

    def _report(
        self,
        database_profile: DatabaseProfile,
    ) -> ProfilingReport:

        dashboard = self._dashboard(
            database_profile
        )

        return ProfilingReport(
            database_profile=database_profile,
            dashboard=dashboard,
        )

    # ======================================================
    # Dashboard Serialization
    # ======================================================

    def dashboard_dict(
        self,
        dashboard: DashboardSummary,
    ) -> dict[str, Any]:

        return {
            "total_tables": dashboard.total_tables,
            "total_columns": dashboard.total_columns,
            "total_rows": dashboard.total_rows,
            "average_quality_score": (
                dashboard.average_quality_score
            ),
            "pii_columns": dashboard.pii_columns,
            "anomaly_columns": dashboard.anomaly_columns,
            "duplicate_rows": dashboard.duplicate_rows,
            "missing_cells": dashboard.missing_cells,
        }

    # ======================================================
    # Report Serialization
    # ======================================================

    def report_dict(
        self,
        report: ProfilingReport,
    ) -> dict[str, Any]:

        return {
            "database": {
                "name": (
                    report.database_profile
                    .statistics
                    .database_name
                ),
                "tables": (
                    report.database_profile
                    .statistics
                    .total_tables
                ),
                "rows": (
                    report.database_profile
                    .statistics
                    .total_rows
                ),
                "columns": (
                    report.database_profile
                    .statistics
                    .total_columns
                ),
                "quality": (
                    report.database_profile
                    .quality
                    .overall_score
                ),
            },

            "dashboard": self.dashboard_dict(
                report.dashboard
            ),
        }

    # ======================================================
    # Health
    # ======================================================

    def health(
        self,
        report: ProfilingReport,
    ) -> dict[str, Any]:

        quality = (
            report.database_profile
            .quality
            .overall_score
        )

        if quality >= 95:
            quality_status = "Excellent"

        elif quality >= 90:
            quality_status = "Very Good"

        elif quality >= 80:
            quality_status = "Good"

        elif quality >= 70:
            quality_status = "Fair"

        elif quality >= 60:
            quality_status = "Poor"

        else:
            quality_status = "Critical"

        return {
            "status": quality_status,
            "quality_score": quality,
            "tables": (
                report.database_profile
                .statistics
                .total_tables
            ),
            "rows": (
                report.database_profile
                .statistics
                .total_rows
            ),
        }

    # ======================================================
    # Profile Datasource
    # ======================================================

    def profile_datasource(
        self,
        datasource: DataSource,
    ) -> ProfilingReport:

        tables = self._load_tables(
            datasource
        )

        database_profile = self._database_profile(
            datasource,
            tables,
        )

        return self._report(
            database_profile
        )

    # ======================================================
    # Profile Existing DataFrames
    # ======================================================

    def profile_tables(
        self,
        tables: dict[str, pd.DataFrame],
        database_name: str = "Uploaded Dataset",
    ) -> ProfilingReport:

        database_profile = (
            self.database_profiler.profile_database(
                tables=tables,
                database_name=database_name,
            )
        )

        return self._report(
            database_profile
        )

    # ======================================================
    # Summary
    # ======================================================

    def summary(
        self,
        report: ProfilingReport,
    ) -> dict[str, Any]:

        return {
            "database": (
                report.database_profile
                .statistics
                .database_name
            ),
            "tables": (
                report.database_profile
                .statistics
                .total_tables
            ),
            "rows": (
                report.database_profile
                .statistics
                .total_rows
            ),
            "columns": (
                report.database_profile
                .statistics
                .total_columns
            ),
            "quality": (
                report.database_profile
                .quality
                .overall_score
            ),
            "dashboard": self.dashboard_dict(
                report.dashboard
            ),
        }

    # ======================================================
    # Run
    # ======================================================

    def run(
        self,
        datasource: DataSource,
    ) -> dict[str, Any]:

        report = self.profile_datasource(
            datasource
        )

        return {
            "success": True,
            "generated_at": self._now(),

            "report": report,

            "summary": self.summary(
                report
            ),

            "health": self.health(
                report
            ),
        }

    # ======================================================
    # Safe Run
    # ======================================================

    def safe_run(
        self,
        datasource: DataSource,
    ) -> dict[str, Any]:

        try:

            return self.run(
                datasource
            )

        except Exception as exc:

            return {
                "success": False,
                "generated_at": self._now(),
                "error": str(exc),
                "report": None,
            }
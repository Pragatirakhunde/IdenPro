from __future__ import annotations

from typing import Any

import pandas as pd

from app.profiling.models import (
    DatabaseProfile,
    DatabaseStatistics,
    TableProfile,
)
from app.profiling.quality_scorer import QualityScorer
from app.profiling.table_profiler import TableProfiler


class DatabaseProfiler:
    """
    Profiles an entire database consisting of multiple tables.

    Responsibilities
    ----------------
    ✓ Profile every table
    ✓ Aggregate statistics
    ✓ Compute database quality
    ✓ Aggregate PII
    ✓ Aggregate anomalies
    """

    def __init__(
        self,
        table_profiler: TableProfiler | None = None,
    ):

        self.table_profiler = (
            table_profiler
            if table_profiler
            else TableProfiler()
        )

        self.quality_scorer = QualityScorer()

    # =====================================================
    # Table Profiling
    # =====================================================

    def _profile_tables(
        self,
        tables: dict[str, pd.DataFrame],
    ) -> list[TableProfile]:

        profiles: list[TableProfile] = []

        for table_name, dataframe in tables.items():

            profiles.append(

                self.table_profiler.profile_table(

                    dataframe=dataframe,

                    table_name=table_name,

                )

            )

        return profiles

    # =====================================================
    # Basic Database Statistics
    # =====================================================

    def _table_count(
        self,
        profiles: list[TableProfile],
    ) -> int:

        return len(profiles)

    # -----------------------------------------------------

    def _total_rows(
        self,
        profiles: list[TableProfile],
    ) -> int:

        return sum(

            table.statistics.total_rows

            for table in profiles

        )

    # -----------------------------------------------------

    def _total_columns(
        self,
        profiles: list[TableProfile],
    ) -> int:

        return sum(

            table.statistics.total_columns

            for table in profiles

        )

    # -----------------------------------------------------

    def _total_cells(
        self,
        profiles: list[TableProfile],
    ) -> int:

        return sum(

            table.statistics.total_rows

            *

            table.statistics.total_columns

            for table in profiles

        )

    # -----------------------------------------------------

    def _missing_cells(
        self,
        profiles: list[TableProfile],
    ) -> int:

        return sum(

            table.statistics.missing_cells

            for table in profiles

        )

    # -----------------------------------------------------

    def _duplicate_rows(
        self,
        profiles: list[TableProfile],
    ) -> int:

        return sum(

            table.statistics.duplicate_rows

            for table in profiles

        )

    # -----------------------------------------------------

    def _average_quality(
        self,
        profiles: list[TableProfile],
    ) -> float:

        if not profiles:

            return 100.0

        score = sum(

            table.quality.overall_score

            for table in profiles

        )

        return round(

            score / len(profiles),

            2,

        )

    # -----------------------------------------------------

    def _table_names(
        self,
        profiles: list[TableProfile],
    ) -> list[str]:

        return [

            table.statistics.table_name

            for table in profiles

        ]
        # =====================================================
    # PII Statistics
    # =====================================================

    def _pii_column_count(
        self,
        profiles: list[TableProfile],
    ) -> int:

        return sum(

            1

            for table in profiles

            for column in table.columns

            if column.pii.contains_pii

        )

    # -----------------------------------------------------

    def _pii_table_count(
        self,
        profiles: list[TableProfile],
    ) -> int:

        count = 0

        for table in profiles:

            if any(

                column.pii.contains_pii

                for column in table.columns

            ):

                count += 1

        return count

    # =====================================================
    # Anomaly Statistics
    # =====================================================

    def _anomaly_column_count(
        self,
        profiles: list[TableProfile],
    ) -> int:

        return sum(

            1

            for table in profiles

            for column in table.columns

            if column.anomaly.has_outliers

        )

    # -----------------------------------------------------

    def _tables_with_anomalies(
        self,
        profiles: list[TableProfile],
    ) -> int:

        count = 0

        for table in profiles:

            if any(

                column.anomaly.has_outliers

                for column in table.columns

            ):

                count += 1

        return count

    # =====================================================
    # Column Statistics
    # =====================================================

    def _numeric_column_count(
        self,
        profiles: list[TableProfile],
    ) -> int:

        total = 0

        for table in profiles:

            total += sum(

                1

                for column in table.columns

                if column.statistics.data_type.startswith(

                    (

                        "int",

                        "float",

                    )

                )

            )

        return total

    # -----------------------------------------------------

    def _text_column_count(
        self,
        profiles: list[TableProfile],
    ) -> int:

        total = 0

        for table in profiles:

            total += sum(

                1

                for column in table.columns

                if column.statistics.data_type == "object"

            )

        return total

    # =====================================================
    # Database Statistics
    # =====================================================

    def _database_statistics(
        self,
        database_name: str,
        profiles: list[TableProfile],
    ) -> DatabaseStatistics:

        return DatabaseStatistics(

            database_name=database_name,

            total_tables=self._table_count(
                profiles
            ),

            total_rows=self._total_rows(
                profiles
            ),

            total_columns=self._total_columns(
                profiles
            ),

            total_cells=self._total_cells(
                profiles
            ),

            missing_cells=self._missing_cells(
                profiles
            ),

            duplicate_rows=self._duplicate_rows(
                profiles
            ),

        )

    # =====================================================
    # Summary
    # =====================================================

    def _database_summary(
        self,
        profiles: list[TableProfile],
    ) -> dict[str, Any]:

        return {

            "tables":
                self._table_count(
                    profiles
                ),

            "rows":
                self._total_rows(
                    profiles
                ),

            "columns":
                self._total_columns(
                    profiles
                ),

            "missing_cells":
                self._missing_cells(
                    profiles
                ),

            "duplicate_rows":
                self._duplicate_rows(
                    profiles
                ),

            "average_quality":
                self._average_quality(
                    profiles
                ),

            "pii_tables":
                self._pii_table_count(
                    profiles
                ),

            "pii_columns":
                self._pii_column_count(
                    profiles
                ),

            "tables_with_anomalies":
                self._tables_with_anomalies(
                    profiles
                ),

            "anomaly_columns":
                self._anomaly_column_count(
                    profiles
                ),

            "numeric_columns":
                self._numeric_column_count(
                    profiles
                ),

            "text_columns":
                self._text_column_count(
                    profiles
                ),

        }
        # =====================================================
    # Aggregate Column Profiles
    # =====================================================

    def _all_column_profiles(
        self,
        table_profiles: list[TableProfile],
    ) -> list[ColumnProfile]:
        """
        Flatten all column profiles from every table.
        """

        columns: list[ColumnProfile] = []

        for table in table_profiles:

            columns.extend(
                table.columns
            )

        return columns

    # =====================================================
    # Database Quality
    # =====================================================

    def _database_quality(
        self,
        table_profiles: list[TableProfile],
    ) -> QualityMetrics:
        """
        Compute database-level quality metrics.
        """

        column_profiles = self._all_column_profiles(
            table_profiles
        )

        return self.quality_scorer.calculate(

            total_rows=self._total_rows(
                table_profiles
            ),

            duplicate_rows=self._duplicate_rows(
                table_profiles
            ),

            total_cells=self._total_cells(
                table_profiles
            ),

            missing_cells=self._missing_cells(
                table_profiles
            ),

            column_profiles=column_profiles,

        )

    # =====================================================
    # Quality Grade
    # =====================================================

    def _quality_grade(
        self,
        metrics: QualityMetrics,
    ) -> str:

        return self.quality_scorer.quality_grade(
            metrics.overall_score
        )

    # =====================================================
    # Database Health
    # =====================================================

    def _database_health(
        self,
        metrics: QualityMetrics,
    ) -> str:

        score = metrics.overall_score

        if score >= 95:
            return "Excellent"

        if score >= 90:
            return "Very Good"

        if score >= 80:
            return "Good"

        if score >= 70:
            return "Fair"

        if score >= 60:
            return "Poor"

        return "Critical"

    # =====================================================
    # Overview
    # =====================================================

    def _overview(
        self,
        database_name: str,
        table_profiles: list[TableProfile],
        quality: QualityMetrics,
    ) -> dict[str, Any]:
        """
        Dashboard-friendly overview.
        """

        return {

            "database_name": database_name,

            "tables": self._table_count(
                table_profiles
            ),

            "rows": self._total_rows(
                table_profiles
            ),

            "columns": self._total_columns(
                table_profiles
            ),

            "overall_quality":
                quality.overall_score,

            "quality_grade":
                self._quality_grade(
                    quality
                ),

            "health":
                self._database_health(
                    quality
                ),

            "pii_columns":
                self._pii_column_count(
                    table_profiles
                ),

            "tables_with_pii":
                self._pii_table_count(
                    table_profiles
                ),

            "anomaly_columns":
                self._anomaly_column_count(
                    table_profiles
                ),

            "tables_with_anomalies":
                self._tables_with_anomalies(
                    table_profiles
                ),

        }
        # =====================================================
    # Profile Database
    # =====================================================

    def profile_database(
        self,
        tables: dict[str, pd.DataFrame],
        database_name: str = "Unknown Database",
    ) -> DatabaseProfile:
        """
        Profile an entire database represented as a dictionary
        of pandas DataFrames.
        """

        # ------------------------------------------
        # Profile every table
        # ------------------------------------------

        table_profiles = self._profile_tables(
            tables
        )

        # ------------------------------------------
        # Database statistics
        # ------------------------------------------

        statistics = self._database_statistics(
            database_name=database_name,
            profiles=table_profiles,
        )

        # ------------------------------------------
        # Quality metrics
        # ------------------------------------------

        quality = self._database_quality(
            table_profiles
        )

        # ------------------------------------------
        # Build profile
        # ------------------------------------------

        return DatabaseProfile(

            statistics=statistics,

            quality=quality,

            tables=table_profiles,

        )

    # =====================================================
    # Profile Existing Table Profiles
    # =====================================================

    def profile_table_profiles(
        self,
        table_profiles: list[TableProfile],
        database_name: str = "Unknown Database",
    ) -> DatabaseProfile:
        """
        Build a DatabaseProfile directly from existing
        TableProfile objects.
        """

        statistics = self._database_statistics(
            database_name=database_name,
            profiles=table_profiles,
        )

        quality = self._database_quality(
            table_profiles
        )

        return DatabaseProfile(

            statistics=statistics,

            quality=quality,

            tables=table_profiles,

        )

    # =====================================================
    # Summary
    # =====================================================

    def summary(
        self,
        profile: DatabaseProfile,
    ) -> dict[str, Any]:
        """
        Dashboard-friendly summary.
        """

        overview = self._overview(

            database_name=profile.statistics.database_name,

            table_profiles=profile.tables,

            quality=profile.quality,

        )

        overview.update({

            "missing_cells":
                profile.statistics.missing_cells,

            "duplicate_rows":
                profile.statistics.duplicate_rows,

            "total_tables":
                profile.statistics.total_tables,

            "total_rows":
                profile.statistics.total_rows,

            "total_columns":
                profile.statistics.total_columns,

        })

        return overview

    # =====================================================
    # Export
    # =====================================================

    def export(
        self,
        profile: DatabaseProfile,
    ) -> dict[str, Any]:
        """
        Convert DatabaseProfile into a serializable dictionary.
        """

        return {

            "summary": self.summary(
                profile
            ),

            "quality": {

                "completeness":
                    profile.quality.completeness_score,

                "uniqueness":
                    profile.quality.uniqueness_score,

                "validity":
                    profile.quality.validity_score,

                "consistency":
                    profile.quality.consistency_score,

                "overall":
                    profile.quality.overall_score,

                "grade":
                    self._quality_grade(
                        profile.quality
                    ),

            },

            "table_count":
                len(profile.tables),

        }

    # =====================================================
    # Pipeline Entry
    # =====================================================

    def run(
        self,
        tables: dict[str, pd.DataFrame],
        database_name: str = "Unknown Database",
    ) -> dict[str, Any]:
        """
        Entry point used by the profiling pipeline.
        """

        profile = self.profile_database(

            tables=tables,

            database_name=database_name,

        )

        return {

            "profile": profile,

            "summary": self.summary(
                profile
            ),

            "export": self.export(
                profile
            ),

        }
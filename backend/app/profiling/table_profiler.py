from __future__ import annotations

from typing import Any

import pandas as pd
from app.profiling.quality_scorer import QualityScorer
from app.profiling.column_profiler import ColumnProfiler
from app.profiling.models import (
    ColumnProfile,
    QualityMetrics,
    TableProfile,
    TableStatistics,
)


class TableProfiler:
    """
    Profiles an entire dataframe (table).

    Responsibilities
    ----------------
    ✓ Table Statistics
    ✓ Column Profiling
    ✓ Missing Cell Statistics
    ✓ Duplicate Rows
    ✓ Quality Metrics
    ✓ PII Summary
    ✓ Anomaly Summary

    Returns
    -------
    TableProfile
    """

    def __init__(
        self,
        column_profiler: ColumnProfiler | None = None,
    ):

        self.column_profiler = (
            column_profiler
            if column_profiler
            else ColumnProfiler()
        )

        self.quality_scorer = QualityScorer()

    # =====================================================
    # Basic Table Statistics
    # =====================================================

    def _total_rows(
        self,
        dataframe: pd.DataFrame,
    ) -> int:

        return int(len(dataframe))

    # -----------------------------------------------------

    def _total_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> int:

        return int(len(dataframe.columns))

    # -----------------------------------------------------

    def _duplicate_rows(
        self,
        dataframe: pd.DataFrame,
    ) -> int:

        return int(

            dataframe.duplicated().sum()

        )

    # -----------------------------------------------------

    def _duplicate_percentage(
        self,
        dataframe: pd.DataFrame,
    ) -> float:

        rows = self._total_rows(
            dataframe
        )

        if rows == 0:
            return 0.0

        duplicates = self._duplicate_rows(
            dataframe
        )

        return round(

            (duplicates / rows) * 100,

            2,

        )

    # -----------------------------------------------------

    def _missing_cells(
        self,
        dataframe: pd.DataFrame,
    ) -> int:

        return int(

            dataframe.isna().sum().sum()

        )

    # -----------------------------------------------------

    def _total_cells(
        self,
        dataframe: pd.DataFrame,
    ) -> int:

        return (

            self._total_rows(dataframe)

            *

            self._total_columns(dataframe)

        )

    # -----------------------------------------------------

    def _missing_percentage(
        self,
        dataframe: pd.DataFrame,
    ) -> float:

        total = self._total_cells(
            dataframe
        )

        if total == 0:

            return 0.0

        missing = self._missing_cells(
            dataframe
        )

        return round(

            (missing / total) * 100,

            2,

        )

    # -----------------------------------------------------

    def _completeness_percentage(
        self,
        dataframe: pd.DataFrame,
    ) -> float:

        return round(

            100
            -
            self._missing_percentage(
                dataframe
            ),

            2,

        )

    # =====================================================
    # Column Profiling
    # =====================================================

    def _profile_columns(
        self,
        dataframe: pd.DataFrame,
    ) -> list[ColumnProfile]:

        profiles = []

        for column in dataframe.columns:

            profile = (

                self.column_profiler

                .profile_column(

                    dataframe[column]

                )

            )

            profiles.append(
                profile
            )

        return profiles

    # =====================================================
    # Helper Counts
    # =====================================================

    def _pii_column_count(
        self,
        profiles: list[ColumnProfile],
    ) -> int:

        return sum(

            1

            for profile in profiles

            if profile.pii.contains_pii

        )

    # -----------------------------------------------------

    def _anomaly_column_count(
        self,
        profiles: list[ColumnProfile],
    ) -> int:

        return sum(

            1

            for profile in profiles

            if profile.anomaly.has_outliers

        )

    # -----------------------------------------------------

    def _numeric_column_count(
        self,
        dataframe: pd.DataFrame,
    ) -> int:

        return int(

            dataframe.select_dtypes(

                include="number"

            ).shape[1]

        )

    # -----------------------------------------------------

    def _text_column_count(
        self,
        dataframe: pd.DataFrame,
    ) -> int:

        return int(

            dataframe.select_dtypes(

                include="object"

            ).shape[1]

        )

    # =====================================================
    # Table Statistics
    # =====================================================

    def _table_statistics(
        self,
        dataframe: pd.DataFrame,
        table_name: str,
    ) -> TableStatistics:
        """
        Build TableStatistics for the dataframe.
        """

        return TableStatistics(

            table_name=table_name,

            total_rows=self._total_rows(
                dataframe
            ),

            total_columns=self._total_columns(
                dataframe
            ),

            duplicate_rows=self._duplicate_rows(
                dataframe
            ),

            duplicate_percentage=self._duplicate_percentage(
                dataframe
            ),

            missing_cells=self._missing_cells(
                dataframe
            ),

            completeness_percentage=self._completeness_percentage(
                dataframe
            ),

        )

    # =====================================================
    # Column Aggregation
    # =====================================================

    def _column_summary(
        self,
        profiles: list[ColumnProfile],
    ) -> dict[str, int]:

        numeric = 0
        text = 0
        datetime_cols = 0
        boolean = 0

        pii = 0
        anomaly = 0

        for profile in profiles:

            dtype = (
                profile.statistics.data_type
                .lower()
            )

            if (
                "int" in dtype
                or
                "float" in dtype
            ):

                numeric += 1

            elif (
                "datetime"
                in dtype
            ):

                datetime_cols += 1

            elif (
                "bool"
                in dtype
            ):

                boolean += 1

            else:

                text += 1

            if profile.pii.contains_pii:

                pii += 1

            if profile.anomaly.has_outliers:

                anomaly += 1

        return {

            "numeric_columns": numeric,

            "text_columns": text,

            "datetime_columns": datetime_cols,

            "boolean_columns": boolean,

            "pii_columns": pii,

            "anomaly_columns": anomaly,

        }

    # =====================================================
    # Missing Values
    # =====================================================

    def _columns_with_missing(
        self,
        profiles: list[ColumnProfile],
    ) -> int:

        return sum(

            1

            for profile in profiles

            if profile.statistics.null_count > 0

        )

    # =====================================================
    # Duplicate Columns
    # =====================================================

    def _columns_with_duplicates(
        self,
        profiles: list[ColumnProfile],
    ) -> int:

        return sum(

            1

            for profile in profiles

            if profile.statistics.duplicate_count > 0

        )

    # =====================================================
    # Constant Columns
    # =====================================================

    def _constant_columns(
        self,
        profiles: list[ColumnProfile],
    ) -> int:

        count = 0

        for profile in profiles:

            info = profile.statistics.constant_info

            if (
                info is not None
                and
                info.is_constant
            ):

                count += 1

        return count

    # =====================================================
    # Quasi Constant Columns
    # =====================================================

    def _quasi_constant_columns(
        self,
        profiles: list[ColumnProfile],
    ) -> int:

        count = 0

        for profile in profiles:

            info = profile.statistics.constant_info

            if (
                info is not None
                and
                info.is_quasi_constant
            ):

                count += 1

        return count

    # =====================================================
    # Table Summary
    # =====================================================

    def _table_summary(
        self,
        dataframe: pd.DataFrame,
        profiles: list[ColumnProfile],
    ) -> dict[str, Any]:

        summary = self._column_summary(
            profiles
        )

        summary.update(

            {

                "rows": self._total_rows(
                    dataframe
                ),

                "columns": self._total_columns(
                    dataframe
                ),

                "missing_cells": self._missing_cells(
                    dataframe
                ),

                "duplicate_rows": self._duplicate_rows(
                    dataframe
                ),

                "columns_with_missing": self._columns_with_missing(
                    profiles
                ),

                "columns_with_duplicates": self._columns_with_duplicates(
                    profiles
                ),

                "constant_columns": self._constant_columns(
                    profiles
                ),

                "quasi_constant_columns": self._quasi_constant_columns(
                    profiles
                ),

            }

        )

        return summary

        # =====================================================
    # Quality Score Components
    # =====================================================

    def _completeness_score(
        self,
        dataframe: pd.DataFrame,
    ) -> float:
        """
        Percentage of non-missing cells.
        """

        return self._completeness_percentage(
            dataframe
        )

    # -----------------------------------------------------

    def _uniqueness_score(
        self,
        dataframe: pd.DataFrame,
    ) -> float:
        """
        Score based on duplicate rows.
        """

        return round(

            100.0
            -
            self._duplicate_percentage(
                dataframe
            ),

            2,

        )

    # -----------------------------------------------------

    def _validity_score(
        self,
        profiles: list[ColumnProfile],
    ) -> float:
        """
        Penalize columns containing anomalies.
        """

        if not profiles:
            return 100.0

        anomaly_columns = sum(

            1

            for profile in profiles

            if profile.anomaly.has_outliers

        )

        score = (

            100

            -

            (
                anomaly_columns

                /

                len(profiles)

            )

            * 100

        )

        return round(

            max(score, 0),

            2,

        )

    # -----------------------------------------------------

    def _consistency_score(
        self,
        profiles: list[ColumnProfile],
    ) -> float:
        """
        Penalize constant and quasi-constant columns.
        """

        if not profiles:
            return 100.0

        issues = 0

        for profile in profiles:

            info = profile.statistics.constant_info

            if info is None:
                continue

            if info.is_constant:

                issues += 1

            elif info.is_quasi_constant:

                issues += 0.5

        score = (

            100

            -

            (

                issues

                /

                len(profiles)

            )

            * 100

        )

        return round(

            max(score, 0),

            2,

        )

    # =====================================================
    # Overall Quality Score
    # =====================================================

    def _overall_score(
        self,
        completeness: float,
        uniqueness: float,
        validity: float,
        consistency: float,
    ) -> float:
        """
        Weighted average.
        """

        score = (

            (0.35 * completeness)

            +

            (0.25 * uniqueness)

            +

            (0.20 * validity)

            +

            (0.20 * consistency)

        )

        return round(

            score,

            2,

        )

    # =====================================================
    # Quality Metrics
    # =====================================================

    def _quality_metrics(
        self,
        dataframe: pd.DataFrame,
        profiles: list[ColumnProfile],
    ) -> QualityMetrics:

        return self.quality_scorer.calculate(

            total_rows=self._total_rows(
                dataframe
            ),

            duplicate_rows=self._duplicate_rows(
                dataframe
            ),

            total_cells=self._total_cells(
                dataframe
            ),

            missing_cells=self._missing_cells(
                dataframe
            ),

            column_profiles=profiles,

        )

    # =====================================================
    # Quality Grade
    # =====================================================

    def _quality_grade(
        self,
        score: float,
    ) -> str:

        if score >= 90:
            return "A"

        if score >= 80:
            return "B"

        if score >= 70:
            return "C"

        if score >= 60:
            return "D"

        return "F"

        # =====================================================
    # Profile Single Table
    # =====================================================

    def profile_table(
        self,
        dataframe: pd.DataFrame,
        table_name: str = "Unknown Table",
    ) -> TableProfile:
        """
        Profile an entire dataframe and return a TableProfile.
        """

        # ------------------------------------
        # Profile all columns
        # ------------------------------------

        column_profiles = self._profile_columns(
            dataframe
        )

        # ------------------------------------
        # Table statistics
        # ------------------------------------

        statistics = self._table_statistics(
            dataframe=dataframe,
            table_name=table_name,
        )

        # ------------------------------------
        # Quality metrics
        # ------------------------------------

        quality = self._quality_metrics(
            dataframe=dataframe,
            profiles=column_profiles,
        )

        # ------------------------------------
        # Final table profile
        # ------------------------------------

        return TableProfile(

            statistics=statistics,

            quality=quality,

            columns=column_profiles,

        )

    # =====================================================
    # Profile Multiple Tables
    # =====================================================

    def profile_tables(
        self,
        tables: dict[str, pd.DataFrame],
    ) -> list[TableProfile]:
        """
        Profile multiple dataframes.

        Example
        -------
        {
            "customers": customers_df,
            "orders": orders_df,
            "payments": payments_df,
        }
        """

        profiles: list[TableProfile] = []

        for table_name, dataframe in tables.items():

            profiles.append(

                self.profile_table(

                    dataframe=dataframe,

                    table_name=table_name,

                )

            )

        return profiles

    # =====================================================
    # Summary
    # =====================================================

    def summary(
        self,
        table_profile: TableProfile,
    ) -> dict[str, Any]:
        """
        Lightweight summary used by the dashboard.
        """

        columns = table_profile.columns

        pii_columns = sum(
            1
            for column in columns
            if column.pii.contains_pii
        )

        anomaly_columns = sum(
            1
            for column in columns
            if column.anomaly.has_outliers
        )

        return {

            "table_name":
                table_profile.statistics.table_name,

            "rows":
                table_profile.statistics.total_rows,

            "columns":
                table_profile.statistics.total_columns,

            "duplicate_rows":
                table_profile.statistics.duplicate_rows,

            "missing_cells":
                table_profile.statistics.missing_cells,

            "quality_score":
                table_profile.quality.overall_score,

            "quality_grade":
                self._quality_grade(
                    table_profile.quality.overall_score
                ),

            "pii_columns":
                pii_columns,

            "anomaly_columns":
                anomaly_columns,

        }

    # =====================================================
    # Pipeline Entry
    # =====================================================

    def run(
        self,
        dataframe: pd.DataFrame,
        table_name: str = "Unknown Table",
    ) -> dict[str, Any]:
        """
        Entry point used by the profiling pipeline.
        """

        profile = self.profile_table(
            dataframe=dataframe,
            table_name=table_name,
        )

        return {

            "summary": self.summary(
                profile
            ),

            "profile": profile,

        }
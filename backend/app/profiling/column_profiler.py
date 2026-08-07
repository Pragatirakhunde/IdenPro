from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any

import numpy as np
import pandas as pd

from app.profiling.models import (
    AnomalyReport,
    BooleanStatistics,
    CardinalityInfo,
    ColumnProfile,
    ColumnStatistics,
    ConstantColumnInfo,
    DatetimeStatistics,
    DistributionMetrics,
    PatternDetection,
    PIIDetection,
    TopValue,
)


class ColumnProfiler:
    """
    Profiles a single dataframe column.

    Features
    --------
    ✓ Missing values
    ✓ Duplicate values
    ✓ Numeric statistics
    ✓ Text statistics
    ✓ Datetime statistics
    ✓ Boolean statistics
    ✓ Pattern detection
    ✓ PII detection
    ✓ Cardinality
    ✓ Constant detection
    ✓ Outlier detection
    """

    # =====================================================
    # Regex Patterns
    # =====================================================

    EMAIL_REGEX = re.compile(
        r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    )

    PHONE_REGEX = re.compile(
        r'^\+?\d[\d\s-]{8,15}$'
    )

    URL_REGEX = re.compile(
        r'^https?://'
    )

    UUID_REGEX = re.compile(
        r'^[0-9a-fA-F]{8}-'
    )

    PINCODE_REGEX = re.compile(
        r'^\d{6}$'
    )

    PAN_REGEX = re.compile(
        r'^[A-Z]{5}[0-9]{4}[A-Z]$'
    )

    AADHAAR_REGEX = re.compile(
        r'^\d{12}$'
    )

    # =====================================================
    # Constructor
    # =====================================================

    def __init__(
        self,
        sample_size: int = 5,
        top_values_limit: int = 10,
    ):

        self.sample_size = sample_size

        self.top_values_limit = top_values_limit

    # =====================================================
    # Utility Methods
    # =====================================================

    def _safe_percentage(
        self,
        value: int,
        total: int,
    ) -> float:

        if total == 0:
            return 0.0

        return round(
            (value / total) * 100,
            2,
        )

    # -----------------------------------------------------

    def _clean_series(
        self,
        series: pd.Series,
    ) -> pd.Series:

        return series.dropna()

    # -----------------------------------------------------

    def _numeric_series(
        self,
        series: pd.Series,
    ) -> pd.Series:

        return (

            pd.to_numeric(

                series,

                errors="coerce",

            )

            .dropna()

        )

    # -----------------------------------------------------

    def _sample_values(
        self,
        series: pd.Series,
    ) -> list[Any]:

        values = (

            series

            .dropna()

            .head(self.sample_size)

            .tolist()

        )

        return values

    # -----------------------------------------------------

    def _duplicate_count(
        self,
        series: pd.Series,
    ) -> int:

        return int(

            series.duplicated().sum()

        )

    # -----------------------------------------------------

    def _unique_count(
        self,
        series: pd.Series,
    ) -> int:

        return int(

            series.nunique(

                dropna=True

            )

        )

    # -----------------------------------------------------

    def _memory_usage(
        self,
        series: pd.Series,
    ) -> int:

        return int(

            series.memory_usage(

                deep=True

            )

        )

    # -----------------------------------------------------

    def _is_numeric(
        self,
        series: pd.Series,
    ) -> bool:

        return pd.api.types.is_numeric_dtype(
            series
        )

    # -----------------------------------------------------

    def _is_datetime(
        self,
        series: pd.Series,
    ) -> bool:

        return pd.api.types.is_datetime64_any_dtype(
            series
        )

    # -----------------------------------------------------

    def _is_boolean(
        self,
        series: pd.Series,
    ) -> bool:

        return pd.api.types.is_bool_dtype(
            series
        )

    # -----------------------------------------------------

    def _column_category(
        self,
        series: pd.Series,
    ) -> str:

        if self._is_numeric(series):

            return "NUMERIC"

        if self._is_datetime(series):

            return "DATETIME"

        if self._is_boolean(series):

            return "BOOLEAN"

        return "TEXT"

    # -----------------------------------------------------

    def _entropy(
        self,
        series: pd.Series,
    ) -> float:

        values = (

            series

            .dropna()

            .astype(str)

        )

        if values.empty:

            return 0.0

        probabilities = (

            values

            .value_counts(

                normalize=True

            )

        )

        entropy = -sum(

            p * math.log2(p)

            for p in probabilities

        )

        return round(
            entropy,
            4,
        )

    # -----------------------------------------------------

    def _mode(
        self,
        series: pd.Series,
    ):

        values = series.mode()

        if values.empty:

            return None

        return values.iloc[0]

        # =====================================================
    # Pattern Detection
    # =====================================================

    def _detect_pattern(
        self,
        series: pd.Series,
    ) -> PatternDetection:

        values = (
            series
            .dropna()
            .astype(str)
            .head(500)
        )

        if values.empty:
            return PatternDetection()

        counters = {
            "EMAIL": 0,
            "PHONE": 0,
            "URL": 0,
            "UUID": 0,
            "PINCODE": 0,
            "PAN": 0,
            "AADHAAR": 0,
        }

        matched_examples = {
            key: []
            for key in counters
        }

        for value in values:

            value = value.strip()

            if self.EMAIL_REGEX.fullmatch(value):
                counters["EMAIL"] += 1
                matched_examples["EMAIL"].append(value)

            elif self.PHONE_REGEX.fullmatch(value):
                counters["PHONE"] += 1
                matched_examples["PHONE"].append(value)

            elif self.URL_REGEX.match(value):
                counters["URL"] += 1
                matched_examples["URL"].append(value)

            elif self.UUID_REGEX.match(value):
                counters["UUID"] += 1
                matched_examples["UUID"].append(value)

            elif self.PINCODE_REGEX.fullmatch(value):
                counters["PINCODE"] += 1
                matched_examples["PINCODE"].append(value)

            elif self.PAN_REGEX.fullmatch(value):
                counters["PAN"] += 1
                matched_examples["PAN"].append(value)

            elif self.AADHAAR_REGEX.fullmatch(value):
                counters["AADHAAR"] += 1
                matched_examples["AADHAAR"].append(value)

        pattern = max(
            counters,
            key=counters.get,
        )

        count = counters[pattern]

        if count == 0:
            return PatternDetection()

        confidence = round(
            count / len(values),
            2,
        )

        return PatternDetection(
            detected_pattern=pattern,
            confidence=confidence,
            examples=matched_examples[pattern][:5],
        )

    # =====================================================
    # PII Detection
    # =====================================================

    def _detect_pii(
        self,
        pattern: PatternDetection,
    ) -> PIIDetection:

        pii_patterns = {
            "EMAIL",
            "PHONE",
            "AADHAAR",
            "PAN",
        }

        if (
            pattern.detected_pattern
            not in pii_patterns
        ):
            return PIIDetection()

        return PIIDetection(

            contains_pii=True,

            pii_type=pattern.detected_pattern,

            confidence=pattern.confidence,

            matched_examples=pattern.examples,

        )

    # =====================================================
    # Top Values
    # =====================================================

    def _top_values(
        self,
        series: pd.Series,
    ) -> list[TopValue]:

        counts = (
            series
            .dropna()
            .value_counts()
            .head(self.top_values_limit)
        )

        result = []

        total = len(series)

        for value, count in counts.items():

            result.append(

                TopValue(

                    value=str(value),

                    count=int(count),

                    percentage=self._safe_percentage(
                        int(count),
                        total,
                    ),

                )

            )

        return result

    # =====================================================
    # Cardinality
    # =====================================================

    def _cardinality(
        self,
        series: pd.Series,
    ) -> CardinalityInfo:

        total = len(series)

        unique = self._unique_count(
            series
        )

        ratio = (
            unique / total
            if total
            else 0
        )

        if ratio >= 0.90:

            level = "HIGH"

        elif ratio >= 0.30:

            level = "MEDIUM"

        else:

            level = "LOW"

        return CardinalityInfo(

            unique_values=unique,

            ratio=round(
                ratio,
                4,
            ),

            level=level,

        )

    # =====================================================
    # Constant Detection
    # =====================================================

    def _constant_info(
        self,
        series: pd.Series,
    ) -> ConstantColumnInfo:

        unique = series.nunique(
            dropna=False
        )

        if unique <= 1:

            return ConstantColumnInfo(

                is_constant=True,

                is_quasi_constant=False,

                dominant_ratio=1.0,

            )

        frequencies = (
            series
            .value_counts(
                normalize=True,
                dropna=False,
            )
        )

        dominant = (
            float(frequencies.iloc[0])
            if not frequencies.empty
            else 0
        )

        return ConstantColumnInfo(

            is_constant=False,

            is_quasi_constant=(
                dominant >= 0.95
            ),

            dominant_ratio=round(
                dominant,
                4,
            ),

        )

    # =====================================================
    # Missing Values
    # =====================================================

    def _missing_statistics(
        self,
        series: pd.Series,
    ) -> tuple[int, float]:

        missing = int(
            series.isna().sum()
        )

        percentage = self._safe_percentage(
            missing,
            len(series),
        )

        return (
            missing,
            percentage,
        )

    # =====================================================
    # Duplicate Statistics
    # =====================================================

    def _duplicate_statistics(
        self,
        series: pd.Series,
    ) -> tuple[int, float]:

        duplicate = self._duplicate_count(
            series
        )

        percentage = self._safe_percentage(
            duplicate,
            len(series),
        )

        return (
            duplicate,
            percentage,
        )

    # =====================================================
    # Basic Column Statistics
    # =====================================================

    def _basic_statistics(
        self,
        series: pd.Series,
    ) -> dict:

        missing_count, missing_percentage = (
            self._missing_statistics(
                series
            )
        )

        duplicate_count, duplicate_percentage = (
            self._duplicate_statistics(
                series
            )
        )

        return {

            "row_count": len(series),

            "null_count": missing_count,

            "null_percentage": missing_percentage,

            "unique_count": self._unique_count(
                series
            ),

            "unique_percentage": self._safe_percentage(

                self._unique_count(series),

                len(series),

            ),

            "duplicate_count": duplicate_count,

            "duplicate_percentage": duplicate_percentage,

            "sample_values": self._sample_values(
                series
            ),

        }

        # =====================================================
    # Numeric Statistics
    # =====================================================

    def _numeric_statistics(
        self,
        series: pd.Series,
    ) -> tuple[
        float | None,
        float | None,
        float | None,
        float | None,
        float | None,
    ]:

        clean = self._numeric_series(series)

        if clean.empty:
            return (
                None,
                None,
                None,
                None,
                None,
            )

        return (

            float(clean.min()),

            float(clean.max()),

            round(float(clean.mean()), 4),

            round(float(clean.median()), 4),

            round(float(clean.std()), 4),

        )

    # =====================================================
    # Distribution Metrics
    # =====================================================

    def _distribution_metrics(
        self,
        series: pd.Series,
    ) -> DistributionMetrics:

        clean = self._numeric_series(series)

        if clean.empty:
            return DistributionMetrics()

        return DistributionMetrics(

            variance=round(
                float(clean.var()),
                4,
            ),

            skewness=round(
                float(clean.skew()),
                4,
            ),

            kurtosis=round(
                float(clean.kurt()),
                4,
            ),

            q1=round(
                float(clean.quantile(0.25)),
                4,
            ),

            median=round(
                float(clean.quantile(0.50)),
                4,
            ),

            q3=round(
                float(clean.quantile(0.75)),
                4,
            ),

        )

    # =====================================================
    # Outlier Detection (IQR Method)
    # =====================================================

    def _detect_numeric_outliers(
        self,
        series: pd.Series,
    ) -> AnomalyReport:

        clean = self._numeric_series(series)

        if clean.empty:
            return AnomalyReport()

        q1 = clean.quantile(0.25)
        q3 = clean.quantile(0.75)

        iqr = q3 - q1

        lower = q1 - (1.5 * iqr)
        upper = q3 + (1.5 * iqr)

        outliers = clean[
            (clean < lower)
            |
            (clean > upper)
        ]

        return AnomalyReport(

            has_outliers=len(outliers) > 0,

            outlier_count=int(
                len(outliers)
            ),

            outlier_percentage=self._safe_percentage(

                len(outliers),

                len(clean),

            ),

            lower_bound=round(
                float(lower),
                4,
            ),

            upper_bound=round(
                float(upper),
                4,
            ),

            examples=outliers.head(5).tolist(),

        )

    # =====================================================
    # Numeric Column Profile
    # =====================================================

    def _profile_numeric(
        self,
        series: pd.Series,
    ) -> tuple[
        ColumnStatistics,
        AnomalyReport,
    ]:

        (
            minimum,
            maximum,
            mean,
            median,
            std,
        ) = self._numeric_statistics(series)

        basic = self._basic_statistics(
            series
        )

        stats = ColumnStatistics(

            column_name=str(series.name),

            data_type=str(series.dtype),

            row_count=basic["row_count"],

            null_count=basic["null_count"],

            null_percentage=basic["null_percentage"],

            unique_count=basic["unique_count"],

            unique_percentage=basic["unique_percentage"],

            duplicate_count=basic["duplicate_count"],

            duplicate_percentage=basic["duplicate_percentage"],

            min_value=minimum,

            max_value=maximum,

            mean=mean,

            median=median,

            std_dev=std,

            sample_values=basic["sample_values"],

            distribution=self._distribution_metrics(
                series
            ),

            cardinality=self._cardinality(
                series
            ),

            constant_info=self._constant_info(
                series
            ),

        )

        anomaly = self._detect_numeric_outliers(
            series
        )

        return (

            stats,

            anomaly,

        )

        # =====================================================
    # Text Statistics
    # =====================================================

    def _text_statistics(
        self,
        series: pd.Series,
    ) -> tuple[
        float | None,
        int | None,
        int | None,
    ]:

        values = (
            series
            .dropna()
            .astype(str)
        )

        if values.empty:
            return (
                None,
                None,
                None,
            )

        lengths = values.str.len()

        return (

            round(
                float(lengths.mean()),
                2,
            ),

            int(lengths.min()),

            int(lengths.max()),

        )

    # =====================================================
    # Datetime Statistics
    # =====================================================

    def _datetime_statistics(
        self,
        series: pd.Series,
    ) -> DatetimeStatistics:

        dates = pd.to_datetime(
            series,
            errors="coerce",
        ).dropna()

        if dates.empty:
            return DatetimeStatistics()

        return DatetimeStatistics(

            minimum=dates.min(),

            maximum=dates.max(),

            range_days=int(
                (
                    dates.max()
                    -
                    dates.min()
                ).days
            ),

        )

    # =====================================================
    # Boolean Statistics
    # =====================================================

    def _boolean_statistics(
        self,
        series: pd.Series,
    ) -> BooleanStatistics:

        values = (
            series
            .dropna()
            .astype(bool)
        )

        if values.empty:
            return BooleanStatistics()

        true_count = int(values.sum())

        false_count = int(
            len(values)
            -
            true_count
        )

        return BooleanStatistics(

            true_count=true_count,

            false_count=false_count,

            true_percentage=self._safe_percentage(
                true_count,
                len(values),
            ),

            false_percentage=self._safe_percentage(
                false_count,
                len(values),
            ),

        )

    # =====================================================
    # Text Column Profile
    # =====================================================

    def _profile_text(
        self,
        series: pd.Series,
    ) -> tuple[
        ColumnStatistics,
        PatternDetection,
        PIIDetection,
    ]:

        basic = self._basic_statistics(
            series
        )

        avg_len, min_len, max_len = (
            self._text_statistics(
                series
            )
        )

        pattern = self._detect_pattern(
            series
        )

        pii = self._detect_pii(
            pattern
        )

        stats = ColumnStatistics(

            column_name=str(series.name),

            data_type=str(series.dtype),

            row_count=basic["row_count"],

            null_count=basic["null_count"],

            null_percentage=basic["null_percentage"],

            unique_count=basic["unique_count"],

            unique_percentage=basic["unique_percentage"],

            duplicate_count=basic["duplicate_count"],

            duplicate_percentage=basic["duplicate_percentage"],

            sample_values=basic["sample_values"],

            average_length=avg_len,

            minimum_length=min_len,

            maximum_length=max_len,

            top_values=self._top_values(
                series
            ),

            cardinality=self._cardinality(
                series
            ),

            constant_info=self._constant_info(
                series
            ),

        )

        return (

            stats,

            pattern,

            pii,

        )

    # =====================================================
    # Datetime Column Profile
    # =====================================================

    def _profile_datetime(
        self,
        series: pd.Series,
    ) -> ColumnStatistics:

        basic = self._basic_statistics(
            series
        )

        return ColumnStatistics(

            column_name=str(series.name),

            data_type=str(series.dtype),

            row_count=basic["row_count"],

            null_count=basic["null_count"],

            null_percentage=basic["null_percentage"],

            unique_count=basic["unique_count"],

            unique_percentage=basic["unique_percentage"],

            duplicate_count=basic["duplicate_count"],

            duplicate_percentage=basic["duplicate_percentage"],

            sample_values=basic["sample_values"],

            datetime_statistics=self._datetime_statistics(
                series
            ),

            cardinality=self._cardinality(
                series
            ),

            constant_info=self._constant_info(
                series
            ),

        )

    # =====================================================
    # Boolean Column Profile
    # =====================================================

    def _profile_boolean(
        self,
        series: pd.Series,
    ) -> ColumnStatistics:

        basic = self._basic_statistics(
            series
        )

        return ColumnStatistics(

            column_name=str(series.name),

            data_type=str(series.dtype),

            row_count=basic["row_count"],

            null_count=basic["null_count"],

            null_percentage=basic["null_percentage"],

            unique_count=basic["unique_count"],

            unique_percentage=basic["unique_percentage"],

            duplicate_count=basic["duplicate_count"],

            duplicate_percentage=basic["duplicate_percentage"],

            sample_values=basic["sample_values"],

            boolean_statistics=self._boolean_statistics(
                series
            ),

            cardinality=self._cardinality(
                series
            ),

            constant_info=self._constant_info(
                series
            ),

        )

        # =====================================================
    # Profile Single Column
    # =====================================================

    def profile_column(
        self,
        series: pd.Series,
    ) -> ColumnProfile:
        """
        Profile a single pandas Series and return a ColumnProfile.
        """

        category = self._column_category(series)

        # Default values
        statistics = None
        anomaly = AnomalyReport()
        pattern = PatternDetection()
        pii = PIIDetection()

        # -------------------------------
        # Numeric
        # -------------------------------
        if category == "NUMERIC":

            statistics, anomaly = self._profile_numeric(
                series
            )

            pattern = self._detect_pattern(
                series
            )

            pii = self._detect_pii(
                pattern
            )

        # -------------------------------
        # Text
        # -------------------------------
        elif category == "TEXT":

            (
                statistics,
                pattern,
                pii,
            ) = self._profile_text(
                series
            )

        # -------------------------------
        # Datetime
        # -------------------------------
        elif category == "DATETIME":

            statistics = self._profile_datetime(
                series
            )

        # -------------------------------
        # Boolean
        # -------------------------------
        elif category == "BOOLEAN":

            statistics = self._profile_boolean(
                series
            )

        else:

            # Fallback for unsupported dtypes
            basic = self._basic_statistics(series)

            statistics = ColumnStatistics(
                column_name=str(series.name),
                data_type=str(series.dtype),
                row_count=basic["row_count"],
                null_count=basic["null_count"],
                null_percentage=basic["null_percentage"],
                unique_count=basic["unique_count"],
                unique_percentage=basic["unique_percentage"],
                duplicate_count=basic["duplicate_count"],
                duplicate_percentage=basic["duplicate_percentage"],
                sample_values=basic["sample_values"],
            )

        return ColumnProfile(
            statistics=statistics,
            pattern=pattern,
            pii=pii,
            anomaly=anomaly,
        )

    # =====================================================
    # Profile DataFrame
    # =====================================================

    def profile_dataframe(
        self,
        dataframe: pd.DataFrame,
    ) -> list[ColumnProfile]:
        """
        Profile all columns in a dataframe.
        """

        profiles: list[ColumnProfile] = []

        for column in dataframe.columns:

            profile = self.profile_column(
                dataframe[column]
            )

            profiles.append(profile)

        return profiles

    # =====================================================
    # Profile Summary
    # =====================================================

    def profile_summary(
        self,
        dataframe: pd.DataFrame,
    ) -> dict[str, Any]:
        """
        Generate a quick summary of the dataframe.
        """

        profiles = self.profile_dataframe(dataframe)

        total_columns = len(profiles)

        numeric_columns = sum(
            1
            for profile in profiles
            if profile.statistics.data_type.startswith(
                (
                    "int",
                    "float",
                )
            )
        )

        text_columns = sum(
            1
            for profile in profiles
            if profile.statistics.data_type == "object"
        )

        datetime_columns = sum(
            1
            for profile in profiles
            if "datetime"
            in profile.statistics.data_type
        )

        boolean_columns = sum(
            1
            for profile in profiles
            if profile.statistics.data_type == "bool"
        )

        pii_columns = sum(
            1
            for profile in profiles
            if profile.pii.contains_pii
        )

        anomaly_columns = sum(
            1
            for profile in profiles
            if profile.anomaly.has_outliers
        )

        return {

            "rows": len(dataframe),

            "columns": total_columns,

            "numeric_columns": numeric_columns,

            "text_columns": text_columns,

            "datetime_columns": datetime_columns,

            "boolean_columns": boolean_columns,

            "pii_columns": pii_columns,

            "anomaly_columns": anomaly_columns,

        }

    # =====================================================
    # Convenience Method
    # =====================================================

    def run(
        self,
        dataframe: pd.DataFrame,
    ) -> dict[str, Any]:
        """
        Entry point used by the profiling pipeline.
        """

        return {

            "summary": self.profile_summary(
                dataframe
            ),

            "columns": self.profile_dataframe(
                dataframe
            ),

        }
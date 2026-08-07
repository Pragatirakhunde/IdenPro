from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


# ============================================================
# Distribution Metrics
# ============================================================

@dataclass
class DistributionMetrics:
    """
    Distribution statistics for numeric columns.
    """

    variance: float | None = None

    skewness: float | None = None

    kurtosis: float | None = None

    q1: float | None = None

    median: float | None = None

    q3: float | None = None


# ============================================================
# Cardinality
# ============================================================

@dataclass
class CardinalityInfo:
    """
    Information about uniqueness.
    """

    unique_values: int = 0

    ratio: float = 0.0

    level: str = "LOW"


# ============================================================
# Constant Column
# ============================================================

@dataclass
class ConstantColumnInfo:

    is_constant: bool = False

    is_quasi_constant: bool = False

    dominant_ratio: float | None = None


# ============================================================
# Top Values
# ============================================================

@dataclass
class TopValue:

    value: str

    count: int

    percentage: float


# ============================================================
# Datetime Statistics
# ============================================================

@dataclass
class DatetimeStatistics:

    minimum: datetime | None = None

    maximum: datetime | None = None

    range_days: int | None = None


# ============================================================
# Boolean Statistics
# ============================================================

@dataclass
class BooleanStatistics:

    true_count: int = 0

    false_count: int = 0

    true_percentage: float = 0.0

    false_percentage: float = 0.0


# ============================================================
# Column Statistics
# ============================================================

@dataclass
class ColumnStatistics:

    column_name: str

    data_type: str

    row_count: int

    null_count: int

    null_percentage: float

    unique_count: int

    unique_percentage: float

    duplicate_count: int

    duplicate_percentage: float

    min_value: Any = None

    max_value: Any = None

    mean: float | None = None

    median: float | None = None

    std_dev: float | None = None

    sample_values: list[Any] = field(default_factory=list)

    # NEW

    average_length: float | None = None

    minimum_length: int | None = None

    maximum_length: int | None = None

    distribution: DistributionMetrics | None = None

    cardinality: CardinalityInfo | None = None

    constant_info: ConstantColumnInfo | None = None

    datetime_statistics: DatetimeStatistics | None = None

    boolean_statistics: BooleanStatistics | None = None

    top_values: list[TopValue] = field(default_factory=list)


# ============================================================
# Pattern Detection
# ============================================================

@dataclass
class PatternDetection:

    detected_pattern: str | None = None

    confidence: float = 0.0

    examples: list[str] = field(default_factory=list)


# ============================================================
# PII
# ============================================================

@dataclass
class PIIDetection:

    contains_pii: bool = False

    pii_type: str | None = None

    confidence: float = 0.0

    matched_examples: list[str] = field(default_factory=list)


# ============================================================
# Anomaly
# ============================================================

@dataclass
class AnomalyReport:

    has_outliers: bool = False

    outlier_count: int = 0

    outlier_percentage: float = 0.0

    lower_bound: float | None = None

    upper_bound: float | None = None

    examples: list[Any] = field(default_factory=list)


# ============================================================
# Column Profile
# ============================================================

@dataclass
class ColumnProfile:

    statistics: ColumnStatistics

    pattern: PatternDetection

    pii: PIIDetection

    anomaly: AnomalyReport


# ============================================================
# Table Statistics
# ============================================================

@dataclass
class TableStatistics:

    table_name: str

    total_rows: int

    total_columns: int

    duplicate_rows: int

    duplicate_percentage: float

    missing_cells: int

    completeness_percentage: float


# ============================================================
# Quality Metrics
# ============================================================

@dataclass
class QualityMetrics:

    completeness_score: float

    uniqueness_score: float

    validity_score: float

    consistency_score: float

    overall_score: float


# ============================================================
# Table Profile
# ============================================================

@dataclass
class TableProfile:

    statistics: TableStatistics

    quality: QualityMetrics

    columns: list[ColumnProfile] = field(default_factory=list)


# ============================================================
# Database Profile
# ============================================================
# ============================================================
# Database Statistics
# ============================================================

@dataclass
class DatabaseStatistics:

    database_name: str

    total_tables: int

    total_rows: int

    total_columns: int

    total_cells: int

    missing_cells: int

    duplicate_rows: int


@dataclass
class DatabaseProfile:

    statistics: DatabaseStatistics

    quality: QualityMetrics

    tables: list[TableProfile] = field(default_factory=list)
# ============================================================
# Dashboard
# ============================================================

@dataclass
class DashboardSummary:

    total_tables: int

    total_columns: int

    total_rows: int

    average_quality_score: float

    pii_columns: int

    anomaly_columns: int

    duplicate_rows: int

    missing_cells: int


# ============================================================
# Final Report
# ============================================================

@dataclass
class ProfilingReport:

    database_profile: DatabaseProfile

    dashboard: DashboardSummary
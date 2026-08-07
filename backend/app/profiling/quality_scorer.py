from __future__ import annotations

from app.profiling.models import (
    ColumnProfile,
    QualityMetrics,
)


class QualityScorer:
    """
    Computes data quality scores from a collection of column profiles.

    Dimensions
    ----------
    • Completeness
    • Uniqueness
    • Validity
    • Consistency

    Produces an overall weighted score.
    """

    def __init__(
        self,
        completeness_weight: float = 0.35,
        uniqueness_weight: float = 0.25,
        validity_weight: float = 0.20,
        consistency_weight: float = 0.20,
    ):

        total = (
            completeness_weight
            + uniqueness_weight
            + validity_weight
            + consistency_weight
        )

        if round(total, 5) != 1.0:
            raise ValueError(
                "Quality score weights must sum to 1.0"
            )

        self.completeness_weight = completeness_weight
        self.uniqueness_weight = uniqueness_weight
        self.validity_weight = validity_weight
        self.consistency_weight = consistency_weight

    # =====================================================
    # Completeness
    # =====================================================

    def completeness_score(
        self,
        total_cells: int,
        missing_cells: int,
    ) -> float:

        if total_cells == 0:
            return 100.0

        score = (
            (total_cells - missing_cells)
            / total_cells
        ) * 100

        return round(score, 2)

    # =====================================================
    # Uniqueness
    # =====================================================

    def uniqueness_score(
        self,
        total_rows: int,
        duplicate_rows: int,
    ) -> float:

        if total_rows == 0:
            return 100.0

        score = (
            (total_rows - duplicate_rows)
            / total_rows
        ) * 100

        return round(score, 2)

    # =====================================================
    # Validity
    # =====================================================

    def validity_score(
        self,
        profiles: list[ColumnProfile],
    ) -> float:

        if not profiles:
            return 100.0

        anomaly_columns = sum(
            1
            for profile in profiles
            if profile.anomaly.has_outliers
        )

        score = (
            (
                len(profiles)
                - anomaly_columns
            )
            / len(profiles)
        ) * 100

        return round(score, 2)

    # =====================================================
    # Consistency
    # =====================================================

    def consistency_score(
        self,
        profiles: list[ColumnProfile],
    ) -> float:

        if not profiles:
            return 100.0

        penalty = 0.0

        for profile in profiles:

            info = profile.statistics.constant_info

            if info is None:
                continue

            if info.is_constant:

                penalty += 1

            elif info.is_quasi_constant:

                penalty += 0.5

        score = (
            (
                len(profiles)
                - penalty
            )
            / len(profiles)
        ) * 100

        return round(
            max(score, 0),
            2,
        )

    # =====================================================
    # Overall
    # =====================================================

    def overall_score(
        self,
        completeness: float,
        uniqueness: float,
        validity: float,
        consistency: float,
    ) -> float:

        score = (

            completeness * self.completeness_weight

            +

            uniqueness * self.uniqueness_weight

            +

            validity * self.validity_weight

            +

            consistency * self.consistency_weight

        )

        return round(score, 2)

    # =====================================================
    # Grade
    # =====================================================

    def quality_grade(
        self,
        score: float,
    ) -> str:

        if score >= 95:
            return "A+"

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
    # Public API
    # =====================================================

    def calculate(
        self,
        *,
        total_rows: int,
        duplicate_rows: int,
        total_cells: int,
        missing_cells: int,
        column_profiles: list[ColumnProfile],
    ) -> QualityMetrics:

        completeness = self.completeness_score(
            total_cells,
            missing_cells,
        )

        uniqueness = self.uniqueness_score(
            total_rows,
            duplicate_rows,
        )

        validity = self.validity_score(
            column_profiles,
        )

        consistency = self.consistency_score(
            column_profiles,
        )

        overall = self.overall_score(
            completeness,
            uniqueness,
            validity,
            consistency,
        )

        return QualityMetrics(
            completeness_score=completeness,
            uniqueness_score=uniqueness,
            validity_score=validity,
            consistency_score=consistency,
            overall_score=overall,
        )

    # =====================================================
    # Dictionary Output
    # =====================================================

    def as_dict(
        self,
        metrics: QualityMetrics,
    ) -> dict:

        return {

            "completeness_score":
                metrics.completeness_score,

            "uniqueness_score":
                metrics.uniqueness_score,

            "validity_score":
                metrics.validity_score,

            "consistency_score":
                metrics.consistency_score,

            "overall_score":
                metrics.overall_score,

            "grade":
                self.quality_grade(
                    metrics.overall_score
                ),

        }
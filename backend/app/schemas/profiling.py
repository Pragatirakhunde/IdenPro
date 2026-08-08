from typing import Any

from pydantic import BaseModel, Field


# ==========================================================
# Dashboard Summary
# ==========================================================

class ProfilingDashboardResponse(BaseModel):
    total_tables: int = 0
    total_columns: int = 0
    total_rows: int = 0

    average_quality_score: float = 0.0

    pii_columns: int = 0
    anomaly_columns: int = 0

    duplicate_rows: int = 0
    missing_cells: int = 0


# ==========================================================
# Database Summary
# ==========================================================

class ProfilingDatabaseResponse(BaseModel):

    name: str

    tables: int
    rows: int
    columns: int

    quality: float


# ==========================================================
# Profiling Health
# ==========================================================

class ProfilingHealthResponse(BaseModel):

    status: str

    quality_score: float

    tables: int

    rows: int


# ==========================================================
# Profiling Run Response
# ==========================================================

class ProfilingRunResponse(BaseModel):

    success: bool

    generated_at: str

    summary: dict[str, Any]

    health: dict[str, Any]

    report: Any | None = None

    error: str | None = None
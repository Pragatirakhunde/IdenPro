from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User
from app.models.datasource import DataSource

from app.services.profiling_service import (
    ProfilingService,
)

from app.schemas.profiling import (
    ProfilingRunResponse,
)


router = APIRouter(
    prefix="/api/profiling",
    tags=["Profiling"],
)


# ==========================================================
# Health
# ==========================================================

@router.get("/health")
def profiling_health(
    current_user: User = Depends(
        get_current_user
    ),
):

    return {
        "status": "healthy",
        "service": "Dataset Profiling",
    }


# ==========================================================
# Run Profiling
# ==========================================================

@router.post(
    "/run/{datasource_id}",
    response_model=ProfilingRunResponse,
)
def run_profiling(
    datasource_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    # ------------------------------------------------------
    # Find datasource
    # ------------------------------------------------------

    datasource = (
        db.query(DataSource)
        .filter(
            DataSource.id == datasource_id
        )
        .first()
    )

    if not datasource:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data source not found.",
        )

    # ------------------------------------------------------
    # Run profiler
    # ------------------------------------------------------

    service = ProfilingService()

    result = service.safe_run(
        datasource
    )

    # ------------------------------------------------------
    # Handle profiling failure
    # ------------------------------------------------------

    if not result.get("success"):

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get(
                "error",
                "Dataset profiling failed.",
            ),
        )

    # ------------------------------------------------------
    # Return result
    # ------------------------------------------------------

    return result


# ==========================================================
# Summary
# ==========================================================

@router.get(
    "/summary/{datasource_id}"
)
def profiling_summary(
    datasource_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    datasource = (
        db.query(DataSource)
        .filter(
            DataSource.id == datasource_id
        )
        .first()
    )

    if not datasource:

        raise HTTPException(
            status_code=404,
            detail="Data source not found.",
        )

    service = ProfilingService()

    result = service.safe_run(
        datasource
    )

    if not result.get("success"):

        raise HTTPException(
            status_code=500,
            detail=result.get(
                "error",
                "Unable to generate profiling summary.",
            ),
        )

    return {
        "datasource_id": str(
            datasource_id
        ),
        "summary": result["summary"],
        "health": result["health"],
    }


# ==========================================================
# Full Report
# ==========================================================

@router.get(
    "/report/{datasource_id}"
)
def profiling_report(
    datasource_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    datasource = (
        db.query(DataSource)
        .filter(
            DataSource.id == datasource_id
        )
        .first()
    )

    if not datasource:

        raise HTTPException(
            status_code=404,
            detail="Data source not found.",
        )

    service = ProfilingService()

    result = service.safe_run(
        datasource
    )

    if not result.get("success"):

        raise HTTPException(
            status_code=500,
            detail=result.get(
                "error",
                "Unable to generate profiling report.",
            ),
        )

    return {
        "datasource_id": str(
            datasource_id
        ),
        "report": result["report"],
        "summary": result["summary"],
        "health": result["health"],
    }
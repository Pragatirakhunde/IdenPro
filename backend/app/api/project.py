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
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectList,
    ProjectCard,
)
from app.services.project_service import ProjectService

router = APIRouter(
    prefix="/api/projects",
    tags=["Projects"],
)


# ==========================================================
# Create Project
# ==========================================================

@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:
        return ProjectService.create_project(
            db=db,
            current_user=current_user,
            project_data=project,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ==========================================================
# Get All Projects
# ==========================================================

@router.get(
    "",
    response_model=ProjectList,
)
def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    projects = ProjectService.get_all_projects(
        db=db,
        current_user=current_user,
    )

    return {
        "total": len(projects),
        "projects": projects,
    }


# ==========================================================
# Get Single Project
# ==========================================================

@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:

        return ProjectService.get_project_by_id(
            db=db,
            current_user=current_user,
            project_id=project_id,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ==========================================================
# Update Project
# ==========================================================

@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
)
def update_project(
    project_id: UUID,
    project: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:

        return ProjectService.update_project(
            db=db,
            current_user=current_user,
            project_id=project_id,
            project_data=project,
        )

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ==========================================================
# Delete Project
# ==========================================================

@router.delete(
    "/{project_id}",
)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:

        ProjectService.delete_project(
            db=db,
            current_user=current_user,
            project_id=project_id,
        )

        return {
            "message": "Project deleted successfully."
        }

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
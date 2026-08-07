from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    UploadFile,
    HTTPException,
    status,
)

from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.auth.dependencies import get_current_user

from app.models.user import User

from app.schemas.datasource import (
    FileDataSourceCreate,
    DataSourceResponse,
    DataSourceList,
)

from app.schemas.db_connection import (
    DatabaseConnectionCreate,
)

from app.services.datasource_service import (
    DataSourceService,
)

router = APIRouter(
    prefix="/api/datasources",
    tags=["Data Sources"],
)


# ==========================================================
# Upload File
# ==========================================================

@router.post(
    "/upload",
    response_model=DataSourceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    project_id: UUID = Form(...),
    name: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:

        request = FileDataSourceCreate(
            project_id=project_id,
            name=name,
            description=description,
        )

        datasource = (
            DataSourceService.create_file_datasource(
                db=db,
                data=request,
                upload_file=file,
            )
        )

        return datasource

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ==========================================================
# Connect Database
# ==========================================================

@router.post(
    "/database",
    response_model=DataSourceResponse,
    status_code=status.HTTP_201_CREATED,
)
def connect_database(
    request: DatabaseConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:

        datasource = (
            DataSourceService.create_database_datasource(
                db=db,
                data=request,
            )
        )

        return datasource

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ==========================================================
# Get Project Data Sources
# ==========================================================

@router.get(
    "/project/{project_id}",
    response_model=DataSourceList,
)
def get_project_datasources(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    datasources = (
        DataSourceService.get_project_datasources(
            db=db,
            project_id=project_id,
        )
    )

    return {
        "total": len(datasources),
        "data_sources": datasources,
    }


# ==========================================================
# Delete Data Source
# ==========================================================

@router.delete(
    "/{datasource_id}",
)
def delete_datasource(
    datasource_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:

        DataSourceService.delete_datasource(
            db=db,
            datasource_id=datasource_id,
        )

        return {
            "message": "Data source deleted successfully."
        }

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
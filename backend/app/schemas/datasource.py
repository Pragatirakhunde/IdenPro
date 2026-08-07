from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ==========================================================
# Enums
# ==========================================================

class SourceType(str, Enum):
    FILE = "FILE"
    DATABASE = "DATABASE"


class DataSourceStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


# ==========================================================
# Create File DataSource
# ==========================================================

class FileDataSourceCreate(BaseModel):
    """
    Metadata required while uploading a file.

    Actual file is received separately through UploadFile.
    """

    project_id: UUID

    name: str = Field(
        ...,
        min_length=2,
        max_length=255
    )

    description: Optional[str] = Field(
        default=None,
        max_length=1000
    )


# ==========================================================
# Create Database DataSource
# ==========================================================

class DatabaseDataSourceCreate(BaseModel):
    """
    Metadata while creating a database connection.
    """

    project_id: UUID

    name: str = Field(
        ...,
        min_length=2,
        max_length=255
    )

    description: Optional[str] = Field(
        default=None,
        max_length=1000
    )


# ==========================================================
# Update DataSource
# ==========================================================

class DataSourceUpdate(BaseModel):

    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=255
    )

    description: Optional[str] = Field(
        default=None,
        max_length=1000
    )

    status: Optional[DataSourceStatus] = None


# ==========================================================
# Response
# ==========================================================

class DataSourceResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID

    project_id: UUID

    name: str

    description: Optional[str]

    source_type: SourceType

    source_format: str

    status: DataSourceStatus

    total_tables: int

    total_columns: int

    total_relationships: int

    created_at: datetime

    updated_at: datetime


# ==========================================================
# Dashboard Card
# ==========================================================

class DataSourceCard(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID

    name: str

    source_type: SourceType

    source_format: str

    status: DataSourceStatus


# ==========================================================
# List Response
# ==========================================================

class DataSourceList(BaseModel):

    total: int

    data_sources: list[DataSourceCard]


# ==========================================================
# Processing Status
# ==========================================================

class ProcessingStatusResponse(BaseModel):

    datasource_id: UUID

    status: DataSourceStatus

    message: str
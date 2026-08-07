from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


# ==========================================================
# Supported Database Types
# ==========================================================

class DatabaseType(str, Enum):
    POSTGRESQL = "POSTGRESQL"
    MYSQL = "MYSQL"
    SQLITE = "SQLITE"
    SQLSERVER = "SQLSERVER"
    ORACLE = "ORACLE"


# ==========================================================
# Create Database Connection
# ==========================================================

class DatabaseConnectionCreate(BaseModel):
    """
    Schema used while connecting a new database.
    """

    project_id: UUID

    connection_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Friendly name shown to the user"
    )

    db_type: DatabaseType

    host: str = Field(
        ...,
        max_length=255,
        description="Database host"
    )

    port: int = Field(
        ...,
        ge=1,
        le=65535
    )

    database_name: str = Field(
        ...,
        max_length=255
    )

    username: str = Field(
        ...,
        max_length=255
    )

    password: str = Field(
        ...,
        min_length=1
    )

    ssl_enabled: bool = False

    description: Optional[str] = Field(
        default=None,
        max_length=1000
    )

    @field_validator("host")
    @classmethod
    def validate_host(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Host cannot be empty.")

        return value


# ==========================================================
# Update Connection
# ==========================================================

class DatabaseConnectionUpdate(BaseModel):

    connection_name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    host: Optional[str] = None

    port: Optional[int] = Field(
        default=None,
        ge=1,
        le=65535
    )

    database_name: Optional[str] = None

    username: Optional[str] = None

    password: Optional[str] = None

    ssl_enabled: Optional[bool] = None

    description: Optional[str] = None


# ==========================================================
# Database Connection Response
# ==========================================================

class DatabaseConnectionResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID

    datasource_id: UUID

    connection_name: str

    db_type: DatabaseType

    host: str

    port: int

    database_name: str

    username: str

    ssl_enabled: bool

    is_active: bool

    last_synced: Optional[datetime]

    created_at: datetime

    updated_at: datetime


# ==========================================================
# Connection Test Response
# ==========================================================

class ConnectionTestResponse(BaseModel):

    success: bool

    message: str

    database_version: Optional[str] = None

    server_time: Optional[str] = None


# ==========================================================
# Database Information
# ==========================================================

class DatabaseInformation(BaseModel):

    database_name: str

    db_type: DatabaseType

    total_tables: int

    total_views: int

    total_columns: int

    total_relationships: int


# ==========================================================
# Sync Response
# ==========================================================

class SyncResponse(BaseModel):

    datasource_id: UUID

    synchronized: bool

    extracted_tables: int

    extracted_columns: int

    extracted_relationships: int

    message: str
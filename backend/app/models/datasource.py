import uuid
from enum import Enum

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    ForeignKey,
    Enum as SqlEnum,
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from app.database.base import Base


# ==========================================================
# Source Type
# ==========================================================

class SourceType(str, Enum):
    FILE = "FILE"
    DATABASE = "DATABASE"


# ==========================================================
# Processing Status
# ==========================================================

class DataSourceStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


# ==========================================================
# Data Source Model
# ==========================================================

class DataSource(Base):
    """
    Represents every source of data.

    Examples

    FILE
    -----
    CSV
    Excel
    JSON
    XML
    Parquet

    DATABASE
    --------
    PostgreSQL
    MySQL
    Oracle
    SQL Server
    SQLite
    """

    __tablename__ = "data_sources"

    # ------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ------------------------------------------------------
    # Parent Project
    # ------------------------------------------------------

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    # ------------------------------------------------------
    # Display Name
    # ------------------------------------------------------

    name = Column(
        String(255),
        nullable=False,
    )

    # ------------------------------------------------------
    # FILE or DATABASE
    # ------------------------------------------------------

    source_type = Column(
        SqlEnum(SourceType),
        nullable=False,
    )

    # ------------------------------------------------------
    # csv / xlsx / postgres / mysql
    # ------------------------------------------------------

    source_format = Column(
        String(50),
        nullable=False,
    )

    # ------------------------------------------------------
    # Current Processing Status
    # ------------------------------------------------------

    status = Column(
        SqlEnum(DataSourceStatus),
        default=DataSourceStatus.PENDING,
        nullable=False,
    )

    # ------------------------------------------------------
    # Optional Description
    # ------------------------------------------------------

    description = Column(
        String(1000),
        nullable=True,
    )

    # ------------------------------------------------------
    # Metadata Summary (filled later)
    # ------------------------------------------------------

    total_tables = Column(Integer, default=0, nullable=False)
    total_columns = Column(Integer, default=0, nullable=False)
    total_relationships = Column(Integer, default=0, nullable=False)

    # ------------------------------------------------------
    # Timestamps
    # ------------------------------------------------------

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ======================================================
    # Relationships
    # ======================================================

    project = relationship(
        "Project",
        back_populates="data_sources",
    )

    db_connection = relationship(
        "DatabaseConnection",
        back_populates="datasource",
        uselist=False,
        cascade="all, delete-orphan",
    )

    file_asset = relationship(
        "FileAsset",
        back_populates="datasource",
        uselist=False,
        cascade="all, delete-orphan",
    )
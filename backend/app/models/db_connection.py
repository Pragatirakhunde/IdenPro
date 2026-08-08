import uuid
from enum import Enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Enum as SqlEnum,
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


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
# Database Connection Model
# ==========================================================

class DatabaseConnection(Base):

    __tablename__ = "database_connections"

    # ======================================================
    # Primary Key
    # ======================================================

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ======================================================
    # Linked Data Source
    # ======================================================

    datasource_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "data_sources.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
    )

    # ======================================================
    # Database Type
    # ======================================================

    db_type = Column(
        SqlEnum(DatabaseType),
        nullable=False,
    )

    # ======================================================
    # Connection Details
    # ======================================================

    connection_name = Column(
        String(100),
        nullable=False,
    )

    host = Column(
        String(255),
        nullable=False,
    )

    port = Column(
        Integer,
        nullable=False,
    )

    database_name = Column(
        String(255),
        nullable=False,
    )

    username = Column(
        String(255),
        nullable=False,
    )

    # ======================================================
    # Password
    # ======================================================

    # Only encrypted password is stored.
    encrypted_password = Column(
        Text,
        nullable=False,
    )

    # ======================================================
    # Connection URI
    # ======================================================

    connection_uri = Column(
        Text,
        nullable=True,
    )

    # ======================================================
    # SSL
    # ======================================================

    ssl_enabled = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ======================================================
    # Status
    # ======================================================

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    last_synced = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ======================================================
    # Audit
    # ======================================================

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
    # Schema / Timeout
    # ======================================================

    schema_name = Column(
        String(100),
        default="public",
        nullable=False,
    )

    connection_timeout = Column(
        Integer,
        default=30,
        nullable=False,
    )

    # ======================================================
    # Relationship
    # ======================================================

    datasource = relationship(
        "DataSource",
        back_populates="db_connection",
    )
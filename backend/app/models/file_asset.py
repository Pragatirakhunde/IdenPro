import uuid

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    Text,
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class FileAsset(Base):
    """
    Stores metadata about uploaded files.

    Actual file is stored on disk or cloud storage.

    This table stores only metadata.
    """

    __tablename__ = "file_assets"

    # =====================================================
    # Primary Key
    # =====================================================

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # =====================================================
    # Linked Data Source
    # =====================================================

    datasource_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "data_sources.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
    )

    # =====================================================
    # Original File Information
    # =====================================================

    original_filename = Column(
        String(255),
        nullable=False,
    )

    stored_filename = Column(
        String(255),
        nullable=False,
        unique=True,
    )

    file_path = Column(
        Text,
        nullable=False,
    )

    # =====================================================
    # File Metadata
    # =====================================================

    file_extension = Column(
        String(20),
        nullable=False,
    )

    mime_type = Column(
        String(100),
        nullable=False,
    )

    file_size = Column(
        Integer,
        nullable=False,
    )

    # SHA256 hash
    checksum = Column(
        String(64),
        nullable=False,
        unique=True,
    )

    # =====================================================
    # Upload Information
    # =====================================================

    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # =====================================================
    # Relationship
    # =====================================================

    datasource = relationship(
        "DataSource",
        back_populates="file_asset",
    )
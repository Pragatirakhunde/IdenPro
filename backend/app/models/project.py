import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from app.database.base import Base


class Project(Base):
    """
    Represents a user project.

    Every uploaded file,
    connected database,
    documentation,
    report,
    knowledge graph,
    AI chat

    belongs to exactly one project.
    """

    __tablename__ = "projects"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    name = Column(
        String(100),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    status = Column(
        String(20),
        default="ACTIVE",
        nullable=False
    )

    last_accessed = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # -------------------------
    # Relationships
    # -------------------------

    owner = relationship(
        "User",
        back_populates="projects"
    )

    data_sources = relationship(
        "DataSource",
        back_populates="project",
        cascade="all, delete-orphan"
    )
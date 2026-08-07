from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# =====================================================
# Create Project
# =====================================================

class ProjectCreate(BaseModel):
    """
    Schema used while creating a project.
    """

    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Project Name"
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Project Description"
    )


# =====================================================
# Update Project
# =====================================================

class ProjectUpdate(BaseModel):
    """
    Schema used while updating a project.
    """

    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=100
    )

    description: str | None = Field(
        default=None,
        max_length=1000
    )


# =====================================================
# Project Response
# =====================================================

class ProjectResponse(BaseModel):
    """
    Returned to frontend.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID

    user_id: UUID

    name: str

    description: str | None

    created_at: datetime

    updated_at: datetime


# =====================================================
# Dashboard Project Card
# =====================================================

class ProjectCard(BaseModel):
    """
    Lightweight project representation.
    Used on dashboard cards.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID

    name: str

    description: str | None

    created_at: datetime


# =====================================================
# Project List
# =====================================================

class ProjectList(BaseModel):
    """
    Response for listing projects.
    """

    total: int

    projects: list[ProjectCard]
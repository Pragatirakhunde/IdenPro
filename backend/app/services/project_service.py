from uuid import UUID

from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
)


class ProjectService:
    """
    Business logic for Project Management.
    """

    # ==========================================================
    # Create Project
    # ==========================================================
    @staticmethod
    def create_project(
        db: Session,
        current_user: User,
        project_data: ProjectCreate,
    ) -> Project:

        # Check duplicate project name for this user
        existing_project = (
            db.query(Project)
            .filter(
                Project.user_id == current_user.id,
                Project.name == project_data.name,
            )
            .first()
        )

        if existing_project:
            raise ValueError(
                "Project with this name already exists."
            )

        new_project = Project(
            user_id=current_user.id,
            name=project_data.name,
            description=project_data.description,
        )

        db.add(new_project)

        db.commit()

        db.refresh(new_project)

        return new_project

    # ==========================================================
    # Get All Projects
    # ==========================================================
    @staticmethod
    def get_all_projects(
        db: Session,
        current_user: User,
    ) -> list[Project]:

        return (
            db.query(Project)
            .filter(
                Project.user_id == current_user.id
            )
            .order_by(Project.created_at.desc())
            .all()
        )

    # ==========================================================
    # Get Single Project
    # ==========================================================
    @staticmethod
    def get_project_by_id(
        db: Session,
        current_user: User,
        project_id: UUID,
    ) -> Project:

        project = (
            db.query(Project)
            .filter(
                Project.id == project_id,
                Project.user_id == current_user.id,
            )
            .first()
        )

        if project is None:
            raise ValueError("Project not found.")

        return project

    # ==========================================================
    # Update Project
    # ==========================================================
    @staticmethod
    def update_project(
        db: Session,
        current_user: User,
        project_id: UUID,
        project_data: ProjectUpdate,
    ) -> Project:

        project = ProjectService.get_project_by_id(
            db,
            current_user,
            project_id,
        )

        # Prevent duplicate names
        if (
            project_data.name
            and project_data.name != project.name
        ):

            duplicate = (
                db.query(Project)
                .filter(
                    Project.user_id == current_user.id,
                    Project.name == project_data.name,
                    Project.id != project.id,
                )
                .first()
            )

            if duplicate:
                raise ValueError(
                    "Project name already exists."
                )

            project.name = project_data.name

        if project_data.description is not None:
            project.description = project_data.description

        db.commit()

        db.refresh(project)

        return project

    # ==========================================================
    # Delete Project
    # ==========================================================
    @staticmethod
    def delete_project(
        db: Session,
        current_user: User,
        project_id: UUID,
    ) -> None:

        project = ProjectService.get_project_by_id(
            db,
            current_user,
            project_id,
        )

        db.delete(project)

        db.commit()
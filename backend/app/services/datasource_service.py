from pathlib import Path
from uuid import UUID
import hashlib
import secrets
import shutil

from cryptography.fernet import Fernet
from sqlalchemy.orm import Session

from app.config import settings

from app.models.project import Project
from app.models.datasource import (
    DataSource,
    SourceType,
    DataSourceStatus,
)
from app.models.file_asset import FileAsset
from app.models.db_connection import (
    DatabaseConnection,
)

from app.schemas.datasource import (
    FileDataSourceCreate,
)

from app.schemas.db_connection import (
    DatabaseConnectionCreate,
)

from app.services.database_connector import DatabaseConnector


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


class DataSourceService:

    # =====================================================
    # Encryption
    # =====================================================

    @staticmethod
    def encrypt_password(password: str) -> str:

        fernet = Fernet(settings.ENCRYPTION_KEY.encode())

        return fernet.encrypt(
            password.encode()
        ).decode()

    # =====================================================
    # SHA256
    # =====================================================

    @staticmethod
    def calculate_checksum(path: Path):

        sha = hashlib.sha256()

        with open(path, "rb") as f:

            while chunk := f.read(8192):
                sha.update(chunk)

        return sha.hexdigest()

    # =====================================================
    # Save Uploaded File
    # =====================================================

    @staticmethod
    def save_uploaded_file(upload_file):

        extension = Path(upload_file.filename).suffix

        stored_name = (
            secrets.token_hex(16)
            + extension
        )

        destination = (
            UPLOAD_DIR / stored_name
        )

        with destination.open("wb") as buffer:
            shutil.copyfileobj(
                upload_file.file,
                buffer,
            )

        checksum = (
            DataSourceService.calculate_checksum(
                destination
            )
        )

        return {
            "stored_name": stored_name,
            "path": str(destination),
            "checksum": checksum,
            "size": destination.stat().st_size,
        }

    # =====================================================
    # Create File DataSource
    # =====================================================

    @staticmethod
    def create_file_datasource(
        db: Session,
        data: FileDataSourceCreate,
        upload_file,
    ):

        project = db.get(
            Project,
            data.project_id,
        )

        if project is None:
            raise ValueError(
                "Project not found."
            )

        file_info = (
            DataSourceService.save_uploaded_file(
                upload_file
            )
        )

        datasource = DataSource(

            project_id=data.project_id,

            name=data.name,

            description=data.description,

            source_type=SourceType.FILE,

            source_format=Path(
                upload_file.filename
            ).suffix.replace(".", ""),

            status=DataSourceStatus.PENDING,
        )

        db.add(datasource)

        db.flush()

        asset = FileAsset(

            datasource_id=datasource.id,

            original_filename=upload_file.filename,

            stored_filename=file_info[
                "stored_name"
            ],

            file_path=file_info[
                "path"
            ],

            file_extension=Path(
                upload_file.filename
            ).suffix,

            mime_type=upload_file.content_type,

            file_size=file_info["size"],

            checksum=file_info[
                "checksum"
            ],
        )

        db.add(asset)

        db.commit()

        db.refresh(datasource)

        return datasource

    # =====================================================
    # Create Database DataSource
    # =====================================================

    @staticmethod
    def create_database_datasource(
        db: Session,
        data: DatabaseConnectionCreate,
    ):

        project = db.get(
            Project,
            data.project_id,
        )

        if project is None:
            raise ValueError(
                "Project not found."
            )

        url = DatabaseConnector.build_connection_url(

            db_type=data.db_type,

            username=data.username,

            password=data.password,

            host=data.host,

            port=data.port,

            database_name=data.database_name,
        )

        engine = (
            DatabaseConnector.create_engine_instance(
                url
            )
        )

        success, message = (
            DatabaseConnector.test_connection(
                engine
            )
        )

        if not success:

            raise ValueError(message)

        datasource = DataSource(

            project_id=data.project_id,

            name=data.connection_name,

            description=data.description,

            source_type=SourceType.DATABASE,

            source_format=data.db_type.value.lower(),

            status=DataSourceStatus.READY,
        )

        db.add(datasource)

        db.flush()

        encrypted = (
            DataSourceService.encrypt_password(
                data.password
            )
        )

        connection = DatabaseConnection(

            datasource_id=datasource.id,

            connection_name=data.connection_name,

            db_type=data.db_type,

            host=data.host,

            port=data.port,

            database_name=data.database_name,

            username=data.username,

            encrypted_password=encrypted,

            connection_uri=url.replace(
                data.password,
                "******",
            ),

            ssl_enabled=data.ssl_enabled,
        )

        db.add(connection)

        db.commit()

        db.refresh(datasource)

        DatabaseConnector.close_engine(
            engine
        )

        return datasource

    # =====================================================
    # List Project Data Sources
    # =====================================================

    @staticmethod
    def get_project_datasources(
        db: Session,
        project_id: UUID,
    ):

        return (
            db.query(DataSource)
            .filter(
                DataSource.project_id == project_id
            )
            .order_by(
                DataSource.created_at.desc()
            )
            .all()
        )

    # =====================================================
    # Delete
    # =====================================================

    @staticmethod
    def delete_datasource(
        db: Session,
        datasource_id: UUID,
    ):

        datasource = db.get(
            DataSource,
            datasource_id,
        )

        if datasource is None:

            raise ValueError(
                "Datasource not found."
            )

        db.delete(datasource)

        db.commit()
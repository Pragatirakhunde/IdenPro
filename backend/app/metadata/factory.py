from app.metadata.files.csv_extractor import CSVExtractor
from app.metadata.files.excel_extractor import ExcelExtractor
from app.metadata.files.json_extractor import JSONExtractor
from app.metadata.files.xml_extractor import XMLExtractor
from app.metadata.files.parquet_extractor import ParquetExtractor

from app.metadata.database.postgres_extractor import PostgresExtractor
from app.metadata.database.mysql_extractor import MySQLExtractor
from app.metadata.database.sqlite_extractor import SQLiteExtractor
from app.metadata.database.sqlserver_extractor import SQLServerExtractor
from app.metadata.database.oracle_extractor import OracleExtractor

from app.models.datasource import SourceType
from app.models.db_connection import DatabaseType


class MetadataExtractorFactory:
    """
    Factory responsible for returning the correct metadata
    extractor based on datasource type and format.
    """

    @staticmethod
    def create(datasource):
        """
        Create and return the appropriate extractor
        for the given DataSource.
        """

        # ==================================================
        # FILE SOURCES
        # ==================================================

        if datasource.source_type == SourceType.FILE:

            if not datasource.source_format:
                raise ValueError(
                    "File source format is missing."
                )

            if not datasource.file_asset:
                raise ValueError(
                    "File asset is missing for this datasource."
                )

            extension = (
                datasource.source_format
                .lower()
                .strip()
                .lstrip(".")
            )

            file_path = datasource.file_asset.file_path

            if not file_path:
                raise ValueError(
                    "File path is missing."
                )

            if extension == "csv":
                return CSVExtractor(file_path)

            elif extension in ("xlsx", "xls"):
                return ExcelExtractor(file_path)

            elif extension == "json":
                return JSONExtractor(file_path)

            elif extension == "xml":
                return XMLExtractor(file_path)

            elif extension == "parquet":
                return ParquetExtractor(file_path)

            raise ValueError(
                f"Unsupported file format: {extension}"
            )

        # ==================================================
        # DATABASE SOURCES
        # ==================================================

        if datasource.source_type == SourceType.DATABASE:

            if not datasource.db_connection:
                raise ValueError(
                    "Database connection is missing."
                )

            db = datasource.db_connection

            if db.db_type == DatabaseType.POSTGRESQL:
                return PostgresExtractor(db)

            elif db.db_type == DatabaseType.MYSQL:
                return MySQLExtractor(db)

            elif db.db_type == DatabaseType.SQLITE:
                return SQLiteExtractor(db)

            elif db.db_type == DatabaseType.SQLSERVER:
                return SQLServerExtractor(db)

            elif db.db_type == DatabaseType.ORACLE:
                return OracleExtractor(db)

            raise ValueError(
                f"Unsupported database type: {db.db_type}"
            )

        # ==================================================
        # INVALID SOURCE
        # ==================================================

        raise ValueError(
            f"Invalid datasource type: "
            f"{datasource.source_type}"
        )
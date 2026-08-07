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
    Factory responsible for returning the correct metadata extractor
    based on datasource type and format.
    """

    @staticmethod
    def create(datasource):
        """
        Parameters
        ----------
        datasource : DataSource ORM object

        Returns
        -------
        BaseExtractor subclass
        """

        # -------------------------------------------------
        # FILE SOURCES
        # -------------------------------------------------

        if datasource.source_type == SourceType.FILE:

            extension = datasource.source_format.lower()

            file_path = datasource.file_asset.file_path

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

        # -------------------------------------------------
        # DATABASE SOURCES
        # -------------------------------------------------

        if datasource.source_type == SourceType.DATABASE:

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
                f"Unsupported database: {db.db_type}"
            )

        raise ValueError("Invalid datasource type.")
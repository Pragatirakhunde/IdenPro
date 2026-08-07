from urllib.parse import quote_plus

from app.metadata.database.base_database_extractor import (
    BaseDatabaseExtractor,
)


class SQLServerExtractor(BaseDatabaseExtractor):
    """
    Metadata extractor for Microsoft SQL Server.

    Uses SQLAlchemy + pyodbc.

    Inherits:
        - Table extraction
        - Column extraction
        - PK/FK discovery
        - Index discovery
        - View discovery
        - Relationship discovery
    """

    DRIVER = "mssql+pyodbc"

    def build_connection_url(self) -> str:

        db = self.db_connection

        username = quote_plus(
            db.username
        )

        password = quote_plus(
            db.password
        )

        connection_string = quote_plus(
            (
                "DRIVER={ODBC Driver 18 for SQL Server};"
                f"SERVER={db.host},{db.port};"
                f"DATABASE={db.database_name};"
                f"UID={db.username};"
                f"PWD={db.password};"
                "TrustServerCertificate=yes;"
            )
        )

        return (
            f"{self.DRIVER}://"
            f"{username}:{password}"
            f"@"
            f"{db.host}:{db.port}"
            "/"
            f"{db.database_name}"
            f"?odbc_connect={connection_string}"
        )
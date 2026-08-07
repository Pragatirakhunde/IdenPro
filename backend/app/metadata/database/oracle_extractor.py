from urllib.parse import quote_plus

from app.metadata.database.base_database_extractor import (
    BaseDatabaseExtractor,
)


class OracleExtractor(BaseDatabaseExtractor):
    """
    Metadata extractor for Oracle Database.

    Uses:
        SQLAlchemy + python-oracledb

    Supports:
        - Tables
        - Columns
        - Primary Keys
        - Foreign Keys
        - Indexes
        - Views
        - Relationships
    """

    DRIVER = "oracle+oracledb"

    def build_connection_url(self) -> str:

        db = self.db_connection

        username = quote_plus(
            db.username
        )

        password = quote_plus(
            db.password
        )

        return (
            f"{self.DRIVER}://"
            f"{username}:{password}"
            "@"
            f"{db.host}:{db.port}"
            "/"
            f"{db.database_name}"
        )
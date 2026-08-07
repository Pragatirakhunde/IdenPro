from urllib.parse import quote_plus

from app.metadata.database.base_database_extractor import (
    BaseDatabaseExtractor,
)


class MySQLExtractor(BaseDatabaseExtractor):
    """
    Metadata extractor for MySQL.

    All metadata extraction is handled by
    BaseDatabaseExtractor.
    """

    DRIVER = "mysql+pymysql"

    def build_connection_url(self) -> str:

        db = self.db_connection

        username = quote_plus(db.username)
        password = quote_plus(db.password)

        return (
            f"{self.DRIVER}://"
            f"{username}:{password}"
            f"@{db.host}:{db.port}"
            f"/{db.database_name}"
            "?charset=utf8mb4"
        )
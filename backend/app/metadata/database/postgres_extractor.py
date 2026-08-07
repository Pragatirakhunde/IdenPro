from urllib.parse import quote_plus

from app.metadata.database.base_database_extractor import (
    BaseDatabaseExtractor,
)


class PostgresExtractor(BaseDatabaseExtractor):
    """
    PostgreSQL metadata extractor.

    Inherits all metadata extraction logic from
    BaseDatabaseExtractor.

    Only responsible for building the connection URL.
    """

    DRIVER = "postgresql+psycopg2"

    def build_connection_url(self) -> str:

        db = self.db_connection

        username = quote_plus(db.username)
        password = quote_plus(db.password)

        return (
            f"{self.DRIVER}://"
            f"{username}:{password}"
            f"@{db.host}:{db.port}"
            f"/{db.database_name}"
        )
from pathlib import Path

from app.metadata.database.base_database_extractor import (
    BaseDatabaseExtractor,
)


class SQLiteExtractor(BaseDatabaseExtractor):
    """
    Metadata extractor for SQLite databases.

    Supports:
        - .db
        - .sqlite
        - .sqlite3

    Uses SQLAlchemy SQLite dialect.
    """

    DRIVER = "sqlite"

    def build_connection_url(self) -> str:

        db = self.db_connection

        database_path = Path(
            db.database_name
        ).resolve()

        return (
            f"{self.DRIVER}:///"
            f"{database_path}"
        )
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.db_connection import DatabaseType


class DatabaseConnector:

    @staticmethod
    def build_connection_url(
        db_type: DatabaseType,
        username: str,
        password: str,
        host: str,
        port: int,
        database_name: str,
    ) -> str:

        if db_type == DatabaseType.POSTGRESQL:

            return (
                f"postgresql+psycopg2://"
                f"{username}:{password}"
                f"@{host}:{port}/{database_name}"
            )

        elif db_type == DatabaseType.MYSQL:

            return (
                f"mysql+pymysql://"
                f"{username}:{password}"
                f"@{host}:{port}/{database_name}"
            )

        elif db_type == DatabaseType.SQLITE:

            return f"sqlite:///{database_name}"

        elif db_type == DatabaseType.SQLSERVER:

            return (
                f"mssql+pyodbc://"
                f"{username}:{password}"
                f"@{host}:{port}/{database_name}"
                "?driver=ODBC+Driver+17+for+SQL+Server"
            )

        elif db_type == DatabaseType.ORACLE:

            return (
                f"oracle+oracledb://"
                f"{username}:{password}"
                f"@{host}:{port}/?service_name={database_name}"
            )

        raise ValueError("Unsupported database type.")

    # ------------------------------------------------------

    @staticmethod
    def create_engine_instance(connection_url: str):

        return create_engine(
            connection_url,
            pool_pre_ping=True,
            future=True,
        )

    # ------------------------------------------------------

    @staticmethod
    def test_connection(engine):

        try:

            with engine.connect() as connection:

                connection.execute(
                    text("SELECT 1")
                )

            return True, "Connection Successful"

        except SQLAlchemyError as e:

            return False, str(e)

    # ------------------------------------------------------

    @staticmethod
    def get_database_version(engine):

        queries = [

            "SELECT version()",

            "SELECT @@VERSION",

            "SELECT sqlite_version()",

        ]

        try:

            with engine.connect() as connection:

                for query in queries:

                    try:

                        version = connection.execute(
                            text(query)
                        ).scalar()

                        if version:

                            return str(version)

                    except Exception:
                        continue

            return "Unknown"

        except Exception:

            return "Unknown"

    # ------------------------------------------------------

    @staticmethod
    def close_engine(engine):

        if engine:

            engine.dispose()
from __future__ import annotations

from abc import abstractmethod
from typing import List

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.metadata.base_extractor import BaseExtractor
from app.metadata.models import (
    ColumnMetadata,
    ForeignKeyMetadata,
    IndexMetadata,
    MetadataResult,
    MetadataSummary,
    RelationshipMetadata,
    TableMetadata,
    ViewMetadata,
)


class BaseDatabaseExtractor(BaseExtractor):
    """
    Base extractor for all relational databases.

    Child classes only provide:
        - build_connection_url()

    Everything else is shared.

    Supported:
        PostgreSQL
        MySQL
        SQLite
        SQL Server
        Oracle
    """

    def __init__(self, db_connection):

        super().__init__(db_connection)

        self.db_connection = db_connection

        self.engine: Engine | None = None

        self.inspector = None

    # ==========================================================
    # Child must implement
    # ==========================================================

    @abstractmethod
    def build_connection_url(self) -> str:
        """
        Return SQLAlchemy connection string.
        """
        pass

    # ==========================================================
    # Connect
    # ==========================================================

    def connect(self):

        if self.engine is not None:
            return self.engine

        url = self.build_connection_url()

        self.engine = create_engine(
            url,
            pool_pre_ping=True,
        )

        self.inspector = inspect(self.engine)

        return self.engine

    # ==========================================================
    # Tables
    # ==========================================================

    def extract_tables(self) -> List[TableMetadata]:

        self.connect()

        tables = []

        for table in self.inspector.get_table_names():

            tables.append(

                TableMetadata(

                    name=table,

                    row_count=self.get_row_count(table),

                )

            )

        return tables

    # ==========================================================
    # Columns
    # ==========================================================

    def extract_columns(
        self,
        table_name: str,
    ) -> List[ColumnMetadata]:

        self.connect()

        columns = []

        pk_columns = set(
            self.extract_primary_keys(table_name)
        )

        fk_columns = {

            fk.column_name

            for fk in self.extract_foreign_keys(table_name)

        }

        for column in self.inspector.get_columns(
            table_name
        ):

            columns.append(

                ColumnMetadata(

                    name=column["name"],

                    data_type=str(column["type"]),

                    nullable=column.get(
                        "nullable",
                        True,
                    ),

                    primary_key=column["name"] in pk_columns,

                    foreign_key=column["name"] in fk_columns,

                    unique=False,

                    default_value=(
                        str(column["default"])
                        if column.get("default")
                        else None
                    ),

                    comment=column.get("comment"),

                )

            )

        return columns

    # ==========================================================
    # Primary Keys
    # ==========================================================

    def extract_primary_keys(
        self,
        table_name: str,
    ) -> List[str]:

        self.connect()

        pk = self.inspector.get_pk_constraint(
            table_name
        )

        return pk.get(
            "constrained_columns",
            [],
        )

    # ==========================================================
    # Foreign Keys
    # ==========================================================

    def extract_foreign_keys(
        self,
        table_name: str,
    ) -> List[ForeignKeyMetadata]:

        self.connect()

        relationships = []

        foreign_keys = self.inspector.get_foreign_keys(
            table_name
        )

        for fk in foreign_keys:

            constrained = fk.get(
                "constrained_columns",
                []
            )

            referred = fk.get(
                "referred_columns",
                []
            )

            if not constrained or not referred:
                continue

            relationships.append(

                ForeignKeyMetadata(

                    column_name=constrained[0],

                    referenced_table=fk.get(
                        "referred_table"
                    ),

                    referenced_column=referred[0],

                    constraint_name=fk.get("name"),

                )

            )

        return relationships

    # ==========================================================
    # Indexes
    # ==========================================================

    def extract_indexes(
        self,
        table_name: str,
    ) -> List[IndexMetadata]:

        self.connect()

        indexes = []

        for index in self.inspector.get_indexes(
            table_name
        ):

            indexes.append(

                IndexMetadata(

                    name=index["name"],

                    columns=index.get(
                        "column_names",
                        [],
                    ),

                    unique=index.get(
                        "unique",
                        False,
                    ),

                )

            )

        return indexes

    # ==========================================================
    # Views
    # ==========================================================

    def extract_views(self) -> List[ViewMetadata]:

        self.connect()

        views = []

        for view in self.inspector.get_view_names():

            definition = None

            try:

                definition = self.inspector.get_view_definition(
                    view
                )

            except Exception:
                pass

            views.append(

                ViewMetadata(

                    name=view,

                    definition=definition,

                )

            )

        return views

    # ==========================================================
    # Row Count
    # ==========================================================

    def get_row_count(
        self,
        table_name: str,
    ) -> int:

        self.connect()

        try:

            with self.engine.connect() as conn:

                result = conn.execute(
                    text(f'SELECT COUNT(*) FROM "{table_name}"')
                )

                return int(result.scalar())

        except Exception:

            return 0

    # ==========================================================
    # Sample Data
    # ==========================================================

    def get_sample_data(
        self,
        table_name: str,
        limit: int = 5,
    ):

        self.connect()

        with self.engine.connect() as conn:

            result = conn.execute(

                text(

                    f'SELECT * FROM "{table_name}" LIMIT {limit}'

                )

            )

            return [

                dict(row._mapping)

                for row in result

            ]

    # ==========================================================
    # Complete Metadata
    # ==========================================================

    def extract_metadata(self) -> MetadataResult:

        self.connect()

        tables = self.extract_tables()

        relationships = []

        total_columns = 0
        total_pk = 0
        total_fk = 0
        total_indexes = 0

        for table in tables:

            table.columns = self.extract_columns(
                table.name
            )

            table.primary_keys = self.extract_primary_keys(
                table.name
            )

            table.foreign_keys = self.extract_foreign_keys(
                table.name
            )

            table.indexes = self.extract_indexes(
                table.name
            )

            total_columns += len(table.columns)
            total_pk += len(table.primary_keys)
            total_fk += len(table.foreign_keys)
            total_indexes += len(table.indexes)

            for fk in table.foreign_keys:

                relationships.append(

                    RelationshipMetadata(

                        source_table=table.name,

                        source_column=fk.column_name,

                        target_table=fk.referenced_table,

                        target_column=fk.referenced_column,

                        relationship_type="FOREIGN_KEY",

                        confidence_score=1.0,

                        discovered_by="database_constraint",

                    )

                )

        summary = MetadataSummary(

            total_tables=len(tables),

            total_views=len(self.extract_views()),

            total_columns=total_columns,

            total_primary_keys=total_pk,

            total_foreign_keys=total_fk,

            total_indexes=total_indexes,

            total_relationships=len(relationships),

        )

        return MetadataResult(

            tables=tables,

            relationships=relationships,

            views=self.extract_views(),

            summary=summary,

        )

    # ==========================================================
    # Connection Test
    # ==========================================================

    def test_connection(self) -> bool:

        try:

            self.connect()

            with self.engine.connect() as conn:

                conn.execute(text("SELECT 1"))

            return True

        except SQLAlchemyError:

            return False

    # ==========================================================
    # Database Information
    # ==========================================================

    def database_information(self):

        self.connect()

        return {

            "database": self.db_connection.database_name,

            "host": self.db_connection.host,

            "port": self.db_connection.port,

            "dialect": self.engine.dialect.name,

            "driver": self.engine.dialect.driver,

        }

    # ==========================================================
    # Close
    # ==========================================================

    def close(self):

        if self.engine:

            self.engine.dispose()

        self.engine = None

        self.inspector = None

    def extract_relationships(self):
        raise NotImplementedError
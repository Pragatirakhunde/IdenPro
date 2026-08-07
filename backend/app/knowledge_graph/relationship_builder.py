from __future__ import annotations

from app.knowledge_graph.models import (
    GraphEdge,
    RelationType,
)
from app.profiling.models import DatabaseProfile


class RelationshipBuilder:
    """
    Builds relationships between graph entities.

    Database
        │
        ├──HAS_TABLE────► Table
        │
        └───────────────┐
                        ▼
                     Columns
                        │
         ├──HAS_DATA_TYPE──► DataType
         ├──HAS_PATTERN────► Pattern
         └──HAS_PII────────► PII
    """

    # =====================================================
    # Database -> Table
    # =====================================================

    def _database_table_edges(
        self,
        profile: DatabaseProfile,
    ) -> list[GraphEdge]:

        database_id = (
            f"db:{profile.statistics.database_name}"
        )

        edges = []

        for table in profile.tables:

            edges.append(

                GraphEdge(

                    source=database_id,

                    target=f"table:{table.statistics.table_name}",

                    relationship=RelationType.HAS_TABLE,

                )

            )

        return edges

    # =====================================================
    # Table -> Column
    # =====================================================

    def _table_column_edges(
        self,
        profile: DatabaseProfile,
    ) -> list[GraphEdge]:

        edges = []

        for table in profile.tables:

            table_id = (
                f"table:{table.statistics.table_name}"
            )

            for column in table.columns:

                edges.append(

                    GraphEdge(

                        source=table_id,

                        target=f"{table.statistics.table_name}.{column.statistics.column_name}",

                        relationship=RelationType.HAS_COLUMN,

                    )

                )

        return edges

    # =====================================================
    # Column -> Data Type
    # =====================================================

    def _datatype_edges(
        self,
        profile: DatabaseProfile,
    ) -> list[GraphEdge]:

        edges = []

        for table in profile.tables:

            for column in table.columns:

                edges.append(

                    GraphEdge(

                        source=f"{table.statistics.table_name}.{column.statistics.column_name}",

                        target=f"dtype:{column.statistics.data_type}",

                        relationship=RelationType.HAS_DATA_TYPE,

                    )

                )

        return edges

    # =====================================================
    # Column -> Pattern
    # =====================================================

    def _pattern_edges(
        self,
        profile: DatabaseProfile,
    ) -> list[GraphEdge]:

        edges = []

        for table in profile.tables:

            for column in table.columns:

                pattern = (
                    column.pattern.detected_pattern
                )

                if not pattern:
                    continue

                edges.append(

                    GraphEdge(

                        source=f"{table.statistics.table_name}.{column.statistics.column_name}",

                        target=f"pattern:{pattern}",

                        relationship=RelationType.HAS_PATTERN,

                    )

                )

        return edges

    # =====================================================
    # Column -> PII
    # =====================================================

    def _pii_edges(
        self,
        profile: DatabaseProfile,
    ) -> list[GraphEdge]:

        edges = []

        for table in profile.tables:

            for column in table.columns:

                if not column.pii.contains_pii:
                    continue

                edges.append(

                    GraphEdge(

                        source=f"{table.statistics.table_name}.{column.statistics.column_name}",

                        target=f"pii:{column.pii.pii_type}",

                        relationship=RelationType.HAS_PII,

                    )

                )

        return edges

    # =====================================================
    # Public API
    # =====================================================

    def build(
        self,
        profile: DatabaseProfile,
    ) -> list[GraphEdge]:

        edges = []

        edges.extend(
            self._database_table_edges(
                profile
            )
        )

        edges.extend(
            self._table_column_edges(
                profile
            )
        )

        edges.extend(
            self._datatype_edges(
                profile
            )
        )

        edges.extend(
            self._pattern_edges(
                profile
            )
        )

        edges.extend(
            self._pii_edges(
                profile
            )
        )

        return edges
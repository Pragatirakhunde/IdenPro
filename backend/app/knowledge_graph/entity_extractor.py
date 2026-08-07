from __future__ import annotations

from app.knowledge_graph.models import (
    GraphNode,
    NodeType,
)
from app.profiling.models import DatabaseProfile


class EntityExtractor:
    """
    Converts profiling objects into graph nodes.

    DatabaseProfile
            │
            ▼
        Database Node
            │
            ▼
        Table Nodes
            │
            ▼
        Column Nodes
            │
            ▼
    Pattern / PII / Quality Nodes
    """

    # =====================================================
    # Database
    # =====================================================

    def _database_node(
        self,
        profile: DatabaseProfile,
    ) -> GraphNode:

        return GraphNode(

            id=f"db:{profile.statistics.database_name}",

            label=profile.statistics.database_name,

            node_type=NodeType.DATABASE,

            properties={

                "tables":
                    profile.statistics.total_tables,

                "rows":
                    profile.statistics.total_rows,

                "columns":
                    profile.statistics.total_columns,

                "quality":
                    profile.quality.overall_score,

            },

        )

    # =====================================================
    # Tables
    # =====================================================

    def _table_nodes(
        self,
        profile: DatabaseProfile,
    ) -> list[GraphNode]:

        nodes = []

        for table in profile.tables:

            nodes.append(

                GraphNode(

                    id=f"table:{table.statistics.table_name}",

                    label=table.statistics.table_name,

                    node_type=NodeType.TABLE,

                    properties={

                        "rows":
                            table.statistics.total_rows,

                        "columns":
                            table.statistics.total_columns,

                        "quality":
                            table.quality.overall_score,

                        "duplicates":
                            table.statistics.duplicate_rows,

                        "missing":
                            table.statistics.missing_cells,

                    },

                )

            )

        return nodes

    # =====================================================
    # Columns
    # =====================================================

    def _column_nodes(
        self,
        profile: DatabaseProfile,
    ) -> list[GraphNode]:

        nodes = []

        for table in profile.tables:

            for column in table.columns:

                nodes.append(

                    GraphNode(

                        id=f"{table.statistics.table_name}.{column.statistics.column_name}",

                        label=column.statistics.column_name,

                        node_type=NodeType.COLUMN,

                        properties={

                            "datatype":
                                column.statistics.data_type,

                            "unique":
                                column.statistics.unique_count,

                            "nulls":
                                column.statistics.null_count,

                            "duplicates":
                                column.statistics.duplicate_count,

                        },

                    )

                )

        return nodes

    # =====================================================
    # Data Type Nodes
    # =====================================================

    def _datatype_nodes(
        self,
        profile: DatabaseProfile,
    ) -> list[GraphNode]:

        nodes = {}

        for table in profile.tables:

            for column in table.columns:

                dtype = column.statistics.data_type

                if dtype not in nodes:

                    nodes[dtype] = GraphNode(

                        id=f"dtype:{dtype}",

                        label=dtype,

                        node_type=NodeType.DATA_TYPE,

                        properties={},

                    )

        return list(nodes.values())

    # =====================================================
    # Pattern Nodes
    # =====================================================

    def _pattern_nodes(
        self,
        profile: DatabaseProfile,
    ) -> list[GraphNode]:

        nodes = {}

        for table in profile.tables:

            for column in table.columns:

                pattern = column.pattern.detected_pattern

                if not pattern:
                    continue

                if pattern not in nodes:

                    nodes[pattern] = GraphNode(

                        id=f"pattern:{pattern}",

                        label=pattern,

                        node_type=NodeType.PATTERN,

                        properties={},

                    )

        return list(nodes.values())

    # =====================================================
    # PII Nodes
    # =====================================================

    def _pii_nodes(
        self,
        profile: DatabaseProfile,
    ) -> list[GraphNode]:

        nodes = {}

        for table in profile.tables:

            for column in table.columns:

                if not column.pii.contains_pii:
                    continue

                pii_type = column.pii.pii_type

                if pii_type not in nodes:

                    nodes[pii_type] = GraphNode(

                        id=f"pii:{pii_type}",

                        label=pii_type,

                        node_type=NodeType.PII,

                        properties={},

                    )

        return list(nodes.values())

    # =====================================================
    # Public API
    # =====================================================

    def extract(
        self,
        profile: DatabaseProfile,
    ) -> list[GraphNode]:

        nodes = []

        nodes.append(

            self._database_node(
                profile
            )

        )

        nodes.extend(

            self._table_nodes(
                profile
            )

        )

        nodes.extend(

            self._column_nodes(
                profile
            )

        )

        nodes.extend(

            self._datatype_nodes(
                profile
            )

        )

        nodes.extend(

            self._pattern_nodes(
                profile
            )

        )

        nodes.extend(

            self._pii_nodes(
                profile
            )

        )

        return nodes
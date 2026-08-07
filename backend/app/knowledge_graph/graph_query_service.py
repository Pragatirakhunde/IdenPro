from __future__ import annotations

from typing import Any

from app.knowledge_graph.neo4j_repository import Neo4jRepository


class GraphQueryService:
    """
    High-level query service for Knowledge Graph.

    Provides application-level graph queries
    without exposing Neo4j implementation.
    """

    def __init__(
        self,
        repository: Neo4jRepository | None = None,
    ):

        self.repository = (
            repository
            or Neo4jRepository()
        )


    # =====================================================
    # Node Queries
    # =====================================================

    def get_node(
        self,
        node_id: str,
    ) -> dict[str, Any] | None:
        """
        Get a single graph node.
        """

        return self.repository.get_node(
            node_id
        )


    def get_all_nodes(
        self,
        node_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get nodes optionally filtered by type.

        Examples:

        TABLE
        COLUMN
        DATABASE
        PII
        """

        return self.repository.get_nodes(
            node_type
        )


    # =====================================================
    # Schema Discovery Queries
    # =====================================================

    def find_tables(
        self,
    ) -> list[dict[str, Any]]:
        """
        Return all table nodes.
        """

        return self.repository.get_nodes(
            "TABLE"
        )


    def find_columns(
        self,
        table_name: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Find columns.

        If table_name is provided,
        returns columns belonging to that table.
        """

        if table_name is None:

            return self.repository.get_nodes(
                "COLUMN"
            )


        query = """
        MATCH
        (t:GraphNode)-[:HAS_COLUMN]->(c:GraphNode)

        WHERE
        t.label = $table_name

        RETURN
            c.id AS id,
            c.label AS label,
            c.node_type AS node_type,
            properties(c) AS properties
        """


        return self.repository.client.execute_read(
            query,
            {
                "table_name": table_name
            }
        )


    # =====================================================
    # PII Queries
    # =====================================================

    def find_pii_columns(
        self,
    ) -> list[dict[str, Any]]:
        """
        Find columns containing PII.
        """

        query = """

        MATCH
        (c:GraphNode)-[:HAS_PII]->(p:GraphNode)

        RETURN
            c.label AS column,
            p.label AS pii_type,
            properties(c) AS column_properties

        """

        return self.repository.client.execute_read(
            query
        )


    # =====================================================
    # Pattern Search
    # =====================================================

    def search_by_pattern(
        self,
        pattern: str,
    ) -> list[dict[str, Any]]:
        """
        Search columns by detected pattern.

        Example:

        EMAIL
        PHONE
        URL
        """

        query = """

        MATCH
        (c:GraphNode)-[:HAS_PATTERN]->(p:GraphNode)

        WHERE
        toLower(p.label)
        CONTAINS
        toLower($pattern)


        RETURN

            c.label AS column,

            p.label AS pattern

        """


        return self.repository.client.execute_read(
            query,
            {
                "pattern": pattern
            }
        )


    # =====================================================
    # Relationship Queries
    # =====================================================

    def get_relationships(
        self,
        node_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get graph relationships.
        """

        return self.repository.get_relationships(
            node_id
        )


    def get_neighbors(
        self,
        node_id: str,
    ) -> list[dict[str, Any]]:
        """
        Find directly connected nodes.
        """

        query = """

        MATCH
        (source:GraphNode {id:$node_id})
        -[r]-
        (target:GraphNode)


        RETURN

            target.id AS id,

            target.label AS label,

            target.node_type AS type,

            type(r) AS relationship

        """


        return self.repository.client.execute_read(
            query,
            {
                "node_id": node_id
            }
        )


    # =====================================================
    # Impact Analysis
    # =====================================================

    def find_related_tables(
        self,
        table_name: str,
    ) -> list[dict[str, Any]]:
        """
        Find tables connected through relationships.

        Useful for lineage/data impact.
        """

        query = """

        MATCH

        (t:GraphNode {label:$table_name})
        -[*1..2]-
        (related:GraphNode)


        WHERE
        related.node_type = "TABLE"


        RETURN DISTINCT

            related.label AS table

        """


        return self.repository.client.execute_read(
            query,
            {
                "table_name": table_name
            }
        )


    # =====================================================
    # Path Finding
    # =====================================================

    def find_path(
        self,
        source_id: str,
        target_id: str,
    ) -> list[dict[str, Any]]:
        """
        Find shortest path between two entities.
        """

        query = """

        MATCH path =
        shortestPath(

            (
                source:GraphNode
                {id:$source}

            )-[*]-

            (
                target:GraphNode
                {id:$target}

            )

        )


        RETURN

        [
            node IN nodes(path)
            |
            {
                id:node.id,
                label:node.label,
                type:node.node_type
            }

        ] AS path

        """


        result = self.repository.client.execute_read(
            query,
            {
                "source": source_id,
                "target": target_id,
            }
        )


        if not result:

            return []


        return result[0]["path"]


    # =====================================================
    # Graph Search
    # =====================================================

    def search(
        self,
        keyword: str,
    ) -> list[dict[str, Any]]:
        """
        General keyword search.

        Used later by GraphRAG retriever.
        """

        query = """

        MATCH
        (n:GraphNode)


        WHERE

        toLower(n.label)
        CONTAINS
        toLower($keyword)


        RETURN

            n.id AS id,

            n.label AS label,

            n.node_type AS type

        LIMIT 50

        """


        return self.repository.client.execute_read(
            query,
            {
                "keyword": keyword
            }
        )


    # =====================================================
    # Dashboard Summary
    # =====================================================

    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Return graph summary.
        """

        statistics = (
            self.repository.statistics()
        )


        return {

            "graph_nodes":
                statistics["nodes"],

            "graph_relationships":
                statistics["relationships"],

            "tables":
                len(
                    self.find_tables()
                ),

            "pii_columns":
                len(
                    self.find_pii_columns()
                ),

        }
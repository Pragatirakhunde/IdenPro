from __future__ import annotations

from typing import Any

from app.knowledge_graph.models import KnowledgeGraph
from app.knowledge_graph.neo4j_client import Neo4jClient


class Neo4jRepository:
    """
    Handles persistence and retrieval of KnowledgeGraph
    objects in Neo4j.
    """

    def __init__(
        self,
        client: Neo4jClient | None = None,
    ):
        self.client = client or Neo4jClient()

    # =====================================================
    # Database Setup
    # =====================================================

    def create_constraints(self) -> None:
        """
        Create basic Neo4j constraints/indexes.

        Every graph node uses its application-level
        `id` as a unique identifier.
        """

        query = """
        CREATE CONSTRAINT graph_node_id_unique IF NOT EXISTS
        FOR (n:GraphNode)
        REQUIRE n.id IS UNIQUE
        """

        self.client.execute_write(query)

    # =====================================================
    # Clear Graph
    # =====================================================

    def clear(self) -> None:
        """
        Delete the complete graph.

        Use carefully.
        """

        query = """
        MATCH (n)
        DETACH DELETE n
        """

        self.client.execute_write(query)

    # =====================================================
    # Create Node
    # =====================================================

    def create_node(
        self,
        node_id: str,
        label: str,
        node_type: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        """
        Create or update one graph node.
        """

        properties = properties or {}

        query = """
        MERGE (n:GraphNode {id: $id})

        SET
            n.label = $label,
            n.node_type = $node_type

        SET n += $properties
        """

        self.client.execute_write(
            query,
            {
                "id": node_id,
                "label": label,
                "node_type": node_type,
                "properties": properties,
            },
        )

    # =====================================================
    # Create Relationship
    # =====================================================

    def create_relationship(
        self,
        source: str,
        target: str,
        relationship: str,
        properties: dict[str, Any] | None = None,
    ) -> None:
        """
        Create a relationship between two graph nodes.

        Relationship types cannot safely be passed as
        normal Cypher parameters, therefore the value is
        validated before being inserted into the query.
        """

        properties = properties or {}

        safe_relationship = "".join(
            character
            for character in relationship
            if character.isalnum() or character == "_"
        )

        if not safe_relationship:

            raise ValueError(
                "Invalid relationship type."
            )

        query = f"""
        MATCH (source:GraphNode {{id: $source}})
        MATCH (target:GraphNode {{id: $target}})

        MERGE (
            source
        )-[
            r:{safe_relationship}
        ]->(
            target
        )

        SET r += $properties
        """

        self.client.execute_write(
            query,
            {
                "source": source,
                "target": target,
                "properties": properties,
            },
        )

    # =====================================================
    # Store Complete Graph
    # =====================================================

    def save_graph(
        self,
        graph: KnowledgeGraph,
    ) -> dict[str, int]:
        """
        Persist an entire KnowledgeGraph into Neo4j.
        """

        self.create_constraints()

        node_count = 0
        relationship_count = 0

        # -------------------------------------------------
        # Nodes
        # -------------------------------------------------

        for node in graph.nodes:

            self.create_node(
                node_id=node.id,
                label=node.label,
                node_type=str(
                    node.node_type
                ),
                properties=node.properties,
            )

            node_count += 1

        # -------------------------------------------------
        # Relationships
        # -------------------------------------------------

        for edge in graph.edges:

            self.create_relationship(
                source=edge.source,
                target=edge.target,
                relationship=str(
                    edge.relationship
                ),
                properties=edge.properties,
            )

            relationship_count += 1

        return {

            "nodes_created": node_count,

            "relationships_created":
                relationship_count,

        }

    # =====================================================
    # Find Node
    # =====================================================

    def get_node(
        self,
        node_id: str,
    ) -> dict[str, Any] | None:
        """
        Retrieve a node by application-level ID.
        """

        query = """
        MATCH (n:GraphNode {id: $id})

        RETURN
            n.id AS id,
            n.label AS label,
            n.node_type AS node_type,
            properties(n) AS properties
        """

        result = self.client.execute_read(
            query,
            {
                "id": node_id
            },
        )

        if not result:

            return None

        return result[0]

    # =====================================================
    # Get All Nodes
    # =====================================================

    def get_nodes(
        self,
        node_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve all nodes, optionally filtered by type.
        """

        if node_type:

            query = """
            MATCH (n:GraphNode)
            WHERE n.node_type = $node_type

            RETURN
                n.id AS id,
                n.label AS label,
                n.node_type AS node_type,
                properties(n) AS properties

            ORDER BY n.label
            """

            parameters = {
                "node_type": node_type
            }

        else:

            query = """
            MATCH (n:GraphNode)

            RETURN
                n.id AS id,
                n.label AS label,
                n.node_type AS node_type,
                properties(n) AS properties

            ORDER BY n.label
            """

            parameters = {}

        return self.client.execute_read(
            query,
            parameters,
        )

    # =====================================================
    # Get Relationships
    # =====================================================

    def get_relationships(
        self,
        node_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieve graph relationships.

        If node_id is provided, return relationships
        connected to that node.
        """

        if node_id:

            query = """
            MATCH (source:GraphNode)-[r]->(target:GraphNode)

            WHERE
                source.id = $node_id
                OR target.id = $node_id

            RETURN
                source.id AS source,
                target.id AS target,
                type(r) AS relationship,
                properties(r) AS properties
            """

            parameters = {
                "node_id": node_id
            }

        else:

            query = """
            MATCH (source:GraphNode)-[r]->(target:GraphNode)

            RETURN
                source.id AS source,
                target.id AS target,
                type(r) AS relationship,
                properties(r) AS properties
            """

            parameters = {}

        return self.client.execute_read(
            query,
            parameters,
        )

    # =====================================================
    # Graph Statistics
    # =====================================================

    def statistics(self) -> dict[str, int]:
        """
        Return basic graph statistics.
        """

        query = """
        MATCH (n:GraphNode)

        OPTIONAL MATCH (n)-[r]->()

        RETURN
            count(DISTINCT n) AS nodes,
            count(r) AS relationships
        """

        result = self.client.execute_read(
            query
        )

        if not result:

            return {
                "nodes": 0,
                "relationships": 0,
            }

        return {

            "nodes":
                result[0]["nodes"],

            "relationships":
                result[0]["relationships"],

        }

    # =====================================================
    # Delete Node
    # =====================================================

    def delete_node(
        self,
        node_id: str,
    ) -> bool:
        """
        Delete a node and its relationships.
        """

        query = """
        MATCH (n:GraphNode {id: $id})

        DETACH DELETE n

        RETURN count(n) AS deleted
        """

        result = self.client.execute_write(
            query,
            {
                "id": node_id
            },
        )

        return bool(result)

    # =====================================================
    # Health
    # =====================================================

    def health(self) -> dict[str, Any]:
        """
        Return Neo4j connection and graph information.
        """

        connected = (
            self.client.verify_connection()
        )

        if not connected:

            return {
                "connected": False,
                "database": self.client.database,
            }

        statistics = self.statistics()

        return {

            "connected": True,

            "database":
                self.client.database,

            "nodes":
                statistics["nodes"],

            "relationships":
                statistics["relationships"],

        }

    # =====================================================
    # Close
    # =====================================================

    def close(self) -> None:
        """
        Close the Neo4j connection.
        """

        self.client.close()
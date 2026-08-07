from __future__ import annotations

from app.knowledge_graph.entity_extractor import EntityExtractor
from app.knowledge_graph.models import (
    GraphEdge,
    GraphNode,
    KnowledgeGraph,
)
from app.knowledge_graph.relationship_builder import RelationshipBuilder
from app.profiling.models import DatabaseProfile


class GraphBuilder:
    """
    Builds the complete Knowledge Graph from a DatabaseProfile.

    Flow
    ----
    DatabaseProfile
            │
            ▼
      EntityExtractor
            │
            ▼
          Nodes
            │
            ▼
    RelationshipBuilder
            │
            ▼
          Edges
            │
            ▼
      KnowledgeGraph
    """

    def __init__(self):

        self.entity_extractor = EntityExtractor()

        self.relationship_builder = RelationshipBuilder()

    # =====================================================
    # Build Nodes
    # =====================================================

    def _build_nodes(
        self,
        profile: DatabaseProfile,
    ) -> list[GraphNode]:

        return self.entity_extractor.extract(
            profile
        )

    # =====================================================
    # Build Edges
    # =====================================================

    def _build_edges(
        self,
        profile: DatabaseProfile,
    ) -> list[GraphEdge]:

        return self.relationship_builder.build(
            profile
        )

    # =====================================================
    # Remove Duplicate Nodes
    # =====================================================

    def _unique_nodes(
        self,
        nodes: list[GraphNode],
    ) -> list[GraphNode]:

        unique = {}

        for node in nodes:

            unique[node.id] = node

        return list(unique.values())

    # =====================================================
    # Remove Duplicate Edges
    # =====================================================

    def _unique_edges(
        self,
        edges: list[GraphEdge],
    ) -> list[GraphEdge]:

        unique = {}

        for edge in edges:

            key = (
                edge.source,
                edge.target,
                edge.relationship,
            )

            unique[key] = edge

        return list(unique.values())

    # =====================================================
    # Validate Graph
    # =====================================================

    def _validate(
        self,
        graph: KnowledgeGraph,
    ) -> None:
        """
        Ensure every edge references valid nodes.
        """

        node_ids = {

            node.id

            for node in graph.nodes

        }

        invalid = []

        for edge in graph.edges:

            if (
                edge.source not in node_ids
                or edge.target not in node_ids
            ):

                invalid.append(edge)

        if invalid:

            raise ValueError(

                f"{len(invalid)} invalid graph relationships detected."

            )

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(
        self,
        graph: KnowledgeGraph,
    ) -> dict:

        node_types = {}

        edge_types = {}

        for node in graph.nodes:

            node_types[node.node_type] = (

                node_types.get(node.node_type, 0)

                + 1

            )

        for edge in graph.edges:

            edge_types[edge.relationship] = (

                edge_types.get(edge.relationship, 0)

                + 1

            )

        return {

            "nodes": len(graph.nodes),

            "edges": len(graph.edges),

            "node_types": node_types,

            "relationship_types": edge_types,

        }

    # =====================================================
    # Build Graph
    # =====================================================

    def build(
        self,
        profile: DatabaseProfile,
    ) -> KnowledgeGraph:

        nodes = self._build_nodes(
            profile
        )

        edges = self._build_edges(
            profile
        )

        graph = KnowledgeGraph(

            nodes=self._unique_nodes(nodes),

            edges=self._unique_edges(edges),

        )

        self._validate(graph)

        return graph

    # =====================================================
    # Run
    # =====================================================

    def run(
        self,
        profile: DatabaseProfile,
    ) -> dict:

        graph = self.build(
            profile
        )

        return {

            "graph": graph,

            "statistics": self.statistics(
                graph
            ),

        }
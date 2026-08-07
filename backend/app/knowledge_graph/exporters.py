from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import networkx as nx

from app.knowledge_graph.models import KnowledgeGraph


class GraphExporter:
    """
    Exports KnowledgeGraph into formats useful for
    APIs, testing, visualization, and graph databases.
    """

    # =====================================================
    # JSON
    # =====================================================

    def to_dict(
        self,
        graph: KnowledgeGraph,
    ) -> dict[str, Any]:

        return {
            "nodes": [
                {
                    "id": node.id,
                    "label": node.label,
                    "type": node.node_type,
                    "properties": node.properties,
                }
                for node in graph.nodes
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "relationship": edge.relationship,
                    "properties": edge.properties,
                }
                for edge in graph.edges
            ],
        }

    # =====================================================

    def to_json(
        self,
        graph: KnowledgeGraph,
        indent: int = 2,
    ) -> str:

        return json.dumps(
            self.to_dict(graph),
            indent=indent,
            default=str,
        )

    # =====================================================

    def save_json(
        self,
        graph: KnowledgeGraph,
        file_path: str | Path,
    ) -> str:

        path = Path(file_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            self.to_json(graph),
            encoding="utf-8",
        )

        return str(path)

    # =====================================================
    # NetworkX
    # =====================================================

    def to_networkx(
        self,
        graph: KnowledgeGraph,
    ) -> nx.DiGraph:
        """
        Convert custom KnowledgeGraph into
        a NetworkX directed graph.
        """

        nx_graph = nx.DiGraph()

        # -----------------------------
        # Nodes
        # -----------------------------

        for node in graph.nodes:

            nx_graph.add_node(
                node.id,
                label=node.label,
                node_type=node.node_type,
                **node.properties,
            )

        # -----------------------------
        # Edges
        # -----------------------------

        for edge in graph.edges:

            nx_graph.add_edge(
                edge.source,
                edge.target,
                relationship=edge.relationship,
                **edge.properties,
            )

        return nx_graph

    # =====================================================
    # NetworkX Statistics
    # =====================================================

    def networkx_statistics(
        self,
        graph: KnowledgeGraph,
    ) -> dict[str, Any]:

        nx_graph = self.to_networkx(
            graph
        )

        return {

            "nodes":
                nx_graph.number_of_nodes(),

            "edges":
                nx_graph.number_of_edges(),

            "connected":
                nx.is_weakly_connected(nx_graph)
                if nx_graph.number_of_nodes()
                else True,

            "isolated_nodes":
                list(
                    nx.isolates(nx_graph)
                ),

        }

    # =====================================================
    # GraphML
    # =====================================================

    def save_graphml(
        self,
        graph: KnowledgeGraph,
        file_path: str | Path,
    ) -> str:
        """
        Save graph in GraphML format.

        Useful for tools such as Gephi.
        """

        path = Path(file_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        nx_graph = self.to_networkx(
            graph
        )

        # GraphML supports primitive values,
        # so convert complex properties to strings.
        for node_id, data in nx_graph.nodes(data=True):

            for key, value in list(data.items()):

                if not isinstance(
                    value,
                    (
                        str,
                        int,
                        float,
                        bool,
                    ),
                ):

                    data[key] = str(value)

        for source, target, data in nx_graph.edges(data=True):

            for key, value in list(data.items()):

                if not isinstance(
                    value,
                    (
                        str,
                        int,
                        float,
                        bool,
                    ),
                ):

                    data[key] = str(value)

        nx.write_graphml(
            nx_graph,
            path,
        )

        return str(path)

    # =====================================================
    # Export All
    # =====================================================

    def export(
        self,
        graph: KnowledgeGraph,
        json_path: str | Path | None = None,
        graphml_path: str | Path | None = None,
    ) -> dict[str, Any]:
        """
        Export graph into requested formats.
        """

        result = {

            "graph": self.to_dict(graph),

            "networkx":
                self.networkx_statistics(
                    graph
                ),

        }

        if json_path:

            result["json_path"] = (
                self.save_json(
                    graph,
                    json_path,
                )
            )

        if graphml_path:

            result["graphml_path"] = (
                self.save_graphml(
                    graph,
                    graphml_path,
                )
            )

        return result
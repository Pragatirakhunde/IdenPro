from __future__ import annotations

from typing import Any

from app.knowledge_graph.models import KnowledgeGraph


class GraphVisualizer:
    """
    Converts Knowledge Graph into frontend visualization formats.
    """

    # =====================================================
    # React Flow Format
    # =====================================================

    def to_react_flow(
        self,
        graph: KnowledgeGraph,
    ) -> dict[str, Any]:
        """
        Convert graph into React Flow format.

        React Flow expects:

        nodes:
        [
            {
              id,
              data,
              position
            }
        ]

        edges:
        [
            {
              id,
              source,
              target,
              label
            }
        ]
        """

        nodes = []

        edges = []


        # -----------------------------
        # Nodes
        # -----------------------------

        for index, node in enumerate(
            graph.nodes
        ):

            nodes.append(

                {

                    "id":
                        node.id,

                    "type":
                        "default",

                    "data":
                        {

                            "label":
                                node.label,

                            "node_type":
                                str(
                                    node.node_type
                                ),

                            "properties":
                                node.properties,

                        },

                    "position":
                        {

                            "x":
                                (index % 5) * 250,

                            "y":
                                (index // 5) * 150,

                        },

                }

            )


        # -----------------------------
        # Edges
        # -----------------------------

        for index, edge in enumerate(
            graph.edges
        ):

            edges.append(

                {

                    "id":
                        f"edge-{index}",

                    "source":
                        edge.source,

                    "target":
                        edge.target,

                    "label":
                        str(
                            edge.relationship
                        ),

                    "animated":
                        False,

                }

            )


        return {

            "nodes":
                nodes,

            "edges":
                edges,

        }


    # =====================================================
    # Cytoscape Format
    # =====================================================

    def to_cytoscape(
        self,
        graph: KnowledgeGraph,
    ) -> list[dict[str, Any]]:
        """
        Convert graph into Cytoscape elements format.
        """

        elements = []


        # -----------------------------
        # Nodes
        # -----------------------------

        for node in graph.nodes:

            elements.append(

                {

                    "data":
                        {

                            "id":
                                node.id,

                            "label":
                                node.label,

                            "type":
                                str(
                                    node.node_type
                                ),

                            **node.properties,

                        }

                }

            )


        # -----------------------------
        # Edges
        # -----------------------------

        for edge in graph.edges:

            elements.append(

                {

                    "data":
                        {

                            "id":
                                (
                                    f"{edge.source}"
                                    f"-{edge.target}"
                                ),

                            "source":
                                edge.source,

                            "target":
                                edge.target,

                            "label":
                                str(
                                    edge.relationship
                                ),

                            **edge.properties,

                        }

                }

            )


        return elements


    # =====================================================
    # D3.js Format
    # =====================================================

    def to_d3(
        self,
        graph: KnowledgeGraph,
    ) -> dict[str, Any]:
        """
        Convert graph into D3 force graph format.
        """

        return {

            "nodes":

                [

                    {

                        "id":
                            node.id,

                        "name":
                            node.label,

                        "group":
                            str(
                                node.node_type
                            ),

                    }

                    for node in graph.nodes

                ],


            "links":

                [

                    {

                        "source":
                            edge.source,

                        "target":
                            edge.target,

                        "label":
                            str(
                                edge.relationship
                            ),

                    }

                    for edge in graph.edges

                ],

        }


    # =====================================================
    # Simple Tree View
    # =====================================================

    def hierarchy(
        self,
        graph: KnowledgeGraph,
    ) -> dict[str, Any]:
        """
        Create a tree-like representation.

        Useful for:
        Database
          |
          Tables
          |
          Columns
        """

        databases = []

        database_nodes = [

            node

            for node in graph.nodes

            if str(node.node_type)
            == "DATABASE"

        ]


        for database in database_nodes:

            database_data = {

                "name":
                    database.label,

                "type":
                    "DATABASE",

                "children":
                    []

            }


            for edge in graph.edges:

                if (
                    edge.source
                    == database.id
                ):

                    child = next(

                        (

                            node

                            for node in graph.nodes

                            if node.id
                            ==
                            edge.target

                        ),

                        None

                    )


                    if child:

                        database_data["children"].append(

                            {

                                "name":
                                    child.label,

                                "type":
                                    str(
                                        child.node_type
                                    )

                            }

                        )


            databases.append(
                database_data
            )


        return {

            "name":
                "Knowledge Graph",

            "children":
                databases,

        }


    # =====================================================
    # Statistics For Visualization
    # =====================================================

    def visualization_stats(
        self,
        graph: KnowledgeGraph,
    ) -> dict[str, Any]:

        node_types = {}

        relation_types = {}


        for node in graph.nodes:

            node_type = str(
                node.node_type
            )

            node_types[node_type] = (
                node_types.get(
                    node_type,
                    0
                )
                + 1
            )


        for edge in graph.edges:

            relation = str(
                edge.relationship
            )

            relation_types[relation] = (

                relation_types.get(
                    relation,
                    0
                )
                + 1

            )


        return {

            "total_nodes":
                len(graph.nodes),

            "total_edges":
                len(graph.edges),

            "node_types":
                node_types,

            "relationship_types":
                relation_types,

        }
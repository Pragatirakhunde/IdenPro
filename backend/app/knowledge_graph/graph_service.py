from __future__ import annotations

from datetime import datetime
from typing import Any

from app.knowledge_graph.graph_builder import GraphBuilder
from app.knowledge_graph.models import KnowledgeGraph
from app.profiling.models import DatabaseProfile, ProfilingReport
from app.services.profiling_service import ProfilingService


class GraphService:
    """
    Service responsible for generating a Knowledge Graph
    from profiling results.
    """

    def __init__(self):

        self.profiling_service = ProfilingService()

        self.graph_builder = GraphBuilder()

    # =====================================================
    # Helpers
    # =====================================================

    def _now(self) -> str:

        return datetime.utcnow().isoformat()

    # =====================================================
    # Build Graph
    # =====================================================

    def _build_graph(
        self,
        database_profile: DatabaseProfile,
    ) -> KnowledgeGraph:

        return self.graph_builder.build(
            database_profile
        )

    # =====================================================
    # Graph Summary
    # =====================================================

    def _summary(
        self,
        graph: KnowledgeGraph,
    ) -> dict[str, Any]:

        return self.graph_builder.statistics(
            graph
        )

    # =====================================================
    # Serialize Graph
    # =====================================================

    def _graph_dict(
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
    # Build From Profiling Report
    # =====================================================

    def _from_report(
        self,
        report: ProfilingReport,
    ) -> KnowledgeGraph:
        """
        Build a KnowledgeGraph from an existing
        ProfilingReport.
        """

        return self._build_graph(
            report.database_profile
        )

    # =====================================================
    # Graph Response
    # =====================================================

    def _response(
        self,
        graph: KnowledgeGraph,
    ) -> dict[str, Any]:
        """
        Standard response returned by the graph service.
        """

        return {

            "generated_at": self._now(),

            "summary": self._summary(
                graph
            ),

            "graph": self._graph_dict(
                graph
            ),

        }

    # =====================================================
    # Graph Preview
    # =====================================================

    def preview(
        self,
        graph: KnowledgeGraph,
    ) -> dict[str, Any]:
        """
        Lightweight graph preview.
        """

        return {

            "node_count": len(
                graph.nodes
            ),

            "edge_count": len(
                graph.edges
            ),

            "first_nodes": [

                {

                    "id": node.id,

                    "label": node.label,

                    "type": node.node_type,

                }

                for node in graph.nodes[:10]

            ],

            "first_edges": [

                {

                    "source": edge.source,

                    "target": edge.target,

                    "relationship": edge.relationship,

                }

                for edge in graph.edges[:10]

            ],

        }

    # =====================================================
    # Export
    # =====================================================

    def export(
        self,
        graph: KnowledgeGraph,
    ) -> dict[str, Any]:
        """
        Export graph for API consumers.
        """

        return {

            "generated_at": self._now(),

            "statistics": self._summary(
                graph
            ),

            "nodes": self._graph_dict(
                graph
            )["nodes"],

            "edges": self._graph_dict(
                graph
            )["edges"],

        }

    # =====================================================
    # Validate
    # =====================================================

    def validate(
        self,
        graph: KnowledgeGraph,
    ) -> bool:
        """
        Basic graph validation.
        """

        node_ids = {

            node.id

            for node in graph.nodes

        }

        for edge in graph.edges:

            if edge.source not in node_ids:

                return False

            if edge.target not in node_ids:

                return False

        return True
        # =====================================================
    # Build From Database Profile
    # =====================================================

    def build_from_profile(
        self,
        profile: DatabaseProfile,
    ) -> dict[str, Any]:
        """
        Build a Knowledge Graph directly from a DatabaseProfile.
        """

        graph = self._build_graph(
            profile
        )

        if not self.validate(graph):
            raise ValueError(
                "Generated Knowledge Graph failed validation."
            )

        return self._response(
            graph
        )

    # =====================================================
    # Build From Profiling Report
    # =====================================================

    def build_from_report(
        self,
        report: ProfilingReport,
    ) -> dict[str, Any]:
        """
        Build a Knowledge Graph from a ProfilingReport.
        """

        graph = self._from_report(
            report
        )

        if not self.validate(graph):
            raise ValueError(
                "Generated Knowledge Graph failed validation."
            )

        return self._response(
            graph
        )

    # =====================================================
    # Build From Datasource
    # =====================================================

    def build_from_datasource(
        self,
        datasource,
    ) -> dict[str, Any]:
        """
        Complete pipeline:

        Datasource
            ↓
        Profiling
            ↓
        DatabaseProfile
            ↓
        Knowledge Graph
        """

        report = (
            self.profiling_service.profile_datasource(
                datasource
            )
        )

        return self.build_from_report(
            report
        )

    # =====================================================
    # Run
    # =====================================================

    def run(
        self,
        datasource,
    ) -> dict[str, Any]:
        """
        Main entry point for API endpoints.
        """

        try:

            result = self.build_from_datasource(
                datasource
            )

            return {

                "success": True,

                **result,

            }

        except Exception as exc:

            return {

                "success": False,

                "generated_at": self._now(),

                "error": str(exc),

            }

    # =====================================================
    # Run From Existing Profile
    # =====================================================

    def run_from_profile(
        self,
        profile: DatabaseProfile,
    ) -> dict[str, Any]:
        """
        Build graph without running profiling again.
        """

        try:

            result = self.build_from_profile(
                profile
            )

            return {

                "success": True,

                **result,

            }

        except Exception as exc:

            return {

                "success": False,

                "generated_at": self._now(),

                "error": str(exc),

            }

    # =====================================================
    # Health
    # =====================================================

    def health(
        self,
        graph: KnowledgeGraph,
    ) -> dict[str, Any]:
        """
        Return basic graph health information.
        """

        valid = self.validate(
            graph
        )

        statistics = self._summary(
            graph
        )

        return {

            "healthy": valid,

            "nodes": statistics["nodes"],

            "edges": statistics["edges"],

            "node_types": statistics["node_types"],

            "relationship_types":
                statistics["relationship_types"],

        }
    
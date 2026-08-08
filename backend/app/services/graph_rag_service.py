from typing import Any, Optional

from sqlalchemy.orm import Session

from app.knowledge_graph.graph_query_service import (
    GraphQueryService,
)

from app.services.grok_service import (
    GrokService,
)


class GraphRAGService:
    """
    GraphRAG orchestration service.

    Pipeline:

        User Question
             ↓
        Graph Retrieval
             ↓
        Context Construction
             ↓
        Grok LLM
             ↓
        Final Answer
    """

    def __init__(
        self,
        db: Session,
    ):

        self.db = db

        self.graph_query_service = (
            GraphQueryService()
        )

        self.grok_service = GrokService()

    # =====================================================
    # Main Query
    # =====================================================

    def query(
        self,
        question: str,
        project_id: Optional[str] = None,
        datasource_id: Optional[str] = None,
        top_k: int = 5,
    ) -> dict[str, Any]:

        if not question or not question.strip():

            raise ValueError(
                "Question cannot be empty."
            )

        # -------------------------------------------------
        # Step 1: Retrieve graph context
        # -------------------------------------------------

        context = self.retrieve_context(
            question=question,
            project_id=project_id,
            datasource_id=datasource_id,
            top_k=top_k,
        )

        # -------------------------------------------------
        # Step 2: Generate answer using Grok
        # -------------------------------------------------

        answer = self.grok_service.generate_answer(
            question=question,
            context=context,
        )

        # -------------------------------------------------
        # Step 3: Return GraphRAG result
        # -------------------------------------------------

        return {
            "answer": answer,

            "sources": context,

            "graph_context": context,

            "metadata": {
                "top_k": top_k,
                "project_id": project_id,
                "datasource_id": datasource_id,
                "llm": "Grok",
                "model": self.grok_service.model,
            },
        }

    # =====================================================
    # Retrieve Graph Context
    # =====================================================

    def retrieve_context(
        self,
        question: str,
        project_id: Optional[str] = None,
        datasource_id: Optional[str] = None,
        top_k: int = 5,
    ) -> list[Any]:

        try:

            results = (
                self.graph_query_service.search(
                    question
                )
            )

            if results is None:
                return []

            if isinstance(results, list):

                return results[:top_k]

            return [results]

        except Exception as e:

            raise RuntimeError(
                "Knowledge Graph retrieval failed: "
                f"{str(e)}"
            )
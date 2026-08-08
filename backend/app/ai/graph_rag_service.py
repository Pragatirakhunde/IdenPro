from __future__ import annotations

from typing import Any

from app.ai.llm_client import llm
from app.ai.prompt_builder import PromptBuilder
from app.knowledge_graph.graph_query_service import GraphQueryService


class GraphRAGService:
    """
    GraphRAG service.

    Flow:

        User Question
             ↓
        Knowledge Graph retrieval
             ↓
        Relevant graph context
             ↓
        Prompt Builder
             ↓
        Grok LLM
             ↓
        Final Answer
    """

    def __init__(self):
        self.graph_query_service = GraphQueryService()

    # =====================================================
    # Retrieve Graph Context
    # =====================================================

    def retrieve_context(
        self,
        question: str,
    ) -> Any:
        """
        Retrieve relevant information from the
        Knowledge Graph.
        """

        if not question or not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        question = question.strip()

        # -------------------------------------------------
        # Search Knowledge Graph
        # -------------------------------------------------

        try:

            results = self.graph_query_service.search(
                question
            )

        except AttributeError:

            # ------------------------------------------------
            # Fallback for implementations where the method
            # is called search_graph()
            # ------------------------------------------------

            try:

                results = (
                    self.graph_query_service.search_graph(
                        question
                    )
                )

            except AttributeError:

                # ------------------------------------------------
                # Final fallback
                # ------------------------------------------------

                results = []

        return results

    # =====================================================
    # Generate Answer
    # =====================================================

    def generate_answer(
        self,
        question: str,
        graph_context: Any,
    ) -> str:
        """
        Generate final answer using Grok.
        """

        prompts = PromptBuilder.build(
            question=question,
            graph_context=graph_context,
        )

        answer = llm.generate(
            prompt=prompts["user_prompt"],
            system_prompt=prompts["system_prompt"],
        )

        return answer

    # =====================================================
    # Complete GraphRAG Pipeline
    # =====================================================

    def ask(
        self,
        question: str,
    ) -> dict[str, Any]:
        """
        Complete GraphRAG pipeline.

        Returns both the answer and the retrieved
        graph context.
        """

        if not question or not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        question = question.strip()

        # -------------------------------------------------
        # Step 1: Retrieve
        # -------------------------------------------------

        graph_context = self.retrieve_context(
            question
        )

        # -------------------------------------------------
        # Step 2: Generate
        # -------------------------------------------------

        answer = self.generate_answer(
            question=question,
            graph_context=graph_context,
        )

        # -------------------------------------------------
        # Step 3: Return
        # -------------------------------------------------

        return {
            "question": question,
            "answer": answer,
            "graph_context": graph_context,
        }


# =========================================================
# Singleton
# =========================================================

graph_rag_service = GraphRAGService()
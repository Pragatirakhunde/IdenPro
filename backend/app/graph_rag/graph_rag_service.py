from __future__ import annotations

from typing import Any

from app.graph_rag.graph_retriever import (
    GraphRetriever,
)

from app.graph_rag.prompt_builder import (
    GraphPromptBuilder,
)

from app.graph_rag.llm_service import (
    LLMService,
)


class GraphRAGService:
    """
    Main GraphRAG orchestration service.

    Flow:

        Question
            ↓
        Graph Retriever
            ↓
        Graph Context
            ↓
        Prompt Builder
            ↓
        LLM
            ↓
        Answer
    """

    def __init__(self):

        self.retriever = GraphRetriever()

        self.prompt_builder = (
            GraphPromptBuilder()
        )

        self.llm = LLMService()

    # =====================================================
    # Ask Question
    # =====================================================

    def ask(
        self,
        question: str,
        max_results: int = 20,
    ) -> dict[str, Any]:

        question = question.strip()

        if not question:

            raise ValueError(
                "Question cannot be empty."
            )

        # -------------------------------------------------
        # 1. Retrieve Graph Information
        # -------------------------------------------------

        graph_results = (
            self.retriever.search(
                question=question,
                max_results=max_results,
            )
        )

        # -------------------------------------------------
        # 2. Build Graph Context
        # -------------------------------------------------

        context = (
            self.prompt_builder.build_context(
                graph_results
            )
        )

        # -------------------------------------------------
        # 3. Build LLM Prompt
        # -------------------------------------------------

        prompt = (
            self.prompt_builder.build_prompt(
                question=question,
                context=context,
            )
        )

        # -------------------------------------------------
        # 4. Generate Answer
        # -------------------------------------------------

        answer = self.llm.generate(
            prompt
        )

        # -------------------------------------------------
        # 5. Return
        # -------------------------------------------------

        evidence = []

        for item in graph_results:

            evidence.append(
                {
                    "source": item.get(
                        "source_name",
                        item.get(
                            "source_id",
                            "Unknown",
                        ),
                    ),

                    "target": item.get(
                        "target_name",
                        item.get(
                            "target_id",
                            "Unknown",
                        ),
                    ),

                    "relationship": item.get(
                        "relationship",
                        "RELATED_TO",
                    ),
                }
            )

        return {
            "question": question,
            "answer": answer,
            "evidence": evidence,
            "retrieved_context": graph_results,
        }
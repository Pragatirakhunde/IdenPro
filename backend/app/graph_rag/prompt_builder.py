from __future__ import annotations

from typing import Any


class GraphPromptBuilder:
    """
    Builds the prompt used by the LLM from
    Knowledge Graph results.
    """

    # =====================================================
    # Build Context
    # =====================================================

    @staticmethod
    def build_context(
        graph_results: list[dict[str, Any]],
    ) -> str:

        if not graph_results:
            return (
                "No relevant information was found "
                "in the Knowledge Graph."
            )

        lines = []

        for item in graph_results:

            source = item.get(
                "source_name",
                item.get("source_id", "Unknown"),
            )

            target = item.get(
                "target_name",
                item.get("target_id", "Unknown"),
            )

            relationship = item.get(
                "relationship",
                "RELATED_TO",
            )

            source_labels = item.get(
                "source_labels",
                [],
            )

            target_labels = item.get(
                "target_labels",
                [],
            )

            source_type = (
                ", ".join(source_labels)
                if source_labels
                else "ENTITY"
            )

            target_type = (
                ", ".join(target_labels)
                if target_labels
                else "ENTITY"
            )

            lines.append(
                f"{source} ({source_type}) "
                f"--[{relationship}]--> "
                f"{target} ({target_type})"
            )

        return "\n".join(lines)

    # =====================================================
    # Build Final Prompt
    # =====================================================

    @staticmethod
    def build_prompt(
        question: str,
        context: str,
    ) -> str:

        return f"""
You are an enterprise data knowledge assistant.

Answer the user's question using ONLY the
Knowledge Graph context provided below.

If the context does not contain enough information,
clearly say that the Knowledge Graph does not contain
enough information.

Do not invent tables, columns, databases,
relationships, or other facts.

Explain database relationships clearly when relevant.

Knowledge Graph Context:
------------------------

{context}

------------------------

User Question:
{question}

Instructions:

1. Answer directly.
2. Use the graph context as the source of truth.
3. Do not hallucinate information.
4. Mention relevant tables, columns, databases,
   or relationships when available.
5. Keep the answer understandable.
"""
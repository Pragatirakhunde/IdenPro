from typing import Any

from openai import OpenAI

from app.config import settings


class GrokService:
    """
    Service responsible for communicating with
    xAI's Grok API.
    """

    def __init__(self):
        if not settings.XAI_API_KEY:
            raise ValueError(
                "XAI_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=settings.XAI_API_KEY,
            base_url=settings.XAI_BASE_URL,
        )

        self.model = settings.GROK_MODEL

    # =====================================================
    # Generate Answer
    # =====================================================

    def generate_answer(
        self,
        question: str,
        context: list[Any],
    ) -> str:

        if not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        context_text = self._format_context(
            context
        )

        system_prompt = """
You are an Enterprise Knowledge Graph assistant.

Your job is to answer questions using the
provided Knowledge Graph context.

Rules:

1. Use the provided context as the primary source.
2. Do not invent database, table, column, or
   relationship information.
3. If the context does not contain enough information,
   clearly say that the information is not available.
4. Give concise but useful answers.
5. When possible, mention the relevant tables,
   columns, databases, or relationships.
6. Do not expose passwords, secrets, API keys,
   or other sensitive credentials.
"""

        user_prompt = f"""
Knowledge Graph Context:

{context_text}

User Question:

{question}

Answer the question using the Knowledge Graph
context above.
"""

        try:

            response = self.client.chat.completions.create(
                model=self.model,
                temperature=settings.GRAPHRAG_TEMPERATURE,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
            )

            answer = response.choices[0].message.content

            if not answer:
                return (
                    "Grok did not return an answer."
                )

            return answer.strip()

        except Exception as e:

            raise RuntimeError(
                f"Grok API request failed: {str(e)}"
            )

    # =====================================================
    # Format Graph Context
    # =====================================================

    @staticmethod
    def _format_context(
        context: list[Any],
    ) -> str:

        if not context:
            return (
                "No relevant Knowledge Graph "
                "context was found."
            )

        formatted = []

        for index, item in enumerate(
            context,
            start=1,
        ):

            formatted.append(
                f"Context {index}:\n{item}"
            )

        return "\n\n".join(formatted)
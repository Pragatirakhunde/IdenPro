from typing import Optional

from openai import OpenAI

from app.config import settings


class GrokClient:
    """
    Client for interacting with xAI Grok using
    the OpenAI-compatible API.
    """

    def __init__(self):
        api_key = getattr(settings, "XAI_API_KEY", None)

        if not api_key:
            raise ValueError(
                "XAI_API_KEY is not configured."
            )

        self.model = getattr(
            settings,
            "XAI_MODEL",
            "grok-3-mini",
        )

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1",
        )

    # =====================================================
    # Generate Answer
    # =====================================================

    def generate_answer(
        self,
        question: str,
        context: str,
        conversation_history: Optional[list] = None,
    ) -> str:

        system_prompt = """
You are an AI assistant for an Enterprise
Knowledge Management System.

You answer questions using the provided
Knowledge Graph context.

Rules:

1. Use the provided context as the primary source.
2. Do not invent databases, tables, columns,
   relationships or facts.
3. If the context does not contain enough
   information, clearly say that the information
   is not available.
4. Explain relationships clearly.
5. Keep the answer concise but useful.
6. Mention relevant tables, columns or entities
   when they are available.
7. If the question asks about PII, explain which
   columns are involved.
"""

        user_prompt = f"""
Knowledge Graph Context
=======================

{context}

=======================

User Question
=======================

{question}

Answer the question using the Knowledge Graph
context above.
"""

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            }
        ]

        if conversation_history:

            messages.extend(
                conversation_history
            )

        messages.append(
            {
                "role": "user",
                "content": user_prompt,
            }
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
        )

        return (
            response.choices[0]
            .message
            .content
            .strip()
        )


# =========================================================
# Singleton
# =========================================================

grok_client = GrokClient()
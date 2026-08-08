from __future__ import annotations

import os

from openai import OpenAI


class GrokLLM:

    def __init__(self):

        self.api_key = os.getenv("XAI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "XAI_API_KEY is not configured."
            )

        self.model = os.getenv(
            "XAI_MODEL",
            "grok-4.5",
        )

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1",
        )

    # =====================================================
    # Generate Response
    # =====================================================

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
    ) -> str:

        messages = []

        if system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": system_prompt,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
        )

        return response.choices[0].message.content


# =========================================================
# Singleton
# =========================================================

llm = GrokLLM()
from __future__ import annotations

import os
from typing import Any


class LLMService:
    """
    LLM abstraction for GraphRAG.

    The GraphRAG layer does not directly depend
    on a specific LLM provider.
    """

    def __init__(self):

        self.provider = os.getenv(
            "LLM_PROVIDER",
            "none",
        )

    # =====================================================
    # Generate Answer
    # =====================================================

    def generate(
        self,
        prompt: str,
    ) -> str:

        if self.provider == "none":

            return (
                "LLM is not configured yet.\n\n"
                "Retrieved Knowledge Graph context:\n\n"
                + prompt
            )

        # Provider implementation will be added here.
        #
        # Example:
        #
        # if self.provider == "openai":
        #     return self._generate_openai(prompt)
        #
        # if self.provider == "gemini":
        #     return self._generate_gemini(prompt)

        raise ValueError(
            f"Unsupported LLM provider: "
            f"{self.provider}"
        )
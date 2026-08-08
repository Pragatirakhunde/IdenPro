from typing import Any, Optional

from pydantic import BaseModel, Field


# ==========================================================
# GraphRAG Request
# ==========================================================

class GraphRAGRequest(BaseModel):
    """
    Request sent by the frontend to GraphRAG.
    """

    question: str = Field(
        ...,
        min_length=1,
        description="Natural language question",
    )

    project_id: Optional[str] = None

    datasource_id: Optional[str] = None

    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
    )


# ==========================================================
# GraphRAG Response
# ==========================================================

class GraphRAGResponse(BaseModel):
    """
    Response returned by GraphRAG.
    """

    question: str

    answer: str

    sources: list[Any] = []

    graph_context: list[Any] = []

    metadata: dict[str, Any] = {}
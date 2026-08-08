from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.ai.graph_rag_service import graph_rag_service
from app.auth.dependencies import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/api/chat",
    tags=["GraphRAG Chat"],
)


# ==========================================================
# Request Schema
# ==========================================================

class ChatRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
        description="Question to ask the Knowledge Graph",
    )


# ==========================================================
# Response Schema
# ==========================================================

class ChatResponse(BaseModel):

    question: str

    answer: str

    graph_context: Any = None


# ==========================================================
# GraphRAG Chat
# ==========================================================

@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    current_user: User = Depends(
        get_current_user
    ),
):

    try:

        result = graph_rag_service.ask(
            request.question
        )

        return result

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GraphRAG failed: {str(e)}",
        )
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.models.user import User

from app.schemas.graph_rag import (
    GraphRAGRequest,
    GraphRAGResponse,
)

from app.services.graph_rag_service import (
    GraphRAGService,
)


router = APIRouter(
    prefix="/api/graph-rag",
    tags=["GraphRAG"],
)


# ==========================================================
# Health
# ==========================================================

@router.get("/health")
def graph_rag_health(
    current_user: User = Depends(
        get_current_user
    ),
):

    return {
        "status": "healthy",
        "service": "GraphRAG",
    }


# ==========================================================
# Query
# ==========================================================

@router.post(
    "/query",
    response_model=GraphRAGResponse,
)
def query_graph_rag(
    request: GraphRAGRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    try:

        service = GraphRAGService(
            db=db
        )

        result = service.query(
            question=request.question,
            project_id=request.project_id,
            datasource_id=request.datasource_id,
            top_k=request.top_k,
        )

        return GraphRAGResponse(
            question=request.question,
            answer=result.get(
                "answer",
                "",
            ),
            sources=result.get(
                "sources",
                [],
            ),
            graph_context=result.get(
                "graph_context",
                [],
            ),
            metadata=result.get(
                "metadata",
                {},
            ),
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "GraphRAG query failed: "
                f"{str(e)}"
            ),
        )


# ==========================================================
# Context Only
# ==========================================================

@router.post("/context")
def get_graph_context(
    request: GraphRAGRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    try:

        service = GraphRAGService(
            db=db
        )

        context = service.retrieve_context(
            question=request.question,
            project_id=request.project_id,
            datasource_id=request.datasource_id,
            top_k=request.top_k,
        )

        return {
            "question": request.question,
            "context": context,
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Graph context retrieval failed: "
                f"{str(e)}"
            ),
        )


# ==========================================================
# Info
# ==========================================================

@router.get("/info")
def graph_rag_info(
    current_user: User = Depends(
        get_current_user
    ),
):

    return {
        "service": "GraphRAG",

        "pipeline": [
            "User Question",
            "Graph Retrieval",
            "Context Construction",
            "LLM Generation",
            "Final Answer",
        ],

        "knowledge_graph": "Neo4j",

        "llm": "Grok",
    }
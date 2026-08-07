from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends
from typing import Any

from app.knowledge_graph.graph_service import GraphService
from app.knowledge_graph.graph_query_service import GraphQueryService
from app.knowledge_graph.visualizer import GraphVisualizer
from app.knowledge_graph.neo4j_repository import Neo4jRepository


router = APIRouter(
    prefix="/knowledge-graph",
    tags=["Knowledge Graph"]
)


# =====================================================
# Dependencies
# =====================================================

def get_repository():

    return Neo4jRepository()



def get_query_service():

    return GraphQueryService()



def get_visualizer():

    return GraphVisualizer()



def get_graph_service():

    return GraphService()



# =====================================================
# Build Knowledge Graph
# =====================================================

@router.post(
    "/build/{datasource_id}"
)
def build_graph(
    datasource_id: int,
    service: GraphService = Depends(
        get_graph_service
    ),
):
    """
    Build knowledge graph from datasource.

    Flow:

    Datasource
        ↓
    Metadata
        ↓
    Profiling
        ↓
    GraphBuilder
        ↓
    Neo4j
    """

    try:

        result = service.build_graph(
            datasource_id
        )

        return {

            "message":
                "Knowledge graph created successfully",

            "result":
                result

        }


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )



# =====================================================
# Graph Statistics
# =====================================================

@router.get(
    "/statistics"
)
def graph_statistics(
    repository: Neo4jRepository = Depends(
        get_repository
    ),
):
    """
    Return graph statistics.
    """

    try:

        return repository.statistics()


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )



# =====================================================
# Get All Nodes
# =====================================================

@router.get(
    "/nodes"
)
def get_nodes(
    node_type: str | None = None,
    query_service: GraphQueryService = Depends(
        get_query_service
    ),
):
    """
    Get graph nodes.

    Example:

    /nodes?node_type=TABLE

    """

    return query_service.get_all_nodes(
        node_type
    )



# =====================================================
# Get Relationships
# =====================================================

@router.get(
    "/relationships"
)
def get_relationships(
    node_id: str | None = None,
    query_service: GraphQueryService = Depends(
        get_query_service
    ),
):
    """
    Get graph relationships.
    """

    return query_service.get_relationships(
        node_id
    )



# =====================================================
# Search Graph
# =====================================================

@router.get(
    "/search"
)
def search_graph(
    q: str,
    query_service: GraphQueryService = Depends(
        get_query_service
    ),
):
    """
    Search graph entities.

    Example:

    /search?q=customer

    """

    return query_service.search(
        q
    )



# =====================================================
# Find PII
# =====================================================

@router.get(
    "/pii"
)
def pii_columns(
    query_service: GraphQueryService = Depends(
        get_query_service
    ),
):
    """
    Find columns containing PII.
    """

    return query_service.find_pii_columns()



# =====================================================
# Find Tables
# =====================================================

@router.get(
    "/tables"
)
def tables(
    query_service: GraphQueryService = Depends(
        get_query_service
    ),
):
    """
    Return all tables.
    """

    return query_service.find_tables()



# =====================================================
# Table Columns
# =====================================================

@router.get(
    "/tables/{table_name}/columns"
)
def table_columns(
    table_name: str,
    query_service: GraphQueryService = Depends(
        get_query_service
    ),
):
    """
    Return columns of a table.
    """

    return query_service.find_columns(
        table_name
    )



# =====================================================
# Neighbours
# =====================================================

@router.get(
    "/neighbors/{node_id}"
)
def neighbors(
    node_id: str,
    query_service: GraphQueryService = Depends(
        get_query_service
    ),
):
    """
    Return directly connected nodes.
    """

    return query_service.get_neighbors(
        node_id
    )



# =====================================================
# Path Finding
# =====================================================

@router.get(
    "/path"
)
def find_path(
    source: str,
    target: str,
    query_service: GraphQueryService = Depends(
        get_query_service
    ),
):
    """
    Find shortest path between entities.
    """

    return query_service.find_path(
        source,
        target
    )



# =====================================================
# React Flow Visualization
# =====================================================

@router.get(
    "/visualization/react-flow"
)
def react_flow_graph(
    graph_service: GraphService = Depends(
        get_graph_service
    ),
    visualizer: GraphVisualizer = Depends(
        get_visualizer
    ),
):
    """
    Return graph in React Flow format.
    """

    try:

        graph = (
            graph_service.get_current_graph()
        )


        return visualizer.to_react_flow(
            graph
        )


    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )



# =====================================================
# Cytoscape Visualization
# =====================================================

@router.get(
    "/visualization/cytoscape"
)
def cytoscape_graph(
    graph_service: GraphService = Depends(
        get_graph_service
    ),
    visualizer: GraphVisualizer = Depends(
        get_visualizer
    ),
):
    """
    Return Cytoscape format.
    """

    graph = (
        graph_service.get_current_graph()
    )


    return visualizer.to_cytoscape(
        graph
    )



# =====================================================
# Graph Health
# =====================================================

@router.get(
    "/health"
)
def health(
    repository: Neo4jRepository = Depends(
        get_repository
    ),
):
    """
    Check Neo4j and graph status.
    """

    return repository.health()
import requests
import streamlit as st


# ============================================================
# Backend
# ============================================================

BACKEND_URL = "http://127.0.0.1:8000"


# ============================================================
# Authentication
# ============================================================

def get_headers():

    token = st.session_state.get("access_token")

    if not token:
        return {}

    return {
        "Authorization": f"Bearer {token}"
    }


# ============================================================
# GET
# ============================================================

def get(
    endpoint: str,
    params: dict | None = None,
):

    response = requests.get(
        f"{BACKEND_URL}{endpoint}",
        params=params,
        headers=get_headers(),
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# POST JSON
# ============================================================

def post(
    endpoint: str,
    data: dict | None = None,
):

    response = requests.post(
        f"{BACKEND_URL}{endpoint}",
        json=data,
        headers=get_headers(),
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# DELETE
# ============================================================

def delete(endpoint: str):

    response = requests.delete(
        f"{BACKEND_URL}{endpoint}",
        headers=get_headers(),
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# PROJECTS
# ============================================================

def get_projects():

    return get(
        "/api/projects"
    )


def get_project(
    project_id: str,
):

    return get(
        f"/api/projects/{project_id}"
    )


def create_project(
    name: str,
    description: str | None = None,
):

    data = {
        "name": name,
        "description": description,
    }

    return post(
        "/api/projects",
        data,
    )


def delete_project(
    project_id: str,
):

    return delete(
        f"/api/projects/{project_id}"
    )


# ============================================================
# DATA SOURCES
# ============================================================

def upload_file(
    project_id: str,
    name: str,
    uploaded_file,
    description: str | None = None,
):

    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type,
        )
    }

    data = {
        "project_id": project_id,
        "name": name,
    }

    if description:
        data["description"] = description

    response = requests.post(
        f"{BACKEND_URL}/api/datasources/upload",
        data=data,
        files=files,
        headers=get_headers(),
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


def connect_database(
    project_id: str,
    connection_name: str,
    db_type: str,
    username: str,
    password: str,
    host: str,
    port: int,
    database_name: str,
    ssl_enabled: bool = False,
    description: str | None = None,
):

    data = {
        "project_id": project_id,
        "connection_name": connection_name,
        "db_type": db_type,
        "username": username,
        "password": password,
        "host": host,
        "port": port,
        "database_name": database_name,
        "ssl_enabled": ssl_enabled,
    }

    if description:
        data["description"] = description

    return post(
        "/api/datasources/database",
        data,
    )


def get_project_datasources(
    project_id: str,
):

    return get(
        f"/api/datasources/project/{project_id}"
    )


def delete_datasource(
    datasource_id: str,
):

    return delete(
        f"/api/datasources/{datasource_id}"
    )


# ============================================================
# KNOWLEDGE GRAPH
# ============================================================

def get_knowledge_graph_health():

    return get(
        "/api/knowledge-graph/health"
    )


def get_graph_statistics():

    return get(
        "/api/knowledge-graph/statistics"
    )


def get_graph_nodes(
    node_type: str | None = None,
):

    params = None

    if node_type:
        params = {
            "node_type": node_type
        }

    return get(
        "/api/knowledge-graph/nodes",
        params=params,
    )


def get_graph_relationships(
    node_id: str | None = None,
):

    params = None

    if node_id:
        params = {
            "node_id": node_id
        }

    return get(
        "/api/knowledge-graph/relationships",
        params=params,
    )


def search_graph(
    keyword: str,
):

    return get(
        "/api/knowledge-graph/search",
        params={
            "q": keyword,
        },
    )


def get_tables():

    return get(
        "/api/knowledge-graph/tables"
    )


def get_pii_columns():

    return get(
        "/api/knowledge-graph/pii"
    )


def get_react_flow_graph():

    return get(
        "/api/knowledge-graph/visualization/react-flow"
    )


def get_cytoscape_graph():

    return get(
        "/api/knowledge-graph/visualization/cytoscape"
    )


def build_knowledge_graph(
    datasource_id: str,
):

    return post(
        f"/api/knowledge-graph/build/{datasource_id}"
    )
# ============================================================
# GraphRAG
# ============================================================

def get_graph_rag_health():

    return get(
        "/api/graph-rag/health"
    )


def ask_graph_rag(
    question: str,
    max_results: int = 20,
):

    return post(
        "/api/graph-rag/query",
        data={
            "question": question,
            "max_results": max_results,
        },
    )
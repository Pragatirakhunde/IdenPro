import streamlit as st
import pandas as pd

from services.api_client import (
    get_knowledge_graph_health,
    get_graph_statistics,
    get_graph_nodes,
    get_graph_relationships,
    search_graph,
    get_tables,
    get_pii_columns,
    get_react_flow_graph,
)

from services.graph_visualizer import (
    create_graph_visualization,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Knowledge Graph",
    page_icon="🕸️",
    layout="wide",
)


# ============================================================
# HEADER
# ============================================================

st.title("🕸️ Knowledge Graph")

st.write(
    "Explore relationships between databases, tables, "
    "columns and other metadata entities."
)


# ============================================================
# BACKEND / NEO4J STATUS
# ============================================================

st.subheader("System Status")

try:

    health = get_knowledge_graph_health()

    st.success(
        "Knowledge Graph backend is connected."
    )

    with st.expander("View health response"):

        st.json(health)

except Exception as e:

    st.error(
        f"Knowledge Graph backend is not available: {e}"
    )


# ============================================================
# GRAPH STATISTICS
# ============================================================

st.divider()

st.subheader("📊 Graph Statistics")

try:

    stats = get_graph_statistics()

    total_nodes = stats.get(
        "total_nodes",
        stats.get(
            "nodes",
            0,
        ),
    )

    total_relationships = stats.get(
        "total_relationships",
        stats.get(
            "relationships",
            stats.get(
                "total_edges",
                stats.get(
                    "edges",
                    0,
                ),
            ),
        ),
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Total Nodes",
            total_nodes,
        )

    with col2:

        st.metric(
            "Total Relationships",
            total_relationships,
        )

except Exception as e:

    st.warning(
        f"Could not load graph statistics: {e}"
    )


# ============================================================
# INTERACTIVE GRAPH
# ============================================================

st.divider()

st.subheader(
    "🕸️ Interactive Knowledge Graph"
)

try:

    graph_data = get_react_flow_graph()

    nodes = graph_data.get(
        "nodes",
        [],
    )

    edges = graph_data.get(
        "edges",
        [],
    )

    if nodes:

        st.write(
            f"Showing {len(nodes)} nodes "
            f"and {len(edges)} relationships."
        )

        create_graph_visualization(
            nodes,
            edges,
        )

    else:

        st.info(
            "No Knowledge Graph data available yet."
        )

except Exception as e:

    st.error(
        f"Unable to load graph visualization: {e}"
    )


# ============================================================
# SEARCH
# ============================================================

st.divider()

st.subheader("🔎 Search Knowledge Graph")

search_text = st.text_input(
    "Search for a table, column or entity",
    placeholder="Example: customer",
)

if search_text:

    try:

        results = search_graph(
            search_text
        )

        st.write(
            f"Search results for: **{search_text}**"
        )

        if results:

            st.json(results)

        else:

            st.info(
                "No matching entities found."
            )

    except Exception as e:

        st.error(
            f"Search failed: {e}"
        )


# ============================================================
# TABLES
# ============================================================

st.divider()

st.subheader("📋 Tables")

try:

    tables = get_tables()

    if tables:

        if isinstance(
            tables,
            list,
        ):

            table_data = []

            for table in tables:

                if isinstance(
                    table,
                    dict,
                ):

                    table_data.append(
                        table
                    )

                else:

                    table_data.append(
                        {
                            "table": str(table)
                        }
                    )

            if table_data:

                st.dataframe(
                    pd.DataFrame(
                        table_data
                    ),
                    use_container_width=True,
                )

        else:

            st.json(tables)

    else:

        st.info(
            "No tables found in the Knowledge Graph."
        )

except Exception as e:

    st.warning(
        f"Could not load tables: {e}"
    )


# ============================================================
# NODE EXPLORER
# ============================================================

st.divider()

st.subheader("🧩 Node Explorer")

node_type = st.selectbox(
    "Select node type",
    [
        "All",
        "DATABASE",
        "TABLE",
        "COLUMN",
    ],
)

try:

    selected_type = (
        None
        if node_type == "All"
        else node_type
    )

    nodes = get_graph_nodes(
        selected_type
    )

    if nodes:

        st.json(nodes)

    else:

        st.info(
            "No nodes found."
        )

except Exception as e:

    st.warning(
        f"Could not load nodes: {e}"
    )


# ============================================================
# RELATIONSHIPS
# ============================================================

st.divider()

st.subheader("🔗 Relationships")

node_id = st.text_input(
    "Node ID (optional)",
    placeholder="Example: table_customers",
)

try:

    relationships = get_graph_relationships(
        node_id
        if node_id
        else None
    )

    if relationships:

        st.json(
            relationships
        )

    else:

        st.info(
            "No relationships found."
        )

except Exception as e:

    st.warning(
        f"Could not load relationships: {e}"
    )


# ============================================================
# PII
# ============================================================

st.divider()

st.subheader("🔐 PII Detection")

try:

    pii = get_pii_columns()

    if pii:

        st.warning(
            "PII columns detected."
        )

        st.json(
            pii
        )

    else:

        st.success(
            "No PII columns detected."
        )

except Exception as e:

    st.warning(
        f"Could not load PII information: {e}"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Knowledge Graph Explorer • "
    "FastAPI + Neo4j + Streamlit"
)

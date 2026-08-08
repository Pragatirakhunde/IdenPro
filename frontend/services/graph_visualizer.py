from pyvis.network import Network
import streamlit.components.v1 as components


def create_graph_visualization(
    nodes,
    edges,
    height=650,
):
    """
    Display Knowledge Graph using PyVis.

    Accepts nodes and edges returned by the
    backend GraphVisualizer.to_react_flow().
    """

    network = Network(
        height=f"{height}px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#000000",
        directed=True,
    )

    # ========================================================
    # Graph Physics
    # ========================================================

    network.barnes_hut(
        gravity=-3000,
        central_gravity=0.2,
        spring_length=150,
        spring_strength=0.04,
        damping=0.09,
    )

    # ========================================================
    # Nodes
    # ========================================================

    for node in nodes:

        node_id = str(
            node.get("id", "")
        )

        # Your backend puts graph information
        # inside the "data" object.
        data = node.get(
            "data",
            {},
        )

        label = data.get(
            "label",
            node_id,
        )

        node_type = data.get(
            "node_type",
            "UNKNOWN",
        )

        properties = data.get(
            "properties",
            {},
        )

        # ----------------------------------------------------
        # Tooltip
        # ----------------------------------------------------

        title = (
            f"<b>{label}</b><br>"
            f"Type: {node_type}<br>"
        )

        if isinstance(
            properties,
            dict,
        ):

            for key, value in properties.items():

                title += (
                    f"{key}: {value}<br>"
                )

        # ----------------------------------------------------
        # Add Node
        # ----------------------------------------------------

        network.add_node(
            node_id,
            label=str(label),
            title=title,
        )

    # ========================================================
    # Edges
    # ========================================================

    for index, edge in enumerate(edges):

        source = str(
            edge.get(
                "source",
                "",
            )
        )

        target = str(
            edge.get(
                "target",
                "",
            )
        )

        label = edge.get(
            "label",
            "",
        )

        if not source or not target:
            continue

        network.add_edge(
            source,
            target,
            label=str(label),
            arrows="to",
        )

    # ========================================================
    # Generate HTML
    # ========================================================

    html_file = (
        "knowledge_graph.html"
    )

    network.save_graph(
        html_file
    )

    # ========================================================
    # Display in Streamlit
    # ========================================================

    with open(
        html_file,
        "r",
        encoding="utf-8",
    ) as file:

        html = file.read()

    components.html(
        html,
        height=height,
        scrolling=True,
    )
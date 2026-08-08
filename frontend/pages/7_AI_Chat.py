import streamlit as st

from services.api_client import (
    ask_graph_rag,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Chat",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# Authentication
# ============================================================

if "access_token" not in st.session_state:

    st.warning(
        "Please login first."
    )

    st.stop()


# ============================================================
# Header
# ============================================================

st.title("🤖 AI Knowledge Assistant")

st.write(
    """
Ask questions about your organization's
databases, tables, columns and relationships.
"""
)


# ============================================================
# Example Questions
# ============================================================

st.subheader(
    "Example Questions"
)

examples = [
    "Which tables are related to customers?",
    "What columns are present in the customer table?",
    "Which tables contain customer information?",
    "What relationships exist between orders and customers?",
    "Which columns may contain PII?",
]


for example in examples:

    if st.button(
        example,
        use_container_width=True,
    ):

        st.session_state[
            "chat_question"
        ] = example


# ============================================================
# Question
# ============================================================

question = st.text_area(
    "Ask your question",
    value=st.session_state.get(
        "chat_question",
        "",
    ),
    placeholder=(
        "Example: "
        "Which tables are connected to customers?"
    ),
    height=120,
)


# ============================================================
# Ask
# ============================================================

if st.button(
    "🔍 Ask Knowledge Graph",
    type="primary",
):

    if not question.strip():

        st.warning(
            "Please enter a question."
        )

        st.stop()

    with st.spinner(
        "Searching Knowledge Graph..."
    ):

        try:

            result = ask_graph_rag(
                question
            )

            # ------------------------------------------------
            # Answer
            # ------------------------------------------------

            st.subheader(
                "💡 Answer"
            )

            st.write(
                result.get(
                    "answer",
                    "No answer returned.",
                )
            )

            # ------------------------------------------------
            # Evidence
            # ------------------------------------------------

            st.subheader(
                "🔗 Graph Evidence"
            )

            evidence = result.get(
                "evidence",
                [],
            )

            if evidence:

                for item in evidence:

                    st.write(
                        f"**{item.get('source')}** "
                        f"→ "
                        f"**{item.get('relationship')}** "
                        f"→ "
                        f"**{item.get('target')}**"
                    )

            else:

                st.info(
                    "No graph evidence found."
                )

            # ------------------------------------------------
            # Retrieved Context
            # ------------------------------------------------

            with st.expander(
                "View Retrieved Graph Context"
            ):

                st.json(
                    result.get(
                        "retrieved_context",
                        [],
                    )
                )

        except Exception as e:

            st.error(
                f"GraphRAG request failed: {e}"
            )
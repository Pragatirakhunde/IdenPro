import streamlit as st

st.set_page_config(
    page_title="DataMind AI",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 DataMind AI")

st.markdown("""
Welcome to **DataMind AI**

An AI-powered Data Intelligence Platform.

### Features

- 📂 Upload CSV / Excel / JSON / XML
- 🗄 Connect Live Databases
- 📊 Data Profiling
- 🔍 Relationship Discovery
- 🕸 Knowledge Graph
- 🤖 AI Chat
- 📑 Documentation Generation

Use the sidebar to navigate.
""")

if "access_token" not in st.session_state:
    st.warning("Please login from the Login page.")
else:
    st.success("Logged In Successfully!")
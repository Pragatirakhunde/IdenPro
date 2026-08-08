import pandas as pd
import plotly.express as px
import streamlit as st

from components.metrics import render_metrics
from components.navbar import render_navbar
from components.sidebar import render_sidebar
from utils import api

st.set_page_config(page_title="Reports · DataMind AI", page_icon="📈", layout="wide")

api.require_login()
render_sidebar()
render_navbar("Reports", "Summary reports across all projects and data sources.", "📈")

try:
    project_data = api.list_projects()
    projects = project_data.get("projects", [])
except api.ApiError as e:
    st.error(f"Could not load projects: {e.detail}")
    projects = []

if not projects:
    st.info("No projects yet. Create one from the Dashboard.")
    st.stop()

all_sources = []
for p in projects:
    try:
        ds = api.list_project_datasources(p["id"]).get("data_sources", [])
    except api.ApiError:
        ds = []
    for s in ds:
        s = dict(s)
        s["project_name"] = p["name"]
        all_sources.append(s)

render_metrics([
    {"label": "Projects", "value": len(projects)},
    {"label": "Data Sources", "value": len(all_sources)},
    {"label": "Ready", "value": sum(1 for s in all_sources if s.get("status") == "READY")},
    {"label": "Processing", "value": sum(1 for s in all_sources if s.get("status") == "PROCESSING")},
])

st.divider()

if not all_sources:
    st.info("No data sources across your projects yet.")
    st.stop()

df = pd.DataFrame(all_sources)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Data Sources by Type")
    type_counts = df["source_type"].value_counts().reset_index()
    type_counts.columns = ["Type", "Count"]
    fig = px.pie(type_counts, names="Type", values="Count", hole=0.5)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Data Sources by Status")
    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    fig2 = px.bar(status_counts, x="Status", y="Count", color="Status")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
st.subheader("📊 Data Sources by Project")

per_project = df.groupby("project_name").size().reset_index(name="Data Sources")
fig3 = px.bar(per_project, x="project_name", y="Data Sources", labels={"project_name": "Project"})
st.plotly_chart(fig3, use_container_width=True)

st.divider()
st.subheader("📋 Full Data Source Table")

display_cols = ["project_name", "name", "source_type", "source_format", "status", "total_tables", "total_columns", "total_relationships"]
display_cols = [c for c in display_cols if c in df.columns]
st.dataframe(df[display_cols], use_container_width=True)

csv = df[display_cols].to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download report as CSV", data=csv, file_name="datamind_report.csv", mime="text/csv")
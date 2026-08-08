import streamlit as st

from services.api_client import (
    get_projects,
    get_project_datasources,
    upload_file,
    connect_database,
    delete_datasource,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Data Sources",
    page_icon="🗄️",
    layout="wide",
)


# ============================================================
# AUTHENTICATION
# ============================================================

if "access_token" not in st.session_state:

    st.warning(
        "Please login first."
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.title("🗄️ Data Sources")

st.write(
    "Upload files or connect external databases "
    "to build your enterprise knowledge base."
)


# ============================================================
# LOAD PROJECTS
# ============================================================

try:

    project_response = get_projects()

    projects = project_response.get(
        "projects",
        []
    )

except Exception as e:

    st.error(
        f"Unable to load projects: {e}"
    )

    st.stop()


if not projects:

    st.warning(
        "No projects found."
    )

    st.info(
        "Create a project first before adding a data source."
    )

    st.stop()


# ============================================================
# PROJECT SELECTION
# ============================================================

st.subheader("📁 Select Project")


project_options = {}

for project in projects:

    project_id = str(
        project.get("id")
    )

    project_name = project.get(
        "name",
        project_id,
    )

    project_options[
        f"{project_name} ({project_id})"
    ] = project_id


selected_project_label = st.selectbox(
    "Project",
    list(project_options.keys()),
)


selected_project_id = project_options[
    selected_project_label
]


# ============================================================
# DATA SOURCE TYPE
# ============================================================

st.divider()

source_type = st.radio(
    "Choose data source type",
    [
        "📂 File",
        "🗄️ Database",
    ],
    horizontal=True,
)


# ============================================================
# FILE UPLOAD
# ============================================================

if source_type == "📂 File":

    st.subheader(
        "📂 Upload File"
    )

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=[
            "csv",
            "xlsx",
            "xls",
            "json",
            "parquet",
            "xml",
        ],
    )

    if uploaded_file:

        st.success(
            f"Selected: {uploaded_file.name}"
        )

        file_name = st.text_input(
            "Data source name",
            value=uploaded_file.name,
        )

        description = st.text_area(
            "Description",
            placeholder=(
                "Optional description "
                "of this data source."
            ),
        )

        if st.button(
            "🚀 Upload File",
            type="primary",
            use_container_width=True,
        ):

            if not file_name.strip():

                st.error(
                    "Please provide a data source name."
                )

            else:

                try:

                    with st.spinner(
                        "Uploading file..."
                    ):

                        result = upload_file(
                            project_id=selected_project_id,
                            name=file_name,
                            uploaded_file=uploaded_file,
                            description=description,
                        )

                    st.success(
                        "File uploaded successfully!"
                    )

                    st.json(result)

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"File upload failed: {e}"
                    )


# ============================================================
# DATABASE CONNECTION
# ============================================================

else:

    st.subheader(
        "🗄️ Connect Database"
    )

    db_type = st.selectbox(
        "Database Type",
        [
            "POSTGRESQL",
            "MYSQL",
            "SQLITE",
            "SQLSERVER",
            "ORACLE",
        ],
    )

    connection_name = st.text_input(
        "Connection Name",
        placeholder="Production Database",
    )

    host = st.text_input(
        "Host",
        placeholder="localhost",
    )

    port = st.number_input(
        "Port",
        min_value=1,
        max_value=65535,
        value=5432 if db_type == "POSTGRESQL" else 3306,
    )

    database_name = st.text_input(
        "Database Name",
        placeholder="my_database",
    )

    username = st.text_input(
        "Username",
    )

    password = st.text_input(
        "Password",
        type="password",
    )

    ssl_enabled = st.checkbox(
        "Enable SSL"
    )

    description = st.text_area(
        "Description",
        placeholder=(
            "Optional description "
            "of this database."
        ),
    )

    if st.button(
        "🔌 Connect Database",
        type="primary",
        use_container_width=True,
    ):

        if not connection_name.strip():

            st.error(
                "Connection name is required."
            )

        elif not host.strip():

            st.error(
                "Host is required."
            )

        elif not database_name.strip():

            st.error(
                "Database name is required."
            )

        elif not username.strip():

            st.error(
                "Username is required."
            )

        elif not password:

            st.error(
                "Password is required."
            )

        else:

            try:

                with st.spinner(
                    "Testing database connection..."
                ):

                    result = connect_database(
                        project_id=selected_project_id,
                        connection_name=connection_name,
                        db_type=db_type,
                        username=username,
                        password=password,
                        host=host,
                        port=int(port),
                        database_name=database_name,
                        ssl_enabled=ssl_enabled,
                        description=description,
                    )

                st.success(
                    "Database connected successfully!"
                )

                st.json(result)

                st.rerun()

            except Exception as e:

                st.error(
                    f"Database connection failed: {e}"
                )


# ============================================================
# EXISTING DATA SOURCES
# ============================================================

st.divider()

st.subheader(
    "📋 Existing Data Sources"
)


try:

    response = get_project_datasources(
        selected_project_id
    )

    datasources = response.get(
        "data_sources",
        []
    )

except Exception as e:

    st.error(
        f"Unable to load data sources: {e}"
    )

    datasources = []


if not datasources:

    st.info(
        "No data sources added to this project yet."
    )

else:

    for datasource in datasources:

        datasource_id = datasource.get(
            "id"
        )

        name = datasource.get(
            "name",
            "Unnamed",
        )

        source_type = datasource.get(
            "source_type",
            "UNKNOWN",
        )

        source_format = datasource.get(
            "source_format",
            "UNKNOWN",
        )

        status = datasource.get(
            "status",
            "UNKNOWN",
        )

        with st.expander(
            f"📌 {name}"
        ):

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Type",
                    source_type,
                )

            with col2:

                st.metric(
                    "Format",
                    source_format,
                )

            with col3:

                st.metric(
                    "Status",
                    status,
                )

            st.write(
                f"**ID:** `{datasource_id}`"
            )

            if datasource.get(
                "description"
            ):

                st.write(
                    datasource["description"]
                )

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    f"Tables: "
                    f"{datasource.get('total_tables', 0)}"
                )

            with col2:

                st.write(
                    f"Columns: "
                    f"{datasource.get('total_columns', 0)}"
                )

            if st.button(
                "🗑️ Delete",
                key=f"delete_{datasource_id}",
            ):

                try:

                    delete_datasource(
                        datasource_id
                    )

                    st.success(
                        "Data source deleted."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Delete failed: {e}"
                    )
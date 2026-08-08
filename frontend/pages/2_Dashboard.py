import requests
import streamlit as st


# ============================================================
# BACKEND
# ============================================================

API_URL = "http://127.0.0.1:8000"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
)


# ============================================================
# AUTHENTICATION
# ============================================================

if "access_token" not in st.session_state:

    st.warning("Please Login First.")

    if st.button("Go to Login"):

        st.switch_page(
            "pages/1_Login.py"
        )

    st.stop()


TOKEN = st.session_state["access_token"]

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}


# ============================================================
# GET CURRENT USER
# ============================================================

try:

    response = requests.get(
        f"{API_URL}/api/auth/me",
        headers=HEADERS,
        timeout=30,
    )

    if response.status_code != 200:

        st.error("Session expired. Please login again.")

        st.session_state.clear()

        st.stop()

    user = response.json()

except Exception as e:

    st.error(
        f"Unable to connect to backend: {e}"
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.title("📊 Dashboard")

st.write(
    f"Welcome **{user.get('username', 'User')}**!"
)

st.write(
    "Create a project first, then add files or "
    "connect databases to build your enterprise knowledge base."
)


# ============================================================
# CREATE PROJECT
# ============================================================

st.divider()

st.subheader("➕ Create New Project")

with st.form("create_project_form"):

    project_name = st.text_input(
        "Project Name",
        placeholder="Example: Customer Data Analysis",
    )

    project_description = st.text_area(
        "Project Description",
        placeholder=(
            "Describe what this project is about..."
        ),
    )

    create_project = st.form_submit_button(
        "Create Project",
        use_container_width=True,
    )


if create_project:

    if not project_name.strip():

        st.error(
            "Project name is required."
        )

    else:

        payload = {
            "name": project_name.strip(),
            "description": (
                project_description.strip()
                if project_description
                else None
            ),
        }

        try:

            response = requests.post(
                f"{API_URL}/api/projects",
                json=payload,
                headers=HEADERS,
                timeout=30,
            )

            if response.status_code in (
                200,
                201,
            ):

                project = response.json()

                st.success(
                    f"Project '{project_name}' created successfully!"
                )

                st.rerun()

            else:

                try:
                    error_detail = response.json().get(
                        "detail",
                        response.text,
                    )

                except Exception:

                    error_detail = response.text

                st.error(
                    f"Could not create project: "
                    f"{error_detail}"
                )

        except Exception as e:

            st.error(
                f"Backend connection failed: {e}"
            )


# ============================================================
# PROJECTS
# ============================================================

st.divider()

st.subheader("📁 Your Projects")


try:

    response = requests.get(
        f"{API_URL}/api/projects",
        headers=HEADERS,
        timeout=30,
    )

    if response.status_code != 200:

        try:

            error_detail = response.json().get(
                "detail",
                response.text,
            )

        except Exception:

            error_detail = response.text

        st.error(
            f"Unable to load projects: "
            f"{error_detail}"
        )

    else:

        result = response.json()

        projects = result.get(
            "projects",
            [],
        )

        if not projects:

            st.info(
                "No projects found. "
                "Create your first project above."
            )

        else:

            st.write(
                f"Total projects: **{len(projects)}**"
            )

            # ------------------------------------------------
            # Display projects
            # ------------------------------------------------

            for project in projects:

                project_id = project.get(
                    "id"
                )

                project_name = project.get(
                    "name",
                    "Unnamed Project",
                )

                project_description = project.get(
                    "description",
                    "",
                )

                project_status = project.get(
                    "status",
                    "ACTIVE",
                )

                with st.container(
                    border=True
                ):

                    col1, col2, col3 = st.columns(
                        [5, 2, 2]
                    )

                    with col1:

                        st.subheader(
                            f"📂 {project_name}"
                        )

                        if project_description:

                            st.write(
                                project_description
                            )

                        st.caption(
                            f"Project ID: {project_id}"
                        )

                    with col2:

                        st.write(
                            "**Status**"
                        )

                        st.info(
                            str(project_status)
                        )

                    with col3:

                        if st.button(
                            "Add Data Source",
                            key=f"datasource_{project_id}",
                            use_container_width=True,
                        ):

                            st.session_state[
                                "selected_project_id"
                            ] = str(project_id)

                            st.switch_page(
                                "pages/2_Data_Source.py"
                            )


except Exception as e:

    st.error(
        f"Unable to load projects: {e}"
    )


# ============================================================
# QUICK ACTIONS
# ============================================================

st.divider()

st.subheader("🚀 Quick Actions")

col1, col2, col3 = st.columns(3)


with col1:

    if st.button(
        "📂 Data Sources",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/2_Data_Source.py"
        )


with col2:

    if st.button(
        "🕸️ Knowledge Graph",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/4_Knowledge_Graph.py"
        )


with col3:

    if st.button(
        "🤖 AI Chat",
        use_container_width=True,
    ):

        st.switch_page(
            "pages/7_AI_Chat.py"
        )


# ============================================================
# CURRENT USER
# ============================================================

st.divider()

with st.expander("👤 Current User"):

    st.json(user)


# ============================================================
# LOGOUT
# ============================================================

st.divider()

if st.button(
    "Logout",
    use_container_width=True,
):

    st.session_state.clear()

    st.switch_page(
        "pages/1_Login.py"
    )
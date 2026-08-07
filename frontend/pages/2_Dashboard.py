import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/api/auth"

if "access_token" not in st.session_state:
    st.warning("Please Login First.")
    st.stop()

headers = {
    "Authorization":
    f"Bearer {st.session_state['access_token']}"
}

response = requests.get(
    f"{API_URL}/me",
    headers=headers
)

if response.status_code != 200:

    st.error("Session Expired.")

    st.session_state.clear()

    st.stop()

user = response.json()

st.set_page_config(
    page_title="Dashboard",
    layout="wide"
)

st.title("📊 Dashboard")

st.success(
    f"Welcome {user['username']}"
)

col1, col2 = st.columns(2)

with col1:

    st.info("📂 Upload Files")

    if st.button("Go to Upload Module"):
        st.write("Coming Soon...")

with col2:

    st.info("🗄 Connect Database")

    if st.button("Go to Database Module"):
        st.write("Coming Soon...")

st.divider()

st.subheader("Current User")

st.json(user)

if st.button("Logout"):

    st.session_state.clear()

    st.switch_page("pages/1_Login.py")
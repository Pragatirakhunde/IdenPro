import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/api/auth"

st.set_page_config(page_title="Login")

st.title("🔐 Login")

tab1, tab2 = st.tabs(["Login", "Register"])

# --------------------------
# Login
# --------------------------
with tab1:

    username = st.text_input(
        "Username",
        key="login_username"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="login_password"
    )

    if st.button("Login"):

        payload = {
            "username": username,
            "password": password
        }

        response = requests.post(
            f"{API_URL}/login",
            json=payload
        )

        if response.status_code == 200:

            data = response.json()

            st.session_state["access_token"] = data["access_token"]

            st.success("Login Successful!")

            st.switch_page("pages/2_Dashboard.py")

        else:

            st.error(response.json()["detail"])

# --------------------------
# Register
# --------------------------

with tab2:

    username = st.text_input(
        "Username",
        key="register_username"
    )

    email = st.text_input(
        "Email",
        key="register_email"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="register_password"
    )

    if st.button("Register"):

        payload = {
            "username": username,
            "email": email,
            "password": password
        }

        response = requests.post(
            f"{API_URL}/register",
            json=payload
        )

        if response.status_code == 201:

            st.success(
                "Registration Successful.\nPlease Login."
            )

        else:

            st.error(response.json()["detail"])
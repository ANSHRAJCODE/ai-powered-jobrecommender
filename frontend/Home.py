import streamlit as st
import requests

# --- Page Configuration ---
st.set_page_config(
    page_title="Welcome - AI Job Recommender",
    page_icon="🤖",
    layout="centered"
)

# --- API URL ---
# This points to your locally running FastAPI backend
API_URL = "http://127.0.0.1:8000"

# --- Main Page Content ---
st.title("Welcome to the 🤖 AI Job Recommender")
st.markdown("An exceptional, AI-powered platform to find your perfect job match.")

# --- User Authentication ---
# Check if the user is already logged in
if 'access_token' in st.session_state:
    st.success(f"You are logged in as **{st.session_state.username}**!")
    if st.button("Go to Your Profile"):
        st.switch_page("pages/Profile.py")
else:
    st.info("Please log in or sign up to get started.")
    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    # --- Login Form ---
    with login_tab:
        st.header("Login")
        login_username = st.text_input("Username", key="login_user")
        login_password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if login_username and login_password:
                try:
                    response = requests.post(
                        f"{API_URL}/auth/token",
                        data={"username": login_username, "password": login_password}
                    )
                    if response.status_code == 200:
                        st.session_state.access_token = response.json().get("access_token")
                        st.session_state.username = login_username
                        st.rerun() # Rerun the script to show the logged-in state
                    else:
                        st.error(f"Login failed: {response.json().get('detail')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Could not connect to the backend server. Is it running?")
            else:
                st.warning("Please enter both username and password.")

    # --- Sign Up Form ---
    with signup_tab:
        st.header("Sign Up")
        signup_username = st.text_input("Choose a Username", key="signup_user")
        signup_password = st.text_input("Choose a Password", type="password", key="signup_pass")
        if st.button("Sign Up"):
            if signup_username and signup_password:
                try:
                    response = requests.post(
                        f"{API_URL}/auth/register",
                        json={"username": signup_username, "password": signup_password}
                    )
                    if response.status_code == 200:
                        st.success("Account created successfully! Please log in to continue.")
                    else:
                        st.error(f"Sign-up failed: {response.json().get('detail')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Could not connect to the backend server.")
            else:
                st.warning("Please choose a username and password.")
import streamlit as st
import requests

st.set_page_config(page_title="Saved Jobs", page_icon="❤️", layout="wide")

if 'access_token' not in st.session_state:
    st.warning("You must be logged in."); st.page_link("Home.py", label="Go to Login"); st.stop()

API_URL = "http://127.0.0.1:8000"
HEADERS = {"Authorization": f"Bearer {st.session_state.access_token}"}
st.title("❤️ Your Saved Jobs")

try:
    response = requests.get(f"{API_URL}/jobs/saved", headers=HEADERS)
    response.raise_for_status()
    saved_jobs = response.json()

    if not saved_jobs:
        st.info("You haven't saved any jobs yet.")
    else:
        for job in saved_jobs:
            with st.container(border=True):
                st.subheader(job['title'])
                score_percentage = int(float(job['score']) * 100)
                st.progress(score_percentage, text=f"Match Score: {score_percentage}%")
                col1, col2 = st.columns(2); 
                with col1: st.write(f"**Company:** {job.get('company', 'N/A')}")
                with col2: st.write(f"**Location:** {job.get('location', 'N/A')}")
                with st.expander("View Details"):
                    st.info(f"**AI Explanation:** {job['explanation']}")
                    st.write("**Full Job Description:**", job['description'])
except requests.exceptions.RequestException as e:
    st.error(f"Error fetching saved jobs: {e}")
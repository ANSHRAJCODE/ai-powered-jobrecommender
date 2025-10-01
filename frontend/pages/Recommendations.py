import streamlit as st
import requests

st.set_page_config(page_title="Your Recommendations", page_icon="🎯", layout="wide")

if 'access_token' not in st.session_state:
    st.warning("You must be logged in to access this page.")
    st.page_link("Home.py", label="Go to Login Page")
    st.stop()

API_URL = "http://127.0.0.1:8000"
HEADERS = {"Authorization": f"Bearer {st.session_state.access_token}"}

st.title("🎯 Your Personalized Job Recommendations")

if st.button("Get My Job Recommendations"):
    with st.spinner("Analyzing your profile and finding the best job matches..."):
        try:
            response = requests.post(f"{API_URL}/recommendations", headers=HEADERS)
            response.raise_for_status()
            st.session_state.recommendations = response.json().get("jobs", [])
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching recommendations: {e}")

if 'recommendations' in st.session_state and st.session_state.recommendations:
    st.header("Top Job Matches for You")
    for i, job in enumerate(st.session_state.recommendations):
        with st.container(border=True):
            st.subheader(job['title'])
            score_percentage = int(job['score'] * 100)
            st.progress(score_percentage, text=f"Match Score: {score_percentage}%")
            
            col1, col2 = st.columns(2)
            with col1: st.write(f"**Company:** {job.get('company', 'N/A')}")
            with col2: st.write(f"**Location:** {job.get('location', 'N/A')}")

            # --- ADD THIS 'SAVE JOB' BUTTON ---
            if st.button("❤️ Save Job", key=f"save_{i}"):
                try:
                    response = requests.post(f"{API_URL}/jobs/save", json=job, headers=HEADERS)
                    response.raise_for_status()
                    st.toast("Job saved successfully!")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error saving job: {e}")

            with st.expander("Why is this a good match? (View Details)"):
                st.info(f"**AI Explanation:** {job['explanation']}")
                st.write("**Full Job Description:**", job['description'])
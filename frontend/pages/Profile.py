import streamlit as st
import requests

# --- Page Configuration ---
st.set_page_config(
    page_title="Your Profile - AI Job Recommender",
    page_icon="👤",
    layout="wide"
)

# --- Authentication Check ---
# This ensures that only logged-in users can access this page.
if 'access_token' not in st.session_state:
    st.warning("You must be logged in to access this page.")
    st.page_link("Home.py", label="Go to Login Page")
    st.stop()
# --- End of Check ---

# --- API URL and Headers ---
API_URL = "http://127.0.0.1:8000"
HEADERS = {"Authorization": f"Bearer {st.session_state.access_token}"}

# --- Page Content ---
st.title(f"👤 Welcome to Your Profile, {st.session_state.username}!")
st.markdown("Here, you can manage your resume. Upload your latest resume to get personalized job recommendations based on your unique skills and experience.")
st.markdown("---")

# --- Resume Upload Section ---
st.header("Upload Your Resume")

# Initialize resume status in session state if it doesn't exist
if 'resume_status' not in st.session_state:
    st.session_state.resume_status = "No resume uploaded yet."

# Display the current status of the resume
st.info(f"**Current Status:** {st.session_state.resume_status}")

uploaded_file = st.file_uploader(
    "Choose your resume PDF. This will overwrite any previously uploaded resume.",
    type="pdf"
)

if st.button("Process Resume"):
    if uploaded_file is not None:
        with st.spinner('Reading and processing your resume... This may take a moment.'):
            files = {'file': (uploaded_file.name, uploaded_file, 'application/pdf')}
            try:
                response = requests.post(f"{API_URL}/resumes/upload", files=files, headers=HEADERS)
                response.raise_for_status() # Raise an error for bad status codes (4xx or 5xx)
                
                # Update the status and rerun to show the new state
                st.session_state.resume_status = "Resume processed successfully! You can now get recommendations."
                st.rerun()

            except requests.exceptions.RequestException as e:
                st.error(f"Error processing resume: {e}. Is the backend server running?")
    else:
        st.warning("Please upload a resume file first.")

st.markdown("---")

# --- Navigation ---
# This button is disabled until a resume has been successfully processed.
st.header("Get Your Recommendations")
if st.button("Go to Recommendations Page", disabled=(st.session_state.resume_status != "Resume processed successfully! You can now get recommendations.")):
    st.switch_page("pages/Recommendations.py")
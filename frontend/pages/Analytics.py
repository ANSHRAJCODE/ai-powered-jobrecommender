import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Analytics", page_icon="📈", layout="wide")

if 'access_token' not in st.session_state:
    st.warning("You must be logged in."); st.page_link("Home.py", label="Go to Login"); st.stop()

API_URL = "http://127.0.0.1:8000"
HEADERS = {"Authorization": f"Bearer {st.session_state.access_token}"}
st.title(f"📈 Your Analytics Dashboard")

@st.cache_data
def fetch_data():
    try:
        response = requests.get(f"{API_URL}/jobs/saved", headers=HEADERS)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except:
        return pd.DataFrame()

df = fetch_data()

if df.empty:
    st.info("No saved jobs found. Save some jobs to see your analytics.")
else:
    df['score'] = pd.to_numeric(df['score'])
    st.header("Your Saved Job Analytics")
    
    col1, col2 = st.columns(2)
    with col1: st.metric("Total Jobs Saved", len(df))
    with col2: st.metric("Average Match Score", f"{df['score'].mean():.2%}")

    fig_pie = px.pie(df, names='company', title='Saved Jobs by Company')
    st.plotly_chart(fig_pie, use_container_width=True)
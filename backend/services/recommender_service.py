import os
import joblib
import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from dotenv import load_dotenv

import models

load_dotenv()

# --- 1. Load All Artifacts on Startup ---
try:
    print("Loading SBERT model...")
    sbert_model_path = os.path.join('data', 'minilm_model')
    sbert_model = SentenceTransformer(sbert_model_path)
    print("✅ SBERT model loaded.")

    print("Loading job data and embeddings...")
    jobs_df_path = os.path.join('data', 'jobs_df.pkl')
    job_embeddings_path = os.path.join('data', 'job_embeddings.pkl')
    jobs_df = joblib.load(jobs_df_path)
    job_embeddings = joblib.load(job_embeddings_path)
    print("✅ Job data and embeddings loaded.")

    print("Initializing LLM for explanations...")
    llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", temperature=0.3)
    print("✅ LLM initialized.")

except FileNotFoundError:
    print("❌ Error: One or more data files not found. Ensure the 'data' folder is in the 'backend' directory.")
    sbert_model, jobs_df, job_embeddings, llm = None, None, None, None

# --- 2. Core Recommendation Logic ---
def get_recommendations(user_text: str, top_n: int = 10):
    """Generates a base list of recommendations with scores."""
    if sbert_model is None or jobs_df is None or job_embeddings is None:
        return pd.DataFrame()

    user_embedding = sbert_model.encode([user_text])
    similarities = cosine_similarity(user_embedding, job_embeddings)[0]
    top_n_indices = np.argsort(similarities)[-top_n:][::-1]

    recommended_jobs = jobs_df.iloc[top_n_indices].copy()
    recommended_jobs['score'] = similarities[top_n_indices]
    
    return recommended_jobs

# --- 3. Explanation Generation Logic ---
async def get_explanation(user_text: str, job_title: str, job_description: str):
    """Uses an LLM to explain why a job is a good match."""
    if llm is None:
        return "Explanation model is not available."

    prompt_template = ChatPromptTemplate.from_template(
        """
        You are an expert career coach. Explain in one concise paragraph why the following job is a good match for a candidate with the skills and experience listed below.
        Focus on highlighting the specific keywords and concepts that overlap.

        Candidate's Profile:
        {user_text}

        Job Title: {job_title}
        Job Description: {job_description}

        Explanation:
        """
    )
    explanation_chain = prompt_template | llm | StrOutputParser()
    
    explanation = await explanation_chain.ainvoke({
        "user_text": user_text,
        "job_title": job_title,
        "job_description": job_description
    })
    return explanation

# --- 4. Main Service Function for Explained Recommendations ---
async def get_explained_recommendations(db: Session, user: models.User, top_n: int = 10):
    """The main function called by the API to get recommendations with explanations."""
    user_resume = db.query(models.Resume).filter(models.Resume.user_id == user.id).first()
    if not user_resume or not user_resume.raw_text:
        raise HTTPException(status_code=404, detail="No resume found. Please upload one on the Profile page.")

    # Step 1: Get base recommendations
    recommended_jobs_df = get_recommendations(user_resume.raw_text, top_n)

    # Step 2: Generate explanations for each recommendation
    explained_jobs = []
    for _, row in recommended_jobs_df.iterrows():
        explanation_text = await get_explanation(
            user_text=user_resume.raw_text,
            job_title=row['title'],
            job_description=row['description']
        )
        job_data = {
            "title": row['title'],
            "description": row['description'],
            "score": row['score'],
            "explanation": explanation_text,
            "company": row.get('company'),
            "location": row.get('location')
        }
        explained_jobs.append(job_data)
        
    return {"jobs": explained_jobs}
# import os
# import joblib
# import numpy as np
# import pandas as pd
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity
# from dotenv import load_dotenv

# # --- NEW: Imports for Explainable AI (XAI) ---
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.prompts import ChatPromptTemplate
# from langchain.schema.output_parser import StrOutputParser

# # --- 1. Application and Model Initialization ---
# load_dotenv() # Load environment variables from .env file

# app = FastAPI(
#     title="AI Job Recommender API",
#     description="Recommends jobs and explains why they are a good fit.",
#     version="2.0.0" # Updated version
# )

# # --- Load Artifacts ---
# try:
#     print("Loading artifacts...")
#     model_path = os.path.join('data', 'minilm_model')
#     jobs_df_path = os.path.join('data', 'jobs_df.pkl')
#     job_embeddings_path = os.path.join('data', 'job_embeddings.pkl')

#     sbert_model = SentenceTransformer(model_path)
#     jobs_df = joblib.load(jobs_df_path)
#     job_embeddings = joblib.load(job_embeddings_path)
    
#     # --- NEW: Initialize the LLM for explanations ---
#     # llm = ChatGoogleGenerativeAI(model="models/gemini-pro", temperature=0.3)
#     # llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-pro", temperature=0.3)
#     llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", temperature=0.3)
#     print("✅ Artifacts and LLM loaded successfully!")
# except Exception as e:
#     print(f"Error loading artifacts: {e}")
#     sbert_model, jobs_df, job_embeddings, llm = None, None, None, None

# # --- 2. Pydantic Models for API ---
# class RecommendRequest(BaseModel):
#     text: str
#     top_n: int = 10

# class Job(BaseModel):
#     title: str
#     description: str
#     company: str | None = None
#     location: str | None = None
#     score: float
#     explanation: str | None = None # --- NEW: Field for the explanation ---

# class RecommendResponse(BaseModel):
#     jobs: list[Job]

# # --- 3. LangChain Prompt for XAI ---
# explanation_prompt = ChatPromptTemplate.from_template(
#     "You are an expert career advisor. Based on the user's skills and the job description below, "
#     "write a short, encouraging, and professional explanation (2-3 sentences) explaining why this job is a strong match. "
#     "Highlight the key overlapping skills.\n\n"
#     "--- USER'S SKILLS/RESUME ---\n{user_text}\n\n"
#     "--- JOB DESCRIPTION ---\n{job_description}\n\n"
#     "--- EXPLANATION ---"
# )

# explanation_chain = explanation_prompt | llm | StrOutputParser()

# # --- 4. API Endpoints ---
# @app.get("/")
# def read_root():
#     return {"status": "Job Recommender API is running"}

# @app.post("/recommend", response_model=RecommendResponse)
# def recommend_jobs(request: RecommendRequest):
#     if sbert_model is None or jobs_df is None or job_embeddings is None or llm is None:
#         raise HTTPException(status_code=503, detail="Model and data not loaded.")

#     user_embedding = sbert_model.encode([request.text])
#     similarities = cosine_similarity(user_embedding, job_embeddings)[0]
#     top_n_indices = np.argsort(similarities)[-request.top_n:][::-1]
    
#     recommended_jobs_df = jobs_df.iloc[top_n_indices].copy()
#     recommended_jobs_df['score'] = similarities[top_n_indices]

#     recommended_jobs = []
#     for _, row in recommended_jobs_df.iterrows():
#         # --- NEW: Generate explanation for each job ---
#         try:
#             explanation = explanation_chain.invoke({
#                 "user_text": request.text,
#                 "job_description": row['combined_text'] # Use the full text for better context
#             })
#         except Exception:
#             # If the explanation fails for any reason, provide a default one
#             explanation = "This job is a strong match based on the skills provided."

#         recommended_jobs.append(Job(
#             title=row['title'],
#             description=row['description'],
#             company=row.get('company'),
#             location=row.get('location'),
#             score=row['score'],
#             explanation=explanation # Add the generated explanation
#         ))
        
#     return RecommendResponse(jobs=recommended_jobs)
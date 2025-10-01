from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Annotated
from pydantic import BaseModel

# Project-specific imports
import database, models
from services import auth_service, recommender_service, resume_service

# --- 1. App and Database Initialization ---
try:
    models.Base.metadata.create_all(bind=database.engine)
    print("✅ Database tables created successfully (if they didn't exist).")
except Exception as e:
    print(f"❌ Error creating database tables: {e}")

app = FastAPI(
    title="AI Job Recommender API",
    description="An advanced API for job recommendations and career insights.",
    version="2.0.0"
)

# --- 2. Pydantic Models for API Data Validation ---
class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class Job(BaseModel):
    title: str
    description: str
    score: float
    explanation: str
    company: str | None = None
    location: str | None = None

class RecommendResponse(BaseModel):
    jobs: List[Job]

class SaveJobRequest(BaseModel):
    title: str
    description: str
    company: str | None = None
    location: str | None = None
    score: float
    explanation: str

class SavedJobResponse(Job):
    id: int
    class Config:
        from_attributes = True

# --- 3. API Endpoints (Routers) ---

@app.get("/")
def read_root():
    return {"status": "AI Job Recommender API is running"}

# --- Authentication Endpoints ---
@app.post("/auth/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(database.get_db)):
    return auth_service.register_new_user(db=db, username=user.username, password=user.password)

@app.post("/auth/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(database.get_db)):
    return auth_service.login_user(db=db, username=form_data.username, password=form_data.password)

# --- Core Recommender Endpoints ---
@app.post("/recommendations", response_model=RecommendResponse)
async def get_job_recommendations(current_user: models.User = Depends(auth_service.get_current_user), db: Session = Depends(database.get_db)):
    return await recommender_service.get_explained_recommendations(db=db, user=current_user)

@app.post("/resumes/upload")
async def upload_resume(file: UploadFile = File(...), current_user: models.User = Depends(auth_service.get_current_user), db: Session = Depends(database.get_db)):
    file_content = await file.read()
    return resume_service.parse_and_embed_resume(
        file_content=file_content,
        user=current_user,
        db=db,
        sbert_model=recommender_service.sbert_model
    )

@app.post("/jobs/save")
def save_job(job_data: SaveJobRequest, current_user: models.User = Depends(auth_service.get_current_user), db: Session = Depends(database.get_db)):
    new_saved_job = models.SavedJob(
        user_id=current_user.id, title=job_data.title, description=job_data.description,
        company=job_data.company, location=job_data.location,
        score=str(job_data.score), explanation=job_data.explanation
    )
    db.add(new_saved_job)
    db.commit()
    db.refresh(new_saved_job)
    return {"message": "Job saved successfully!"}

@app.get("/jobs/saved", response_model=List[SavedJobResponse])
def get_saved_jobs(current_user: models.User = Depends(auth_service.get_current_user), db: Session = Depends(database.get_db)):
    saved_jobs = db.query(models.SavedJob).filter(models.SavedJob.user_id == current_user.id).order_by(models.SavedJob.id.desc()).all()
    # Convert score back to float for the response
    for job in saved_jobs:
        job.score = float(job.score)
    return saved_jobs

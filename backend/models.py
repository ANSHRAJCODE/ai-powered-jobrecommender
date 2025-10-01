from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.dialects.postgresql import ARRAY

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    resume = relationship("Resume", back_populates="owner", uselist=False)

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    raw_text = Column(Text)
    embedding = Column(ARRAY(Float))
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="resume")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    embedding = Column(ARRAY(Float))
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)

# --- ADD THIS NEW TABLE ---
class SavedJob(Base):
    __tablename__ = "saved_jobs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(Text)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    score = Column(String) # Storing score as string
    explanation = Column(Text)
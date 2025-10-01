import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Modify the URL for SQLAlchemy if it's a Supabase URL
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

# Add SSL requirement for cloud databases
if "supabase" in str(DATABASE_URL):
    DATABASE_URL = f"{DATABASE_URL}?sslmode=require"

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    print("✅ Database engine created successfully.")
except Exception as e:
    print(f"❌ Error creating database engine: {e}")

def get_db():
    """Dependency to get a DB session for a request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
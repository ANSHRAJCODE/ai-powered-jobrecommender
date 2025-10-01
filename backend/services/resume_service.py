import io
import pdfplumber
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
import models

def parse_and_embed_resume(file_content: bytes, user: models.User, db: Session, sbert_model: SentenceTransformer):
    """
    Parses text from a PDF, generates an embedding, and saves it to the user's profile.
    """
    try:
        # Use an in-memory buffer to read the PDF content
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            raw_text = "".join(page.extract_text() for page in pdf.pages if page.extract_text())

        if not raw_text:
            raise ValueError("Could not extract text from the PDF.")

        # Generate the embedding for the resume text
        embedding = sbert_model.encode(raw_text).tolist()

        # Check if the user already has a resume, if so update it, otherwise create a new one
        existing_resume = db.query(models.Resume).filter(models.Resume.user_id == user.id).first()
        if existing_resume:
            existing_resume.raw_text = raw_text
            existing_resume.embedding = embedding
        else:
            new_resume = models.Resume(
                raw_text=raw_text,
                embedding=embedding,
                user_id=user.id
            )
            db.add(new_resume)
        
        db.commit()
        return {"status": "success", "message": "Resume processed and saved."}

    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
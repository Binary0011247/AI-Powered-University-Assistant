import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models.document import Document
from app.services.search.ingestor import doc_ingestor
from app.services.search.semantic_search import search_engine

router = APIRouter(prefix="/api/ingest", tags=["Document Ingestion"])

# Ensure the physical storage folder exists
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...), 
    faculty_email: str = "faculty@university.edu", # Optional: pass from frontend
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid format. Only PDFs allowed.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # 1. Physical Storage: Save the original file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 2. Vector Storage: Update the FAISS AI Brain
        chunks = doc_ingestor.process_pdf(file_path)
        count = doc_ingestor.update_vector_db(chunks)
        
        # Refresh the search engine so it can immediately find the new data
        search_engine.__init__()

        # 3. Relational Storage: Log the upload in PostgreSQL
        new_doc = Document(
            title=file.filename,
            document_type="Academic Policy/Syllabus",
            content_summary=f"Ingested {count} semantic chunks",
            uploaded_by=faculty_email
        )
        db.add(new_doc)
        db.commit()

        return {
            "status": "success",
            "filename": file.filename,
            "chunks_added": count,
            "database_id": new_doc.id
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
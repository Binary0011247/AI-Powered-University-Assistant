from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.utils.database import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False) # PDF Filename
    document_type = Column(String, default="Syllabus")
    content_summary = Column(Text, nullable=True) # e.g. "Ingested 45 chunks"
    department = Column(String, default="Computer Science")
    uploaded_by = Column(String, nullable=True) # Faculty Email
    created_at = Column(DateTime, server_default=func.now())
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.utils.database import Base

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String, nullable=True)
    query_text = Column(Text, nullable=True)
    response_text = Column(Text, nullable=True)
    context_vector = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
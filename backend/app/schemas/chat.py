from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ChatRequest(BaseModel):
    user_id: Optional[int] = None
    session_id: str
    query_text: str

class ChatResponse(BaseModel):
    id: int
    session_id: str
    query_text: str
    response_text: str
    context_vector: Optional[Dict[str, Any]] = None  # <--- Make sure this is here!
    created_at: datetime

    class Config:
        from_attributes = True
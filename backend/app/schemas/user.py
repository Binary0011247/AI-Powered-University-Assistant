from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

# Schema for creating a user (Input)
class UserCreate(BaseModel):
    email: EmailStr
    department: Optional[str] = None
    year_level: Optional[int] = None
    preferences: Optional[Dict[str, Any]] = None

# Schema for reading a user (Output)
class UserResponse(BaseModel):
    id: int
    email: str
    department: Optional[str]
    year_level: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True # This tells Pydantic to read SQLAlchemy models
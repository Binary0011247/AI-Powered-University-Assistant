import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models.user import User
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# --- Request Schema ---
class LoginRequest(BaseModel):
    email: str
    password: str

# --- Response Schema ---
class LoginResponse(BaseModel):
    id: int
    email: str
    role: str
    name: str
    token: Optional[str] = None

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # 1. Find the user in the PostgreSQL database by email
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # We use a generic message for security, but during dev, 404 is helpful
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid Email or Password"
        )

    # 2. Verify the password using modern bcrypt
    # bcrypt requires bytes, so we encode the strings to utf-8
    try:
        user_password_bytes = request.password.encode('utf-8')
        stored_hash_bytes = user.hashed_password.encode('utf-8')

        # This compares the typed password against the stored hash
        if not bcrypt.checkpw(user_password_bytes, stored_hash_bytes):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid Email or Password"
            )
    except Exception as e:
        # This catches errors if the password in DB isn't a valid hash
        print(f"Auth Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Server error during authentication. Ensure passwords were set correctly."
        )

    # 3. Return the data exactly as your React App.jsx expects it
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,  # 'student', 'faculty', or 'admin'
        "name": user.email.split('@')[0], # Taking the part before @ as the name
        "token": "session_active_token" # Placeholder for future JWT implementation
    }
import bcrypt
import secrets
import string
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.utils.database import get_db
from app.models.user import User

router = APIRouter(prefix="/api/admin", tags=["Admin Management"])

# --- Schemas ---
class UserCreate(BaseModel):
    email: str
    role: str
    department: str = "Unassigned"

class BulkUserCreate(BaseModel):
    users: List[UserCreate]

def generate_random_password(length=8):
    """Generates a secure random 8-character password"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))

@router.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    """Fetch all users to display in the Admin Table"""
    users = db.query(User).all()
    return [{"name": u.email.split('@')[0], "email": u.email, "role": u.role, "dept": u.department} for u in users]

@router.post("/users/single")
def create_single_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create one user and return their auto-generated password"""
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail=f"User {user_data.email} already exists")

    # Generate and hash password
    raw_password = generate_random_password()
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(raw_password.encode('utf-8'), salt).decode('utf-8')

    new_user = User(email=user_data.email, hashed_password=hashed_pw, role=user_data.role, department=user_data.department)
    db.add(new_user)
    db.commit()

    return {"message": "User created", "email": user_data.email, "password": raw_password, "role": user_data.role}

@router.post("/users/bulk")
def create_bulk_users(data: BulkUserCreate, db: Session = Depends(get_db)):
    """Create multiple users and return a list of their credentials"""
    created_users = []
    
    for u in data.users:
        if db.query(User).filter(User.email == u.email).first():
            continue # Skip existing users

        raw_password = generate_random_password()
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(raw_password.encode('utf-8'), salt).decode('utf-8')

        new_user = User(email=u.email, hashed_password=hashed_pw, role=u.role, department=u.department)
        db.add(new_user)
        created_users.append({"email": u.email, "password": raw_password, "role": u.role})
    
    db.commit()
    return {"message": f"Successfully created {len(created_users)} users", "credentials": created_users}
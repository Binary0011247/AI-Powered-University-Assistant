import sys
import os

# This adds the 'backend' folder to Python's search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import bcrypt
from sqlalchemy.orm import Session
from app.utils.database import SessionLocal
from app.models.user import User

def set_user_password(email, new_password, role="student"):
    db = SessionLocal()
    try:
        # 1. Check if user exists
        user = db.query(User).filter(User.email == email).first()
        
        # 2. Hash the new password using modern bcrypt
        # We convert the string to bytes, salt it, then convert back to string to store in DB
        salt = bcrypt.gensalt()
        hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
        
        if user:
            print(f"Updating existing user: {email}")
            user.hashed_password = hashed_pw
            user.role = role
        else:
            print(f"Creating new user: {email}")
            user = User(email=email, hashed_password=hashed_pw, role=role)
            db.add(user)
        
        db.commit()
        print(f"✅ Success! Password for {email} is now set.")
    finally:
        db.close()

if __name__ == "__main__":
    set_user_password("shubh@srm.edu", "mysecret123", "student")
    set_user_password("faculty@srm.edu", "srmfaculty", "faculty")
    set_user_password("admin@srm.edu", "admin@123", "admin")
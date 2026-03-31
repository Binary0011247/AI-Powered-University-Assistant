import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.database import SessionLocal
from app.models.user import User
from datetime import datetime

def test_database():
    db = SessionLocal()
    
    try:
        # Create a test user
        test_user = User(
            email="ds5946@srmist.edu.in",
            department="Computer Science",
            year_level=3,
            preferences={"theme": "dark"}
        )
        
        # Add to database
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"✅ User created with ID: {test_user.id}")
        
        # Query the user
        user = db.query(User).filter(User.email == "ds5946@srmist.edu.in").first()
        print(f"✅ User retrieved: {user.email}, Department: {user.department}")
        
        # Clean up - delete test user
        db.delete(user)
        db.commit()
        print("✅ Test user deleted")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_database()
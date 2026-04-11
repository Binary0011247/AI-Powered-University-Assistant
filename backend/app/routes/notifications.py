from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import pytz
from app.utils.database import get_db
from app.models.notification import Notification
from app.models.user import User

router = APIRouter(prefix="/api/notifications", tags=["Proactive Notifications"])

@router.post("/create-test-deadline")
def create_test_deadline(db: Session = Depends(get_db)):
    # 1. Create a dummy user if one doesn't exist
    user = db.query(User).filter(User.email == "student@srmist.edu.in").first()
    if not user:
        user = User(email="student@srmist.edu.in", department="Computer Science")
        db.add(user)
        db.commit()
        db.refresh(user)

    # 2. Create a deadline that is exactly 2 hours from now!
    due_time = datetime.now(pytz.utc) + timedelta(hours=2)

    new_alert = Notification(
        user_id=user.id,
        notification_type="Assessment",
        title="Machine Learning Assignment 3",
        message="Your ML Neural Networks assignment is due very soon. Please submit it on the portal.",
        due_date=due_time,
        is_read=False # Unread, so the scheduler will catch it!
    )
    
    db.add(new_alert)
    db.commit()
    
    return {"message": "✅ Test deadline injected into database! The background scheduler will catch it within 1 minute."}
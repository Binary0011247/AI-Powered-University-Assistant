import pytz
import sys
from datetime import datetime, timedelta
from app.utils.database import SessionLocal
from app.models.notification import Notification
from app.models.user import User

def check_and_send_notifications():
    """This function runs automatically in the background."""
    # --- ADD THIS HEARTBEAT ---
    print("⏳ [HEARTBEAT] Scheduler is checking the database...")
    sys.stdout.flush() # Forces Python to print to the terminal immediately!
    #
    db = SessionLocal()
    try:
        # 1. Calculate the time window (Now to 24 hours from now)
        utc_now = datetime.now(pytz.utc)
        tomorrow = utc_now + timedelta(days=1)
        
        # 2. Query the database for upcoming, unread deadlines
        upcoming_alerts = db.query(Notification).filter(
            Notification.due_date >= utc_now,
            Notification.due_date <= tomorrow,
            Notification.is_read == False  # We only want ones we haven't sent yet
        ).all()

        if upcoming_alerts:
            print(f"\n⏰ SCHEDULER WOKE UP: Found {len(upcoming_alerts)} upcoming deadlines!")

        for alert in upcoming_alerts:
            user = db.query(User).filter(User.id == alert.user_id).first()
            if user:
                # 3. Simulate sending an email (To do this for real, we'd use smtplib here)
                print("="*50)
                print(f"📧 PROACTIVE EMAIL ALERT SENT!")
                print(f"To: {user.email}")
                print(f"Subject: ⚠️ URGENT: Upcoming {alert.notification_type}")
                print(f"Message: {alert.message}")
                print(f"Due Date: {alert.due_date.strftime('%B %d, %Y at %I:%M %p')}")
                print("="*50)

                # 4. Mark as read so we don't spam the student every minute!
                alert.is_read = True
        
        db.commit()

    except Exception as e:
        print(f"❌ Notification Error: {e}")
    finally:
        db.close()
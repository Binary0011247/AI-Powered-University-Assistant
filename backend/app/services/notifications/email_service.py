import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")

def send_email_alert(to_email: str, subject: str, html_content: str):
    """
    Connects to SendGrid and sends a real email.
    """
    if not SENDGRID_API_KEY or not FROM_EMAIL:
        print("⚠️ WARNING: SendGrid API Key or From Email not found in .env. Cannot send real email.")
        return False
    
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"✅ Email sent to {to_email}! Status Code: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ SendGrid Error: {str(e)}")
        return False
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/university_assistant"
)

# Secret key for security
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
import psycopg2
import sys

# Try to connect
try:
    # Replace with your actual credentials
    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",  # Change if different
        password="Dharmi_@2006"  # Change to your PostgreSQL 
    )
    print("✅ Database connection successful!")
    conn.close()
except psycopg2.OperationalError as e:
    print(f"❌ Database connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure PostgreSQL is running")
    print("2. Check your username and password")
    print("3. Verify database 'university_assistant' exists")
    sys.exit(1)
    
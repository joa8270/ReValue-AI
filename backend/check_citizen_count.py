import sys
import os
sys.path.append(os.getcwd())

# Need to load env vars for DB connection
from dotenv import load_dotenv
load_dotenv() 

from app.core.database import SessionLocal, Citizen

def count_citizens():
    print("Connecting to DB...")
    db = SessionLocal()
    try:
        count = db.query(Citizen).count()
        print(f"Total Citizens in Database: {count}")
        return count
    except Exception as e:
        print(f"Error counting citizens: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    count_citizens()

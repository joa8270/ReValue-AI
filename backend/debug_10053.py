import sys
import os
import json
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.database import SessionLocal, Citizen

def check_citizen_10053():
    db = SessionLocal()
    try:
        # Check specifically for ID 10053
        c = db.query(Citizen).filter(Citizen.id == 10053).first()
        if not c:
            print("Citizen 10053 not found!")
            # Try finding by name if ID is wrong? But screenshot says 00010053 which is 10053.
            return

        print(f"ID: {c.id}")
        print(f"Name: {c.name}")
        print(f"Occupation (Raw): {c.occupation!r}")
        print(f"Occupation (Type): {type(c.occupation)}")

        if isinstance(c.occupation, str):
            print("Is String. Trying JSON decode...")
            try:
                decoded = json.loads(c.occupation)
                print(f"Decoded: {decoded!r}")
            except Exception as e:
                print(f"Decode failed: {e}")
        elif isinstance(c.occupation, dict):
            print("Is Dict (Correct).")
            print(f"Value: {c.occupation}")
            if "TW" in c.occupation:
                print("✅ Found 'TW' key.")
            else:
                print("⚠️ Missing 'TW' key!")
        
    finally:
        db.close()

if __name__ == "__main__":
    check_citizen_10053()

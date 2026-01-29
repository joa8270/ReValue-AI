import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.database import SessionLocal, Citizen

def check_encoding():
    db = SessionLocal()
    try:
        citizens = db.query(Citizen).limit(10).all()
        print(f"Checking {len(citizens)} citizens...")
        for c in citizens:
            # Print raw representation to see exact string content
            print(f"ID: {c.id}")
            print(f"Name: {c.name}")
            print(f"Occupation (Raw): {c.occupation!r}")
            print(f"Occupation (Type): {type(c.occupation)}")
            
            if isinstance(c.occupation, str):
                try:
                    decoded = json.loads(c.occupation)
                    print(f"JSON Decoded: {decoded}")
                except:
                    print("JSON Decode Failed")
            print("-" * 30)

    finally:
        db.close()

if __name__ == "__main__":
    check_encoding()

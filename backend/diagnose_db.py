import sys
import os
import json
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.database import SessionLocal, Citizen

def diagnose():
    db = SessionLocal()
    try:
        # 1. Check Total Count
        count = db.query(Citizen).count()
        print(f"Total Citizens in DB: {count}")
        
        # 2. Check Citizen 10053
        c = db.query(Citizen).filter(Citizen.id == 10053).first()
        if c:
            print(f"\n[Citizen 10053]")
            print(f"Name: {c.name}")
            print(f"Occupation: {c.occupation}")
            print(f"Structure: {c.bazi_profile.get('structure')}")
            print(f"Structure (En): {c.bazi_profile.get('structure_en')}")
            print(f"Bazi Profile Keys: {list(c.bazi_profile.keys())}")
        else:
            print("\nCitizen 10053 NOT FOUND.")
            
        # 3. Check first 5 citizens to see if they look normal
        print(f"\n[First 5 Citizens]")
        citizens = db.query(Citizen).limit(5).all()
        for idx, cit in enumerate(citizens):
             print(f"{cit.id}: {cit.name} - {cit.bazi_profile.get('structure')}")

    finally:
        db.close()

if __name__ == "__main__":
    diagnose()

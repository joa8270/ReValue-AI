
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.database import get_all_citizens, SessionLocal, Citizen

def check_raw():
    print("Checking raw citizen data...")
    db = SessionLocal()
    c = db.query(Citizen).first()
    if c:
        print(f"Citizen ID: {c.id}")
        print(f"Name: {c.name}")
        print("Bazi Profile Raw:")
        # Normalize to dict
        bazi = c.bazi_profile if c.bazi_profile else {}
        print(json.dumps(bazi, ensure_ascii=False, indent=2))
        
        if "birth_year" in bazi:
            print(f"✅ Birth Year Present: {bazi['birth_year']}")
        else:
            print("❌ Birth Year MISSING")
    else:
        print("No citizens found.")
    db.close()

if __name__ == "__main__":
    check_raw()


import os
import sys

# Setup Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from app.core.database import SessionLocal, Citizen

def check_citizen_data():
    db = SessionLocal()
    c = db.query(Citizen).first()
    if not c:
        print("No citizens found.")
        return
        
    print(f"Citizen ID: {c.id}")
    bazi = c.bazi_profile if isinstance(c.bazi_profile, dict) else {}
    fp = bazi.get("four_pillars")
    print(f"Four Pillars Type: {type(fp)}")
    print(f"Four Pillars Value: {fp}")
    
    db.close()

if __name__ == "__main__":
    check_citizen_data()

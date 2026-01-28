
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.database import SessionLocal, Citizen

def check_details():
    db = SessionLocal()
    # Find 谢家伟
    c = db.query(Citizen).filter(Citizen.name == "謝家偉").first()
    
    if c:
        print(f"Citizen: {c.name}")
        bazi = c.bazi_profile or {}
        
        has_luck = "luck_timeline" in bazi and bazi["luck_timeline"]
        has_fav = "favorable" in bazi and bazi["favorable"]
        
        print(f"Has Luck Timeline: {has_luck}")
        if has_luck:
             print(f"Luck items: {len(bazi['luck_timeline'])}")
             
        print(f"Has Favorable: {has_fav}")
        if has_fav:
             print(f"Favorable: {bazi['favorable']}")
             
        # Print keys just in case
        print(f"Keys: {list(bazi.keys())}")
        
    else:
        print("Citizen NOT found")
        
    db.close()

if __name__ == "__main__":
    check_details()

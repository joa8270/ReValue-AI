
import sys
import os
import json
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.database import SessionLocal, Citizen

def check_distribution():
    print("Checking element distribution...")
    db = SessionLocal()
    citizens = db.query(Citizen).all()
    
    elements = []
    
    for c in citizens:
        bazi = c.bazi_profile
        if isinstance(bazi, dict):
            el = bazi.get("element", "Unknown")
            elements.append(el)
        else:
            elements.append("NoProfile")
            
    print(f"Total Citizens: {len(citizens)}")
    counts = Counter(elements)
    for k, v in counts.items():
        print(f"{k}: {v} ({v/len(citizens)*100:.1f}%)")
        
    db.close()

if __name__ == "__main__":
    check_distribution()

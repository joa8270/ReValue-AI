from app.core.database import SessionLocal, Citizen
from collections import Counter
import json

def check_db_elements():
    db = SessionLocal()
    try:
        citizens = db.query(Citizen).all()
        print(f"Total Citizens: {len(citizens)}")
        
        elements = []
        raw_elements = []
        
        for c in citizens:
            bazi = c.bazi_profile if c.bazi_profile else {}
            # Check what's actually in there
            raw_elem = bazi.get("element")
            raw_elements.append(str(raw_elem))
            
            # Check what the logic sees
            elem = bazi.get("element", "Fire_Fallback")
            elements.append(elem)
            
        print("\nRaw Element Field Counts:")
        print(Counter(raw_elements))
        
        print("\nLogic Seen Element Counts:")
        print(Counter(elements))
        
    finally:
        db.close()

if __name__ == "__main__":
    check_db_elements()

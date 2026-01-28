
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.database import SessionLocal, Citizen

def check_details():
    try:
        # Check environment encoding
        import locale
        print(f"System encoding: {sys.getdefaultencoding()}")
        print(f"Locale encoding: {locale.getpreferredencoding()}")
        
        # Force UTF-8 for print
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

    db = SessionLocal()
    # Search by name with wildcard in case of traditional/simplified mix
    # But user saw "謝家偉". 
    name_query = "謝家偉"
    print(f"Searching for: {name_query}")
    
    citizen = db.query(Citizen).filter(Citizen.name == name_query).first()
    
    if citizen:
        print(f"Found Citizen: {citizen.name} (ID: {citizen.id})")
        bazi = citizen.bazi_profile or {}
        
        # Check Favorable
        fav = bazi.get("favorable")
        print(f"Favorable Elements: {fav} (Type: {type(fav)})")
        
        # Check Luck Timeline
        timeline = bazi.get("luck_timeline")
        if timeline:
            print(f"Luck Timeline: Found {len(timeline)} items.")
            print(f"Sample Item: {timeline[0]}")
        else:
            print("Luck Timeline: MISSING or Empty")
            
        # Check other keys
        print(f"Bazi Keys: {list(bazi.keys())}")
    else:
        print("Citizen not found. Trying finding ANY citizen with luck timeline...")
        c_any = db.query(Citizen).first()
        if c_any:
             print(f"Any Citizen: {c_any.name}")
             print(f"Luck Timeline: {c_any.bazi_profile.get('luck_timeline')}")

    db.close()

if __name__ == "__main__":
    check_details()

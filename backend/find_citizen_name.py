from app.core.database import SessionLocal, Citizen
from sqlalchemy import text

def find_citizen(name):
    db = SessionLocal()
    try:
        print(f"Searching for raw name: '{name}'")
        
        # 1. LIKE Search to find candidates
        c_list = db.query(Citizen).filter(Citizen.name.like(f"%{name}%")).all()
        
        if not c_list:
             print("❌ No citizen found via LIKE search.")
        else:
             print(f"✅ Found {len(c_list)} candidates.")
             for c in c_list:
                 print(f"ID: {c.id}")
                 print(f"Name (str): {c.name}")
                 print(f"Name (repr): {repr(c.name)}")
                 
                 if c.name == name:
                     print(" -> EXACT MATCH SUCCESS")
                 else:
                     print(" -> EXACT MATCH FAIL")
            
    finally:
        db.close()

if __name__ == "__main__":
    find_citizen("潘華建")

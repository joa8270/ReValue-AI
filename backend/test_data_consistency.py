import sys
import os
import json

# Setup path to import app modules
sys.path.append(os.getcwd())

from app.core.database import SessionLocal, Citizen, get_citizen_by_id

def test_consistency():
    print("🚀 Starting Consistency Test for ID 10572 (Zhou Yuting)")
    
    # 1. Direct DB Access
    db = SessionLocal()
    try:
        c = db.query(Citizen).filter(Citizen.id == 10572).first()
        if c:
            print(f"\n[Direct DB] Citizen Found: {c.name}")
            print(f"[Direct DB] bazi_profile Type: {type(c.bazi_profile)}")
            
            if isinstance(c.bazi_profile, str):
                print(f"[Direct DB] WARN: bazi_profile is STR! Content start: {c.bazi_profile[:50]}...")
            elif isinstance(c.bazi_profile, dict):
                print(f"[Direct DB] OK: bazi_profile is DICT. Element: {c.bazi_profile.get('element')}")
            else:
                print(f"[Direct DB] Unknown Type: {type(c.bazi_profile)}")
        else:
            print("[Direct DB] Citizen 10572 not found!")
    finally:
        db.close()
        
    # 2. Via Service Function (simulating Modal)
    print("\n[Service Call] Calling get_citizen_by_id(10572)...")
    try:
        c_dict = get_citizen_by_id("10572") # Pass as string to match web.py
        if c_dict:
            print(f"[Service Call] Result ID: {c_dict.get('id')}")
            print(f"[Service Call] Result Element: {c_dict.get('element')}")
            print(f"[Service Call] Result Bazi Element: {c_dict.get('bazi_profile', {}).get('element')}")
        else:
            print("[Service Call] Returned None")
    except Exception as e:
        print(f"[Service Call] ERROR: {e}")

if __name__ == "__main__":
    test_consistency()

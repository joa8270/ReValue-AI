
import os
import json
import asyncio
from sqlalchemy.orm import Session

# Setup Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # backend/
import sys
sys.path.append(BASE_DIR)

from app.core.database import SessionLocal, Citizen, insert_citizens_batch, get_citizens_count

DATA_FILE = os.path.join(BASE_DIR, 'data', 'citizens.json') # UPDATED for V6

def seed_db():
    print(">> Starting Database Seed Process (V6 Genesis)...")
    
    # 1. Always Clear for V6 Genesis
    from app.core.database import clear_citizens
    print(">> Clearing existing citizens...")
    clear_citizens()
    
    # 2. Load JSON
    if not os.path.exists(DATA_FILE):
        # Fallback to original if V6 not found
        OLD_FILE = os.path.join(BASE_DIR, 'data', 'citizens.json')
        if os.path.exists(OLD_FILE):
             print(f">> {DATA_FILE} not found. Falling back to citizens.json")
             with open(OLD_FILE, 'r', encoding='utf-8') as f: data = json.load(f)
        else:
             print(f">> No citizen data found.")
             return
    else:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data_raw = json.load(f)
            
        if isinstance(data_raw, dict) and "citizens" in data_raw:
            data = data_raw["citizens"]
        else:
            data = data_raw
    
    print(f">> Loaded {len(data)} citizens from JSON.")
    
    # 3. Transform Data to DB Schema
    db_records = []
    for item in data:
        # Map fields
        tw_profile = item.get("profiles", {}).get("TW", {})
        
        # Handle Bazi Profile: Use existing V6 dict or construct legacy
        if isinstance(item.get("bazi_profile"), dict):
            final_bazi = item.get("bazi_profile")
            # [Fix] Field Mismatch: luck_pillars -> luck_timeline
            if "luck_pillars" in final_bazi:
                final_bazi["luck_timeline"] = final_bazi.pop("luck_pillars")
        else:
            final_bazi = {
                "structure": item.get("bazi"), 
                "element": "Unknown", 
                "trait": item.get("bazi")
            }

        # Force inject luck data into the Bazi structure
        if "current_luck" in item:
            final_bazi["current_luck"] = item["current_luck"]
        if "luck_pillars" in item:
            final_bazi["luck_timeline"] = item["luck_pillars"]

        # Debug output for the first citizen
        if len(db_records) == 0:
            print(f"[DEBUG] First Citizen Final Bazi Keys: {list(final_bazi.keys())}")
            # Safe print
            try:
                if "current_luck" in final_bazi:
                    print(f"[DEBUG] current_luck: {str(final_bazi['current_luck'])[:50]}...")
            except:
                pass

        record = {
            "id": int(item.get("id")),
            "name": item.get("name"), 
            "gender": item.get("gender"),
            "age": item.get("age"),
            "location": tw_profile.get("city", item.get("city", "Unknown")),
            "occupation": tw_profile.get("job", item.get("job", "Unknown")),
            "bazi_profile": final_bazi,
            "traits": item.get("traits", [item.get("mbti")]), 
            "profiles": item.get("profiles")
        }
        db_records.append(record)
    
    # 4. Insert Batch
    # SQLite might choke on 300+ at once? No, it's fine.
    success = insert_citizens_batch(db_records)
    
    if success:
        print(f">> Successfully seeded {len(db_records)} citizens into the database.")
    else:
        print(">> Seeding failed.")

if __name__ == "__main__":
    seed_db()

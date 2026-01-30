
import os
import json
import sys
from dotenv import load_dotenv

# Setup Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # backend/
PROJECT_ROOT = os.path.dirname(BASE_DIR) # MIRRA/

# 1. LOAD ROOT ENV FIRST (Critical Fix)
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))
print(f"[INFO] Loaded Environment from {PROJECT_ROOT}")
print(f"[INFO] DATABASE_URL: {os.getenv('DATABASE_URL')[:30]}...") 

sys.path.append(BASE_DIR)

from app.core.database import insert_citizens_batch, clear_citizens, get_citizens_count

DATA_FILE = os.path.join(BASE_DIR, 'data', 'citizens.json')

def seed_remote():
    print("[INFO] Starting REMOTE Database Seeding...")
    
    # Check DB Connection
    try:
        count = get_citizens_count()
        print(f"[INFO] Current Remote Count: {count}")
    except Exception as e:
        print(f"[ERROR] Failed to connect to DB: {e}")
        return

    # Load JSON
    if not os.path.exists(DATA_FILE):
        print("[ERROR] citizens.json not found.")
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # Handle { "citizens": [...] } structure
    if isinstance(json_data, dict) and "citizens" in json_data:
        data = json_data["citizens"]
    else:
        # Fallback if it is a list
        data = json_data
        
    print(f"[INFO] Loaded {len(data)} citizens from local JSON.")
    
    # Transform
    db_records = []
    for item in data:
        profiles = item.get("profiles", {})
        tw = profiles.get("TW", {})
        cn = profiles.get("CN", {})
        us = profiles.get("US", {})
        
        # Construct Localized Objects for DB JSON Columns
        name_obj = {
            "TW": tw.get("name", item.get("name")),
            "CN": cn.get("name"),
            "US": us.get("name")
        }
        
        occupation_obj = {
            "TW": tw.get("job"),
            "CN": cn.get("job"),
            "US": us.get("job")
        }
        
        record = {
            "name": name_obj, # DB expects JSON
            "gender": item.get("gender"),
            "age": item.get("age"),
            "location": tw.get("city", item.get("location")), # Default to TW city
            "occupation": occupation_obj, # DB expects JSON
            "bazi_profile": item.get("bazi_profile", {}),
            "traits": item.get("traits", []),
            "profiles": profiles
        }
        db_records.append(record)

    # Seed
    print("[INFO] Clearing Remote Table...")
    # Using clear_citizens might fail if table doesn't exist? No, create_all runs on import.
    try:
        clear_citizens()
    except Exception as e:
        print(f"[WARN] Clear failed (maybe table missing): {e}")
    
    print(f"[INFO] Uploading {len(db_records)} records to DB...")
    success = insert_citizens_batch(db_records)
    
    if success:
        print("[SUCCESS] Remote DB is now in sync.")
    else:
        print("[ERROR] Upload failed.")

if __name__ == "__main__":
    seed_remote()


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
        data = json.load(f)
    print(f"[INFO] Loaded {len(data)} citizens from local JSON.")
    
    # Transform
    db_records = []
    for item in data:
        tw_profile = item.get("profiles", {}).get("TW", {})
        record = {
            "name": item.get("name"),
            "gender": item.get("gender"),
            "age": item.get("age"),
            "location": tw_profile.get("city", "Unknown"),
            "occupation": tw_profile.get("job", "Unknown"),
            "bazi_profile": item.get("bazi_profile", {}),
            "traits": [item.get("mbti")] if isinstance(item.get("mbti"), str) else item.get("traits", []),
            "profiles": item.get("profiles")
        }
        db_records.append(record)

    # Seed
    print("[INFO] Clearing Remote Table...")
    clear_citizens()
    
    print(f"[INFO] Uploading {len(db_records)} records to Neon DB...")
    success = insert_citizens_batch(db_records)
    
    if success:
        print("[SUCCESS] Remote DB is now in sync.")
    else:
        print("[ERROR] Upload failed.")

if __name__ == "__main__":
    seed_remote()

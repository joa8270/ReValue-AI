
import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Setup Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # backend/
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# 1. Load Root Env
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))
print(f"[INFO] Loaded Environment from {PROJECT_ROOT}")

sys.path.append(BASE_DIR)

from app.core.database import engine, Base, insert_citizens_batch
import json

DATA_FILE = os.path.join(BASE_DIR, 'data', 'citizens.json')

def reinit_db():
    print("[WARN] ATTENTION: This will DROP 'citizens' table in remote DB!")
    
    # 1. Connect and Drop
    with engine.connect() as conn:
        print("[INFO] Dropping old table...")
        conn.execute(text("DROP TABLE IF EXISTS citizens CASCADE"))
        conn.commit()
        print("[INFO] Table dropped.")

    # 2. Recreate
    print("[INFO] Recreating tables from Schema...")
    Base.metadata.create_all(bind=engine)
    print("[INFO] Tables created.")

    # 3. Seed
    if not os.path.exists(DATA_FILE):
        print("[ERROR] Data file missing.")
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"[INFO] Seeding {len(data)} citizens...")
    
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

    success = insert_citizens_batch(db_records)
    if success:
        print("[SUCCESS] Schema Updated & Data Seeded!")
    else:
        print("[ERROR] Seeding failed.")

if __name__ == "__main__":
    reinit_db()

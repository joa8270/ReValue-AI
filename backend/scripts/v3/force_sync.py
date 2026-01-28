
import os
import json
import shutil
import time

def force_sync():
    print("🔥 Starting FORCE SYNC Operation...")
    
    # 1. Locate Paths
    # assuming script is in backend/scripts/v3/
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    BACKEND_DIR = os.path.dirname(os.path.dirname(SCRIPT_DIR)) # backend/
    PROJECT_ROOT = os.path.dirname(BACKEND_DIR) # MIRRA/
    
    DATA_DIR = os.path.join(BACKEND_DIR, 'data')
    PROGRESS_FILE = os.path.join(DATA_DIR, 'citizens_progress.jsonl')
    
    TARGET_BACKEND = os.path.join(DATA_DIR, 'citizens.json')
    TARGET_FRONTEND = os.path.join(PROJECT_ROOT, 'frontend', 'public', 'data', 'citizens.json')
    DB_FILE = os.path.join(BACKEND_DIR, 'test.db')

    print(f"📂 Data Directory: {DATA_DIR}")
    
    # 2. Find and Read Progress File
    if not os.path.exists(PROGRESS_FILE):
        print(f"❌ Error: {PROGRESS_FILE} not found!")
        return
        
    print(f"📖 Reading live data from {PROGRESS_FILE}...")
    citizens = []
    try:
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        citizens.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        print(f"❌ Error reading progress file: {e}")
        return

    count = len(citizens)
    print(f"✅ Found {count} citizens in progress file.")
    if count == 0:
        print("⚠️ Warning: No citizens found. Aborting sync to prevent data loss.")
        return

    # 3. Overwrite Targets
    targets = [TARGET_BACKEND, TARGET_FRONTEND]
    
    for target in targets:
        try:
            target_dir = os.path.dirname(target)
            os.makedirs(target_dir, exist_ok=True)
            
            print(f"💾 Overwriting {target}...")
            with open(target, 'w', encoding='utf-8') as f:
                json.dump(citizens, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Failed to write to {target}: {e}")

    # 4. Delete Database (The "Nuclear Option")
    if os.path.exists(DB_FILE):
        print(f"💣 Deleting database file: {DB_FILE} to force re-seeding.")
        try:
            os.remove(DB_FILE)
            print("✅ Database deleted.")
        except Exception as e:
            print(f"❌ Failed to delete DB: {e}. It might be locked.")
            # If locked, we might need to rely on the API restart to release it, 
            # but usually usually removing the file works if app is stopped or via os.remove force
    else:
        print("ℹ️ Database file not found (clean slate).")

    print(f"🎉 Force Sync Complete! {count} citizens are now live in the JSON files.")
    print("👉 Now restart the backend API to re-seed from these new files.")

if __name__ == "__main__":
    force_sync()

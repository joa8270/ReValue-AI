
import os
import json
import shutil
import time
from datetime import datetime

def finalize():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    FRONTEND_DATA_DIR = os.path.join(BASE_DIR, '../frontend/public/data')
    
    NEW_FILE = os.path.join(DATA_DIR, 'citizens_global_v2.json')
    TARGET_FILE = os.path.join(DATA_DIR, 'citizens.json')
    
    # 1. Validation
    if not os.path.exists(NEW_FILE):
        print(f"❌ Error: {NEW_FILE} not found.")
        return
    
    try:
        with open(NEW_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            count = len(data)
            print(f"✅ Loaded generated data. Count: {count}")
            
            if count < 10:
                print("⚠️ Warning: Generated count is very low. Proceeding with caution (or aborting?).")
                # return # Optional: strict check
    except Exception as e:
        print(f"❌ Error reading {NEW_FILE}: {e}")
        return

    # 2. Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{TARGET_FILE}.bak_{timestamp}"
    if os.path.exists(TARGET_FILE):
        print(f"📦 Backing up current citizens.json to {backup_path}")
        shutil.move(TARGET_FILE, backup_path)
    
    # 3. Swap
    print(f"🔄 Swapping new data into place: {TARGET_FILE}")
    shutil.move(NEW_FILE, TARGET_FILE)
    
    # 4. Sync to Frontend
    frontend_target = os.path.join(FRONTEND_DATA_DIR, 'citizens.json')
    print(f"🚀 Syncing to frontend: {frontend_target}")
    
    os.makedirs(FRONTEND_DATA_DIR, exist_ok=True)
    if os.path.exists(frontend_target):
         os.remove(frontend_target)
    
    shutil.copy2(TARGET_FILE, frontend_target)
    
    print("🎉 Finalization Complete!")

if __name__ == "__main__":
    finalize()


import os
import json
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROGRESS_FILE = os.path.join(DATA_DIR, 'citizens_progress.jsonl')
FINAL_OUTPUT = os.path.join(DATA_DIR, 'citizens.json') # V3 overwrites source directly at end
FRONTEND_TARGET = os.path.join(BASE_DIR, '../frontend/public/data/citizens.json')

def finalize():
    print("🚀 Finalizing Generation...")
    
    if not os.path.exists(PROGRESS_FILE):
        print("❌ Progress file not found due to generation failure.")
        return

    citizens = []
    with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                citizens.append(json.loads(line))
            except:
                pass
    
    count = len(citizens)
    print(f"✅ Loaded {count} generated citizens.")
    
    # Validation
    invalid_names = [c for c in citizens if "Citizen_" in c.get("name", "")]
    if invalid_names:
        print(f"⚠️ Warning: Found {len(invalid_names)} citizens with placeholder names!")
        for c in invalid_names[:3]:
            print(f"   - {c['id']}: {c['name']}")
    else:
        print("✅ All citizens have valid names.")

    # Save Final JSON
    print(f"💾 Saving to {FINAL_OUTPUT}")
    with open(FINAL_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(citizens, f, ensure_ascii=False, indent=2)
        
    # Sync to Frontend
    print(f"🔄 Syncing to Frontend: {FRONTEND_TARGET}")
    os.makedirs(os.path.dirname(FRONTEND_TARGET), exist_ok=True)
    shutil.copy2(FINAL_OUTPUT, FRONTEND_TARGET)
    
    print("🎉 V3 Generation & Sync Complete.")

if __name__ == "__main__":
    finalize()

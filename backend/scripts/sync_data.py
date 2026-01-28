import os
import shutil
import json

# Paths
# Script is in backend/scripts/
# We want backend/data/citizens.json
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_ROOT)

SOURCE_FILE = os.path.join(BACKEND_ROOT, "data", "citizens.json")
FRONTEND_ROOT = os.path.join(PROJECT_ROOT, "frontend")

def sync_data():
    print("🔄 Starting Data Sync Operation...")
    print(f"📂 Source: {SOURCE_FILE}")

    # 1. Check Source
    if not os.path.exists(SOURCE_FILE):
        print(f"❌ Fatal: Source file not found at {SOURCE_FILE}")
        return

    # Verify integrity
    try:
        with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Source Verified: Contains {len(data)} citizens.")
    except Exception as e:
        print(f"❌ Fatal: Source file corrupted: {e}")
        return

    # 2. Search Targets in Frontend
    print(f"🔍 Searching for targets in {FRONTEND_ROOT}...")
    found_targets = []
    
    # Common locations to check explicitly first (priority)
    priority_checks = [
        os.path.join(FRONTEND_ROOT, "public", "data", "citizens.json"),
        os.path.join(FRONTEND_ROOT, "public", "citizens.json"),
        os.path.join(FRONTEND_ROOT, "src", "data", "citizens.json"),
        os.path.join(FRONTEND_ROOT, "app", "data", "citizens.json"),
    ]

    # Recursive search
    for root, dirs, files in os.walk(FRONTEND_ROOT):
        # Skip heavy folders
        if "node_modules" in dirs:
            dirs.remove("node_modules")
        if ".next" in dirs:
            dirs.remove(".next")
        if ".git" in dirs:
            dirs.remove(".git")
            
        if "citizens.json" in files:
            full_path = os.path.join(root, "citizens.json")
            if full_path not in found_targets:
                found_targets.append(full_path)

    # 3. Overwrite or Create
    if found_targets:
        print(f"🎯 Found {len(found_targets)} existing instances. Overwriting all...")
        for target in found_targets:
            try:
                shutil.copy2(SOURCE_FILE, target)
                print(f"   ✅ Updated: {target}")
            except Exception as e:
                print(f"   ❌ Failed to update {target}: {e}")
    else:
        print("⚠️ No existing 'citizens.json' found in frontend.")
        # Default Create
        target_path = os.path.join(FRONTEND_ROOT, "public", "data", "citizens.json")
        target_dir = os.path.dirname(target_path)
        
        print(f"🆕 Creating default target at: {target_path}")
        
        if not os.path.exists(target_dir):
            try:
                os.makedirs(target_dir, exist_ok=True)
                print(f"   📁 Created directory: {target_dir}")
            except Exception as e:
                 print(f"   ❌ Failed to create directory: {e}")
                 return

        try:
            shutil.copy2(SOURCE_FILE, target_path)
            print(f"   ✅ File created successfully.")
        except Exception as e:
            print(f"   ❌ File creation failed: {e}")

    print("🎉 Sync Operation Complete.")

if __name__ == "__main__":
    sync_data()

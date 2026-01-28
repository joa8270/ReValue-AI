import json
import os
import shutil
import sys

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BROKEN_FILE = os.path.join(BASE_DIR, "data", "citizens_global_v1.json")
TARGET_FILE = os.path.join(BASE_DIR, "data", "citizens.json")
BACKUP_FILE = os.path.join(BASE_DIR, "data", "citizens.json.bak")

def repair_and_swap():
    print(f"🚑 Starting Surgical Repair on {BROKEN_FILE}...")

    if not os.path.exists(BROKEN_FILE):
        print(f"❌ Source file not found: {BROKEN_FILE}")
        return

    # 1. Read as text
    with open(BROKEN_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_len = len(content)
    print(f"📊 File size: {original_len} bytes")

    # 2. Find last valid object separator '},'
    # We search from the end
    last_idx = content.rfind('},')
    
    if last_idx == -1:
        # Fallback: maybe it's the very last item without a comma? e.g. `...}`
        last_idx = content.rfind('}')
        if last_idx == -1:
            print("❌ No closing brace '}' found. File is extremely corrupted.")
            return
        else:
            print("⚠️ pattern '},' not found, using last '}'")
            # If we split at '}', we keep the '}'
            # Truncate after '}'
            repaired_content = content[:last_idx+1]
    else:
        print(f"📍 Found last object separator '}},' at index {last_idx}")
        # We want to keep the closing brace '}', but discard the comma ',' and everything after
        # content[last_idx] is '}'
        # content[last_idx+1] is ','
        repaired_content = content[:last_idx+1]

    # 3. Add closing bracket
    # Assume file starts with '['
    repaired_content = repaired_content.strip()
    if not repaired_content.endswith(']'):
        repaired_content += ']'

    # 4. robust Recursive Validation Loop
    attempts = 0
    max_attempts = 50
    
    while attempts < max_attempts:
        try:
            # Ensure closing bracket
            if not repaired_content.strip().endswith(']'):
                repaired_content += ']'
            
            data = json.loads(repaired_content)
            count = len(data)
            print(f"✅ Repair Successful! Rescued {count} citizens.")
            
            # 5. Backup & Swap
            print("🔄 Performing Hot Swap...")
            
            # Backup
            if os.path.exists(TARGET_FILE):
                if os.path.exists(BACKUP_FILE):
                    os.remove(BACKUP_FILE)
                shutil.move(TARGET_FILE, BACKUP_FILE)
                print(f"📦 Backup created: {BACKUP_FILE}")

            # Write new file
            with open(TARGET_FILE, 'w', encoding='utf-8') as f:
                f.write(repaired_content)
            
            print(f"🚀 Deployment Complete! {TARGET_FILE} is now updated with {count} records.")
            return

        except json.JSONDecodeError as e:
            attempts += 1
            print(f"⚠️ Attempt {attempts} failed: {e}. Rolling back to previous record...")
            
            # Slice off the last proposed closing `]` first if it exists
            # Actually, `repaired_content` is the string we are testing.
            
            # Find the *next-to-last* `},` relative to current length
            # We stripped up to `last_idx` previously.
            # Now we need to search backwards from `last_idx - 1`
            
            # Current `repaired_content` ends with `...},]`
            
            # Remove the trailing `]`
            if repaired_content.endswith(']'):
                repaired_content = repaired_content[:-1]
                
            # Search for previous `},`
            prev_idx = repaired_content.rfind('},')
            
            if prev_idx == -1:
                 print("❌ Cannot find any valid break point. Giving up.")
                 return
                 
            # Truncate
            repaired_content = repaired_content[:prev_idx+1] # Include the `}`
            # Loop will re-add `]` and test

if __name__ == "__main__":
    repair_and_swap()

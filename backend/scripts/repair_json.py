import json
import os
import sys

# Configuration
FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "citizens_global_v1.json")

def repair_json():
    print(f"🔧 Starting surgical repair on {FILE_PATH}...")
    
    if not os.path.exists(FILE_PATH):
        print("❌ File not found!")
        return

    # 1. Read as plain text
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_len = len(content)
    print(f"📊 Original size: {original_len} characters")

    # 2. Find the last closing brace '}'
    last_brace_index = content.rfind('}')
    
    if last_brace_index == -1:
        print("❌ No closing brace '}' found. File looks severely damaged or empty.")
        return

    print(f"📍 Last '}}' found at index: {last_brace_index}")

    # 3. Surgical amputation: Remove everything after the last '}'
    # 4. Prosthetics: Add ']' to close the array
    # Note: We assume the file starts with '['. If it's a list of objects, we need ']' at the end.
    repaired_content = content[:last_brace_index+1] + "]"
    
    print(f"✂️  Trimmed {original_len - (last_brace_index+1)} characters of corrupted tail.")
    print("🩹 Appended closing bracket ']'.")

    # 5. Validation Check
    print("🔍 Validating JSON structure...")
    try:
        data = json.loads(repaired_content)
        record_count = len(data)
        print(f"✅ Success! JSON is valid.")
        print(f"👥 Recovered {record_count} records.")
        
        # Save back to file
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(repaired_content)
        print("💾 File saved successfully.")
        
    except json.JSONDecodeError as e:
        print(f"❌ Repair failed. JSON is still invalid: {e}")
        # Debug snippet
        print("Packet dump (tail):")
        print(repaired_content[-100:])

if __name__ == "__main__":
    repair_json()

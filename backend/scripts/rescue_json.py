import json
import os
import sys

FILE_PATH = "data/citizens_global_v1.json"

def rescue_json():
    print(f"🔧 Attempting to rescue {FILE_PATH}...")
    
    if not os.path.exists(FILE_PATH):
        print("❌ File not found.")
        return

    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Attempt to parse as is
    try:
        json.loads(content)
        print("✅ JSON is already valid. No changes made.")
        return
    except json.JSONDecodeError:
        print("⚠️ JSON is invalid. Repairing...")

    # Find the last closing brace '}'
    last_brace_index = content.rfind('}')
    
    if last_brace_index == -1:
        print("❌ No closing brace '}' found. File might be too corrupted or empty.")
        return

    # Truncate content up to the last '}'
    rescued_content = content[:last_brace_index+1]
    
    # Check if we need to close the array
    # If the file started with '[', we should end with ']'
    # We stripped everything after the last '}', so we need to add ']'
    # Note: If the file was `[ { ... }`, trimmed is `[ { ... }`. We add `]`.
    # Result: `[ { ... }]`.
    
    final_content = rescued_content + "]"
    
    # dry run validation
    try:
        data = json.loads(final_content)
        print(f"✅ Repair successful! Recovered {len(data)} records.")
        
        # Write back
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            f.write(final_content)
            
        print("💾 File saved.")
    except json.JSONDecodeError as e:
        print(f"❌ Failed to repair: {e}")
        # Last ditch effort: Try to remove trailing comma if it exists inside?
        # But rfind('}') usually works for list of objects.
        # Maybe let's try to see if it's `[ ... }, ]` pattern?
        # If we truncated at `}`, we removed `,` or `]`.
        # So `... }` + `]` = `... }]`. Valid.

if __name__ == "__main__":
    rescue_json()

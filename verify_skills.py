import requests
import sys
import time
import json

BASE_URL = "http://localhost:8000"

def verify_skills():
    print(">> Testing Skills API...")
    
    # 1. List Skills
    print("\n[1] GET /api/skills")
    try:
        res = requests.get(f"{BASE_URL}/api/skills")
        if res.status_code == 200:
            skills = res.json()
            print(f"[OK] Success! Found {len(skills)} skills.")
            print(json.dumps(skills, indent=2, ensure_ascii=False))
            
            # Check if demo-skill is present
            has_demo = any(s['slug'] == 'demo-skill' for s in skills)
            if not has_demo:
                print("[FAIL] 'demo-skill' not found in list!")
                return False
        else:
            print(f"[FAIL] Failed to list skills. Status: {res.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

    # 2. Execute Skill
    print("\n[2] POST /api/skills/demo-skill/execute")
    payload = {"name": "MirRa User"}
    try:
        res = requests.post(f"{BASE_URL}/api/skills/demo-skill/execute", json=payload)
        if res.status_code == 200:
            result = res.json()
            print("[OK] Success! Execution result:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            if "Hello, MirRa User!" in result.get("message", ""):
                print("[OK] Logic check passed.")
                return True
            else:
                print("[FAIL] Logic check failed. Unexpected message.")
                return False
        else:
            print(f"[FAIL] Failed to execute skill. Status: {res.status_code}")
            print(res.text)
            return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

if __name__ == "__main__":
    if verify_skills():
        sys.exit(0)
    else:
        sys.exit(1)

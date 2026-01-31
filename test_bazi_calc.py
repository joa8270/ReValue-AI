import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_bazi():
    print(">> Testing BaZi Calculator Skill...")
    
    url = f"{BASE_URL}/api/skills/bazi-calc/execute"
    payload = {
        "year": 1990, 
        "month": 6, 
        "day": 15, 
        "hour": 10
    }
    
    print(f">> Sending request to {url}")
    print(f">> Payload: {json.dumps(payload)}")
    
    try:
        res = requests.post(url, json=payload)
        
        if res.status_code == 200:
            result = res.json()
            print("\n[OK] Calculation Success!")
            print("========================================")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            print("========================================")
            
            bazi = result.get("bazi", {})
            print(f"Year Pillar : {bazi.get('year')}")
            print(f"Month Pillar: {bazi.get('month')}")
            print(f"Day Pillar  : {bazi.get('day')}")
            print(f"Hour Pillar : {bazi.get('hour')}")
            
            return True
        else:
            print(f"\n[FAIL] Status Code: {res.status_code}")
            print(res.text)
            return False
            
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        return False

if __name__ == "__main__":
    test_bazi()

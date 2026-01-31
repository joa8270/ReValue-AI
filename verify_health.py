import requests
import sys
import time

# 設定後端網址 (預設 localhost:8000，如果不同請修改)
BASE_URL = "http://localhost:8000"

def test_health():
    url = f"{BASE_URL}/api/health"
    print(f"Testing {url}...")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("[OK] Success!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"[FAIL] Failed. Status Code: {response.status_code}")
            print(f"Content: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] Connection Error: Could not connect to {BASE_URL}")
        print("Make sure the backend server is running!")
        return False
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

if __name__ == "__main__":
    if test_health():
        sys.exit(0)
    else:
        sys.exit(1)

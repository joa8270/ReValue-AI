
import requests
import sys

try:
    response = requests.get("http://127.0.0.1:8000/")
    if response.status_code == 200:
        print("✅ Backend is ALIVE:", response.json())
    else:
        print(f"❌ Backend returned status {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Backend connection failed: {e}")
    sys.exit(1)

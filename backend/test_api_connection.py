import requests
import sys

try:
    print("Testing Backend Connection...")
    r = requests.get("http://localhost:8000/docs", timeout=5)
    if r.status_code == 200:
        print(f"✅ Backend is UP (Status: {r.status_code})")
    else:
        print(f"⚠️ Backend returned status: {r.status_code}")
except Exception as e:
    print(f"❌ Backend Connection Failed: {e}")
    sys.exit(1)

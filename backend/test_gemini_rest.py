
import requests
import os
from app.core.config import settings

api_key = settings.GOOGLE_API_KEY
models = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.0-flash-exp",
    "gemini-1.5-flash",
    "gemini-1.5-pro"
]

payload = {
    "contents": [{"parts": [{"text": "Hello, are you working?"}]}]
}

print(f"Testing API with Key: {api_key[:10]}...")

for model in models:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    print(f"\nTesting {model}...")
    try:
        response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Success!")
        else:
            print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

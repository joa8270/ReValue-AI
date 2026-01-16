import asyncio
import os
import requests

async def test_copy_v3():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        api_key = "AIzaSyDTDU5szvsGVIowvvMBNAoqXyXe_RrXU7I"

    # Try different variants
    variants = [
        "v1/models/gemini-1.5-flash",
        "v1beta/models/gemini-1.5-flash",
        "v1/gemini-1.5-flash",
        "v1beta/gemini-1.5-flash",
        "v1beta/models/gemini-1.5-pro",
        "v1beta/models/gemini-2.0-flash-exp"
    ]
    
    payload = {
        "contents": [{"parts": [{"text": "Say hi"}]}]
    }
    
    for variant in variants:
        url = f"https://generativelanguage.googleapis.com/{variant}:generateContent?key={api_key}"
        print(f"Testing {url}...")
        try:
            res = requests.post(url, json=payload, timeout=5)
            print(f"Status: {res.status_code}")
            if res.status_code == 200:
                print("SUCCESS!")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_copy_v3())

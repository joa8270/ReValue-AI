import asyncio
import os
import requests

async def test_copy_v4():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        api_key = "AIzaSyDTDU5szvsGVIowvvMBNAoqXyXe_RrXU7I"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": "Hello"}]}]}
    
    print(f"Testing {url}...")
    res = requests.post(url, json=payload)
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        print("SUCCESS!")

if __name__ == "__main__":
    asyncio.run(test_copy_v4())

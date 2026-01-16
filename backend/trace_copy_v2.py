import asyncio
import os
import base64
import requests

async def test_copy_v2():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        api_key = "AIzaSyDTDU5szvsGVIowvvMBNAoqXyXe_RrXU7I" # Use known key

    model = "gemini-1.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    payload = {
        "contents": [{
            "parts": [{"text": "Hello, how are you?"}]
        }]
    }
    
    print(f"Testing model {model}...")
    res = requests.post(url, json=payload)
    print(f"Status: {res.status_code}")
    if res.status_code == 200:
        print("Success!")
        print(res.json()['candidates'][0]['content']['parts'][0]['text'])
    else:
        print(res.text)

if __name__ == "__main__":
    asyncio.run(test_copy_v2())

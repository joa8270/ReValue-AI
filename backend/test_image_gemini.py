import os
import requests
import base64
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    from app.core.config import settings
    api_key = settings.GOOGLE_API_KEY

def call_gemini(prompt, image_path):
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')

    payload = {
        "contents": [{
            "parts": [
                {"text": prompt}
            ]
        }],
        "generationConfig": {
            "maxOutputTokens": 8192,
            "temperature": 0.7,
            "topP": 0.9,
            "responseMimeType": "application/json"
        }
    }
    
    # Force usage of image/jpeg as per GitHub code
    payload["contents"][0]["parts"].append({"inline_data": {"mime_type": "image/jpeg", "data": image_b64}})

    models = [
        "gemini-2.0-flash-exp",
        "gemini-2.5-flash",
        "gemini-1.5-flash"
    ]
    
    print(f"Testing with Image: {image_path}")
    
    for model in models:
        try:
            print(f"Trying model: {model}...")
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload, timeout=60)
            
            if response.status_code == 200:
                print(f"✅ Success with {model}")
                try:
                    text = response.json()['candidates'][0]['content']['parts'][0]['text']
                    print("Response Preview:")
                    print(text[:500])
                    return text
                except Exception as e:
                    print(f"Parse error: {e}")
                    print(response.text)
                    continue
            else:
                print(f"❌ Failed {model}: {response.status_code} {response.text[:200]}")
        except Exception as e:
            print(f"Exception {model}: {e}")

    return None

if __name__ == "__main__":
    # Use the artifact image path provided in user metadata
    # C:/Users/Joa/.gemini/antigravity/brain/a3896c9e-5402-4ac7-adda-a5ec90c643f4/uploaded_image_1768398078937.png
    # But I need to handle path formatting for Windows or copy it?
    # I will try to access it directly.
    target_image = "C:/Users/Joa/.gemini/antigravity/brain/a3896c9e-5402-4ac7-adda-a5ec90c643f4/uploaded_image_1768398078937.png"
    
    if not os.path.exists(target_image):
        print(f"File not found: {target_image}")
        # Try finding ANY png in the artifact dir?
        # Just use a dummy placeholder if needed, but better to use real one.
    else:
        prompt = "Analyze this product image and return JSON with score between 0-100."
        call_gemini(prompt, target_image)

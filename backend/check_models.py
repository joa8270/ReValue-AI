import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    # Try to find it in settings
    try:
        from app.core.config import settings
        api_key = settings.GOOGLE_API_KEY
    except:
        pass

if not api_key:
    print("NO API KEY FOUND")
    exit(1)

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
try:
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        print("AVAILABLE MODELS:")
        for m in data.get('models', []):
            if 'generateContent' in m.get('supportedGenerationMethods', []):
                print(f"- {m['name']}")
    else:
        print(f"Error {resp.status_code}: {resp.text}")
except Exception as e:
    print(f"Exception: {e}")

import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

def check_version(version):
    print(f"\n--- Checking API Version: {version} ---")
    url = f"https://generativelanguage.googleapis.com/{version}/models?key={api_key}"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            for m in data.get('models', []):
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    print(f"- {m['name']}")
        else:
            print(f"Error {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"Exception: {e}")

check_version("v1")
check_version("v1beta")

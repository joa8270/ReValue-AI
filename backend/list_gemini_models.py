import os
import requests
import json

def list_models():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found")
        return

    for v in ["v1", "v1beta"]:
        print(f"=== {v} ===")
        url = f"https://generativelanguage.googleapis.com/{v}/models?key={api_key}"
        res = requests.get(url)
        if res.status_code == 200:
            data = res.json()
            models = data.get('models', [])
            for m in models:
                name = m.get('name')
                if 'gemini' in name.lower():
                    print(name)
        else:
            print(f"Error {v}: {res.status_code}")

if __name__ == "__main__":
    list_models()

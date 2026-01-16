import os
import requests
import json

def list_models():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found")
        return

    versions = ["v1", "v1beta"]
    for v in versions:
        print(f"--- Models in {v} ---")
        url = f"https://generativelanguage.googleapis.com/{v}/models?key={api_key}"
        try:
            res = requests.get(url)
            if res.status_code == 200:
                models = res.json().get('models', [])
                for m in models:
                    print(m.get('name'))
            else:
                print(f"Error {v}: {res.status_code} {res.text}")
        except Exception as e:
            print(f"Exception {v}: {e}")

if __name__ == "__main__":
    list_models()

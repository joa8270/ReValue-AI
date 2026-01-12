
import requests
import os
from app.core.config import settings

api_key = settings.GOOGLE_API_KEY
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

try:
    response = requests.get(url)
    with open("models_log.txt", "w", encoding="utf-8") as f:
        if response.status_code == 200:
            models = response.json().get('models', [])
            f.write("Available Models:\n")
            for m in models:
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    f.write(f" - {m['name']}\n")
        else:
            f.write(f"Failed to list models: {response.status_code} {response.text}\n")
except Exception as e:
    with open("models_log.txt", "w", encoding="utf-8") as f:
        f.write(f"Exception: {e}\n")

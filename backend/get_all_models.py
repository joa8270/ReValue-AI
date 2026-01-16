import os
import requests
import json

def get_all_models():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        api_key = "AIzaSyDTDU5szvsGVIowvvMBNAoqXyXe_RrXU7I"

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    res = requests.get(url)
    if res.status_code == 200:
        with open("full_models_list.json", "w") as f:
            json.dump(res.json(), f, indent=2)
        print("Written to full_models_list.json")
    else:
        print(f"Error: {res.status_code}")

if __name__ == "__main__":
    get_all_models()


import requests
import json

url = "http://localhost:8000/api/web/refine-copy"
payload = {
    "sim_id": "b10ab0bc-f48c-4a30-9c53-53878bce687e",
    "current_copy": "這是一段測試文案，請幫我優化。",
    "product_name": "測試產品",
    "style": "friendly",
    "source_type": "image"
}

try:
    print(f"Sending request to {url}...")
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print("Response Content:")
    print(response.text)
except Exception as e:
    print(f"Request failed: {e}")

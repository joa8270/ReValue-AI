
import requests
import os

url = "http://localhost:8000/api/web/trigger"
file_path = "frontend/public/mirra-logo-new.jpg" # Use an existing image

if not os.path.exists(file_path):
    # create a dummy image if not exists
    with open("dummy.jpg", "wb") as f:
        f.write(b"dummy image content")
    file_path = "dummy.jpg"

try:
    with open(file_path, "rb") as f:
        files = {"file": ("test.jpg", f, "image/jpeg")}
        data = {
            "product_name": "Test Product",
            "price": "1000",
            "description": "Test Description",
            "mode": "image"
        }
        print("Sending request...")
        response = requests.post(url, files=files, data=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Failed to trigger: {e}")

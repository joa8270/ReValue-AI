
import os
import requests
import base64
import json
from dotenv import load_dotenv

load_dotenv(dotenv_path="frontend/.env.local")
api_key = os.getenv("GOOGLE_API_KEY")

def test_identify():
    url = "http://localhost:8000/api/web/identify-product"
    
    # 讀取一個測試圖片 (如果存在)
    image_path = "C:/Users/Joa/.gemini/antigravity/brain/e31beb4f-131c-45cc-839f-5c002b58162e/uploaded_image_1768764636248.png"
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found")
        return

    with open(image_path, "rb") as f:
        files = [("files", ("bottle.png", f, "image/png"))]
        response = requests.post(url, files=files)
        
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(response.text)

if __name__ == "__main__":
    test_identify()


import requests
import os
import json

def test():
    url = "http://localhost:8000/api/web/identify-product"
    img_path = r"C:/Users/Joa/.gemini/antigravity/brain/e31beb4f-131c-45cc-839f-5c002b58162e/uploaded_image_1768764636248.png"
    
    if not os.path.exists(img_path):
        print(f"Image not found: {img_path}")
        return

    print(f"Testing API: {url}")
    print(f"With image: {img_path}")
    
    try:
        with open(img_path, 'rb') as f:
            files = {'files': ('test.png', f, 'image/png')}
            response = requests.post(url, files=files, timeout=60)
            
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            # 只印出我們關心的部分
            output = {
                "product_name": data.get("product_name"),
                "features_head": data.get("product_features", "")[:200] + "..." # 只看前200字確認有沒有【技術規格】
            }
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            print("Error response:", response.text)
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test()

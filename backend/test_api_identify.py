import requests
import os

def test_identify_product():
    url = "http://localhost:8000/api/web/identify-product"
    # 使用本地現有的圖片測試
    img_path = "c:/Users/Joa/Downloads/MIRRA/unnamed.jpg"
    
    if not os.path.exists(img_path):
        print(f"❌ 找不到測試圖片: {img_path}")
        return

    print(f"🚀 測試 API: {url}")
    with open(img_path, "rb") as f:
        files = {"file": ("test.jpg", f, "image/jpeg")}
        try:
            response = requests.post(url, files=files, timeout=60)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Success!")
                print(f"Result: {response.json()}")
            else:
                print(f"❌ Failed: {response.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    test_identify_product()

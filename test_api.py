
import requests
import json
import os

API_URL = "http://localhost:8000/api/web/trigger"

def test_trigger():
    # 創建一個假的圖片文件
    with open("test_image.jpg", "wb") as f:
        f.write(b"fake image content")
    
    files = {
        'files': ('test_image.jpg', open('test_image.jpg', 'rb'), 'image/jpeg')
    }
    
    data = {
        "product_name": "Test Product",
        "price": "100",
        "description": "Test Description",
        "style": "professional"
    }
    
    try:
        print(f"Sending POST request to {API_URL}...")
        response = requests.post(API_URL, files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response:", response.json())
            print("✅ API Test Passed!")
        else:
            print("❌ API Test Failed!")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    finally:
        # 清理測試文件
        if os.path.exists("test_image.jpg"):
            os.remove("test_image.jpg")

if __name__ == "__main__":
    test_trigger()

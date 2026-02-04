
import requests
import time
import os
import base64

API_URL = "http://localhost:8000"

def create_dummy_png(filename):
    # Minimal 1x1 Transparent PNG
    data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    with open(filename, "wb") as f:
        f.write(data)

def test_simulation():
    print(f"Triggering simulation on {API_URL}...")
    
    img_path = "test_image.png"
    create_dummy_png(img_path)

    try:
        with open(img_path, "rb") as f:
            files = {"files": ("test_image.png", f, "image/png")}
            data = {
                "product_name": "Test Product",
                "price": "100",
                "description": "A test product for simulation.",
                "language": "zh-TW"
            }
            response = requests.post(f"{API_URL}/api/web/trigger", files=files, data=data)
            
        print(f"Trigger Response: {response.status_code}")
        # print(f"Trigger Body: {response.text}")
        
        if response.status_code != 200:
            print("Failed to trigger simulation.")
            return

        sim_id = response.json().get("sim_id")
        print(f"Simulation ID: {sim_id}")
        
        # Poll status
        for i in range(30):
            time.sleep(2)
            print(f"Polling status... ({i+1}/30)")
            # Corrected endpoint
            res = requests.get(f"{API_URL}/simulation/{sim_id}")
            if res.status_code == 200:
                data = res.json()
                status = data.get("status")
                print(f"Status: {status}")
                if status == "ready" or status == "completed":
                    print("Simulation COMPLETED SUCCESS (FINAL)!")
                    return
                if status == "error":
                    print(f"Simulation FAILED: {data}")
                    return
            else:
                print(f"Poll Error: {res.status_code}")
        
        print("Simulation TIMED OUT (stuck on processing).")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_simulation()

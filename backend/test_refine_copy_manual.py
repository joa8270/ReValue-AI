import requests
import json
import sys

# Simulation ID from the recent successful run (found in debug_image.log)
SIM_ID = "5b8885a9-5945-4207-ab06-a72bae59f14f"
API_URL = "http://localhost:8000/api/web/refine-copy"

# Mock original copy (similar to what the frontend would send)
ORIGINAL_COPY = """
MEVIUS Menthol Crystal 策略分析報告
本產品的核心價值在於提供一種「乾淨、高效、具儀式感」的短暫心靈抽離體驗。
它精準地切入了傳統紙菸與新興電子菸之間的市場空隙。
相較於傳統紙菸，它解決了菸灰、菸味殘留及用火不便的核心痛點。
"""

def test_refine_copy():
    print(f"🚀 Testing Refine Copy for Simulation ID: {SIM_ID}")
    print(f"📡 Target URL: {API_URL}")
    
    payload = {
        "sim_id": SIM_ID,
        "current_copy": ORIGINAL_COPY,
        "product_name": "MEVIUS Menthol Crystal",
        "price": "120"
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ API Request Successful!")
            print("-" * 50)
            print("🔍 [Pain Points Analysis]:")
            print(data.get("pain_points_summary", "No summary provided"))
            print("-" * 50)
            print("✨ [Refined Copy]:")
            print(data.get("refined_copy", "No copy generated"))
            print("-" * 50)
            
            # Formatting validation
            if "refined_copy" in data and len(data["refined_copy"]) > 10:
                 print("✅ Verification Passed: Refined copy generated successfully.")
            else:
                 print("❌ Verification Failed: Response seems empty or invalid.")
                 
        else:
            print(f"❌ API Request Failed: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")

if __name__ == "__main__":
    test_refine_copy()

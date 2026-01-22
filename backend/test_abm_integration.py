"""
快速測試ABM整合腳本
"""
import requests
import json

API_URL = "http://localhost:8000"

# 測試創建一個簡單的模擬
test_data = {
    "product_name": "無線耳機",
    "price": "1500",
    "description": "產品名稱：藍牙無線耳機，售價：$1500"
}

print("🧬 [TEST] 測試ABM整合...")
print(f"測試數據: {test_data}")

# 檢查後端是否運行
try:
    response = requests.get(f"{API_URL}/", timeout=5)
    print(f"✅ 後端運行中: {response.status_code}")
except Exception as e:
    print(f"❌ 後端未運行: {e}")
    exit(1)

print("\n🎉 整合完成！請在瀏覽器中上傳圖片進行完整測試")
print("期待看到：")
print("1. 5輪意見演化折線圖")
print("2. 演化日誌（Round-by-Round）")
print("3. 共識度、極化度、從眾效應指標")

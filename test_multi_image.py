"""
測試多圖關聯識別功能
"""
import asyncio
import os
import sys

# 確保能導入 backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.line_bot_service import LineBotService

async def test_multi_image_copy():
    service = LineBotService()
    
    # 使用用戶上傳的 Magic Mouse 圖片（假設有多張）
    test_image_path = "C:/Users/Joa/.gemini/antigravity/brain/815dc9f0-34b8-4c30-a297-8500717b3e97/uploaded_image_1768837492615.png"
    
    if not os.path.exists(test_image_path):
        print(f"❌ 測試圖片不存在: {test_image_path}")
        print("⚠️ 請提供測試圖片路徑")
        return
    
    with open(test_image_path, "rb") as f:
        image_bytes = f.read()
    
    # 模擬多圖上傳（這裡用同一張圖片重複，實際應使用不同角度的圖）
    # 在真實場景中，用戶會上傳正面/側面/背面等不同圖片
    multi_images = [image_bytes, image_bytes, image_bytes, image_bytes]
    
    product_name = "Apple Magic Mouse"
    price = "2290"
    style = "professional"
    
    print(f"🚀 測試多圖文案生成功能")
    print(f"📸 圖片數量: {len(multi_images)}")
    print(f"📦 產品: {product_name}")
    print(f"💰 價格: {price} NTD")
    print(f"🎨 風格: {style}")
    print("=" * 60)
    
    result = await service.generate_marketing_copy(multi_images, product_name, price, style)
    
    if "error" in result:
        print(f"❌ 錯誤: {result['error']}")
        sys.exit(1)
    
    content = result.get("copy_content", "")
    
    print(f"\n✅ 生成成功！")
    print(f"📝 文案長度: {len(content)} 字元")
    print("=" * 60)
    print("📄 生成的文案：")
    print(content)
    print("=" * 60)
    
    # 驗證關鍵字
    print("\n🔍 關鍵字檢查：")
    keywords_to_check = {
        "多視角相關": ["角度", "視角", "正面", "側面", "背面", "細節", "特寫"],
        "技術規格": ["藍牙", "Bluetooth", "無線", "充電", "電池", "續航"],
        "材質/設計": ["鋁", "金屬", "材質", "設計", "工藝"]
    }
    
    for category, keywords in keywords_to_check.items():
        found = [kw for kw in keywords if kw.lower() in content.lower()]
        if found:
            print(f"  ✓ {category}: {', '.join(found)}")
        else:
            print(f"  ✗ {category}: 未找到相關關鍵字")
    
    # 保存結果
    with open("multi_image_copy_output.txt", "w", encoding="utf-8") as f:
        f.write(f"測試配置:\n")
        f.write(f"圖片數量: {len(multi_images)}\n")
        f.write(f"產品名稱: {product_name}\n")
        f.write(f"價格: {price}\n")
        f.write(f"風格: {style}\n")
        f.write(f"\n{'='*60}\n\n")
        f.write(f"生成的文案:\n{content}\n")
    
    print(f"\n💾 結果已保存至: multi_image_copy_output.txt")
    
    print(f"\n✅ 測試完成！")

if __name__ == "__main__":
    asyncio.run(test_multi_image_copy())

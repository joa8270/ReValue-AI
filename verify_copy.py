
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))
load_dotenv()

from app.services.line_bot_service import LineBotService

async def test_generation():
    service = LineBotService()
    
    # Mock data for Apple Magic Mouse
    product_name = "Apple Magic Mouse"
    price = "2290"
    style = "professional"
    
    # Use real uploaded image
    image_path = "C:/Users/Joa/.gemini/antigravity/brain/815dc9f0-34b8-4c30-a297-8500717b3e97/uploaded_image_1768837492615.png"
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            dummy_image = f.read()
    else:
        # Fallback to dummy if file deleted
        print("⚠️ Warning: Real image not found, using dummy.")
        dummy_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\xfc\xff\xff\x3f\x03\x00\x05\xfe\x02\xfe\xa9\xcb\x88"\x00\x00\x00\x00IEND\xaeB`\x82'
    
    print(f"🚀 Testing Copy Generation for: {product_name}")
    print("------------------------------------------------")
    
    result = await service.generate_marketing_copy(dummy_image, product_name, price, style)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)
        
    content = result.get("copy_content", "")
    print(f"\n[Generated Content Length]: {len(content)}")
    
    with open("copy_output.txt", "w", encoding="utf-8") as f:
        f.write(content)
    
    # Validation Logic (Case Insensitive)
    content_lower = content.lower()
    
    missing = []
    # Keywords
    conn_keywords = ["藍牙", "bluetooth", "無線", "wireless", "usb"]
    power_keywords = ["充電", "rechargeable", "電池", "battery", "續航"]
    
    # Check if at least ONE connection keyword is present
    has_connection = any(k in content_lower for k in conn_keywords)
    # Check if at least ONE power keyword is present
    has_power = any(k in content_lower for k in power_keywords)
    
    if not has_connection:
        missing.append("Connectivity (藍牙/Bluetooth/無線/USB)")
    if not has_power:
        missing.append("Power (充電/電池/續航)")
        
    if missing:
        print(f"❌ Test FAILED. Missing explicit specs: {', '.join(missing)}")
        sys.exit(1)
    else:
        print("✅ Test PASSED. Found necessary keywords.")

if __name__ == "__main__":
    asyncio.run(test_generation())

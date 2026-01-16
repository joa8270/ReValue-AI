import asyncio
import os
import base64
import requests
from app.services.line_bot_service import LineBotService
from app.core.config import settings

async def test_copy():
    service = LineBotService()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found")
        return

    # Mock parameters
    product_name = "孫悟空公仔"
    price = "350"
    style = "friendly"
    
    # Use a dummy small image or no image if the method allows
    # generate_marketing_copy requires image_bytes
    dummy_image = b"dummy_image_data_not_real"
    
    print(f"Testing generate_marketing_copy with {product_name}...")
    result = await service.generate_marketing_copy(dummy_image, product_name, price, style)
    print("Result:", result)

if __name__ == "__main__":
    asyncio.run(test_copy())

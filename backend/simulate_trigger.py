
import asyncio
import os
import sys
from sqlalchemy import create_engine, text

# Ensure backend dir is in path
sys.path.append(os.getcwd())

from unittest.mock import MagicMock
from app.services.line_bot_service import LineBotService

# Mock classes to mimic linebot event structure
class MockSource:
    user_id = "U_MOCK_TESTER"

class MockMessage:
    def __init__(self, type, id=None, text=None):
        self.type = type
        self.id = id or "MSG_ID_123"
        self.text = text

class MockEvent:
    def __init__(self, type, message):
        self.source = MockSource()
        self.reply_token = "R_TOKEN_123"
        self.message = message

async def main():
    print("🤖 初始化 LineBotService...")
    try:
        service = LineBotService()
    except Exception as e:
        print(f"Error initializing service: {e}")
        return
    
    # 1. Mock External APIs (LINE) to avoid errors
    service.line_bot_api = MagicMock()
    service.line_bot_blob = MagicMock()
    service.line_bot_api.reply_message = MagicMock()
    service.line_bot_api.push_message = MagicMock()

    # Read local image bytes (Dummy)
    img_bytes = b'\xFF\xD8\xFF\xE0\x00\x10\x4A\x46\x49\x46\x00\x01\x01\x01\x00\x48\x00\x48\x00\x00\xFF\xDB\x00\x43\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xC0\x00\x0B\x08\x00\x01\x00\x01\x01\x01\x11\x00\xFF\xC4\x00\x1F\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\xFF\xDA\x00\x08\x01\x01\x00\x00\x3F\x00\x7F\xFF\xD9'
    service.line_bot_blob.get_message_content.return_value = img_bytes

    # 2. Simulate User Sending Image
    print("\n▶️ [STEP 1] 模擬使用者傳送圖片...")
    img_event = MockEvent("message", MockMessage("image", id="IMG_MSG_001"))
    await service.handle_event(img_event)
    
    # 3. Simulate User Sending Details
    print("\n▶️ [STEP 2] 模擬使用者輸入: '未來手錶 / 25000'...")
    text_event = MockEvent("message", MockMessage("text", text="未來手錶 / 25000"))
    await service.handle_event(text_event)
    
    # 4. Simulate User Skipping Description
    print("\n▶️ [STEP 3] 模擬使用者輸入: '3' (略過)...")
    skip_event = MockEvent("message", MockMessage("text", text="3"))
    
    print("⏳ 等待 AI 分析完成 (這可能需要幾秒鐘)...")
    await service.handle_event(skip_event)

    print("\n✅ 模擬觸發完成！")

    # 5. Fetch Latest ID
    engine = create_engine("sqlite:///./test.db")
    with engine.connect() as conn:
        try:
            # Assuming created_at exists, order by it. If not, sim_id is UUID so order might not work perfect but let's try.
            # Actually, standard SQL doesn't guarantee order without created_at.
            # Let's hope filtering by 'ready' status helps or just taking any.
            result = conn.execute(text("SELECT sim_id FROM simulations ORDER BY rowid DESC LIMIT 1"))
            row = result.fetchone()
            if row:
                print(f"🎉 NEW_SIM_ID: {row[0]}")
            else:
                print("❌ ERROR: Could not find created simulation in DB.")
        except Exception as e:
            print(f"❌ DB Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

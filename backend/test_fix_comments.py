
import asyncio
import os
import sys
import json
from sqlalchemy import create_engine, text
from unittest.mock import MagicMock
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Ensure backend dir is in path
sys.path.append(os.getcwd())

from app.services.line_bot_service import LineBotService

# Mock classes to mimic linebot event structure
class MockSource:
    user_id = "U_TEST_FIX_COMMENTS"

class MockMessage:
    def __init__(self, type, id=None, text=None):
        self.type = type
        self.id = id or "MSG_ID_TEST"
        self.text = text

class MockEvent:
    def __init__(self, type, message):
        self.source = MockSource()
        self.reply_token = "R_TOKEN_TEST"
        self.message = message

async def main():
    print("Initializing LineBotService for Verification...")
    try:
        service = LineBotService()
    except Exception as e:
        print(f"Error initializing service: {e}")
        return
    
    # 1. Mock External APIs (LINE)
    service.line_bot_api = MagicMock()
    service.line_bot_blob = MagicMock()
    service.line_bot_api.reply_message = MagicMock()
    service.line_bot_api.push_message = MagicMock()

    # Use a dummy image to trigger Gemini failure -> Fallback
    img_bytes = b'\xFF\xD8\xFF\xE0\x00\x10\x4A\x46\x49\x46\x00\x01\x01\x01\x00\x00\x00\x00\x00\x00\xFF\xDB\x00\x43\x00\xFF\xC0\x00\x0B\x08\x00\x01\x00\x01\x01\x01\x11\x00\xFF\xC4\x00\x1F\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\xFF\xDA\x00\x08\x01\x01\x00\x00\x3F\x00\x7F\xFF\xD9'
    service.line_bot_blob.get_message_content.return_value = img_bytes

    # 2. Simulate User Sending Image
    print("\n[STEP 1] Sending Dummy Image...")
    img_event = MockEvent("message", MockMessage("image", id="IMG_TEST_001"))
    await service.handle_event(img_event)
    
    # 3. Simulate User Sending Details
    print("\n[STEP 2] Sending Product Details...")
    text_event = MockEvent("message", MockMessage("text", text="Ghost Product / 9999"))
    await service.handle_event(text_event)
    
    # 4. Simulate User Skipping Description to Trigger Analysis
    print("\n[STEP 3] Skip description -> Trigger Analysis...")
    skip_event = MockEvent("message", MockMessage("text", text="3"))
    
    print("Waiting for analysis (expecting fallback due to invalid image)...")
    await service.handle_event(skip_event)

    print("\nSimulation trigger complete. checking DB...")

    # 5. Verify Results in DB
    engine = create_engine("sqlite:///./test.db")
    with engine.connect() as conn:
        try:
            # Get latest simulation
            result = conn.execute(text("SELECT sim_id, data FROM simulations ORDER BY rowid DESC LIMIT 1"))
            row = result.fetchone()
            if row:
                sim_id, data_str = row
                data = json.loads(data_str)
                # Check for arena_comments instead of comments, as that's the final key used in result
                comments = data.get("arena_comments", [])
                if not comments:
                     comments = data.get("comments", [])
                     
                print(f"Latest Simulation ID: {sim_id}")
                print(f"Comment Count: {len(comments)}")
                
                valid_count = 0
                for c in comments:
                    txt = c.get("text", "")
                    print(f"   - {txt[:50]}...")
                    if len(txt) > 5 and "符合我的" not in txt:
                        valid_count += 1
                
                if valid_count >= 8:
                    print(f"\nSUCCESS: Found {valid_count} valid comments! Fix verified.")
                else:
                    print(f"\nFAILURE: Only found {valid_count} valid comments. Expected at least 8.")
            else:
                print("ERROR: No simulation found in DB.")
        except Exception as e:
            print(f"DB Verification Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import os
import sys
from dotenv import load_dotenv
from unittest.mock import MagicMock

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from app.services.line_bot_service import LineBotService

async def main():
    print("🚀 Starting Simulation Test...")
    
    # Initialize Service
    service = LineBotService()
    
    # Mock the Blob client to return the local logo image as bytes
    with open("../frontend/public/logo.png", "rb") as f:
        image_bytes = f.read()
    
    service.line_bot_blob.get_message_content = MagicMock(return_value=image_bytes)
    
    # Mock reply_text pushing/messaging since we don't have real line user
    service.line_bot_api.push_message = MagicMock()
    service.reply_text = MagicMock()
    
    # Create a dummy sim_id
    sim_id = "test-sim-local-001"
    message_id = "test-msg-001"
    
    print(f"📦 Simulating with image size: {len(image_bytes)} bytes")
    print(f"🆔 Simulation ID: {sim_id}")
    
    # Create initial record (normally done in _start_simulation)
    from app.core.database import create_simulation
    initial_data = {
        "status": "processing",
        "score": 0,
        "intent": "Calculating...",
        "summary": "Local Test Simulation...",
        "genesis": {"total_population": 0, "sample_size": 0, "personas": []},
        "comments": []
    }
    create_simulation(sim_id, initial_data)
    
    # Run the core logic
    try:
        await service.process_image_with_ai(
            message_id=message_id, 
            sim_id=sim_id, 
            text_context="產品名稱：測試Logo / 售價：999元"
        )
        print("\n✅ Simulation Logic Completed Successfully!")
        print(f"🔗 View Result at: http://localhost:4000/watch/{sim_id}")
        
    except Exception as e:
        print(f"\n❌ Simulation Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())


import sys
import os

# Add project root to path
sys.path.insert(0, os.getcwd())

try:
    print("Attempting to import LineBotService...")
    from app.services.line_bot_service import LineBotService
    print("Import successful.")
    
    print("Attempting to instantiate LineBotService...")
    service = LineBotService()
    print("Instantiation successful.")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()

import os
import sys
import asyncio
import json
import uuid
import base64
from unittest.mock import MagicMock, patch

# 1. 設置路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app.services.line_bot_service import LineBotService

# 模擬環境變量
os.environ["GOOGLE_API_KEY"] = "mock_key"
os.environ["LINE_CHANNEL_ACCESS_TOKEN"] = "mock_token"
os.environ["LINE_CHANNEL_SECRET"] = "mock_secret"

async def verify_lang(lang):
    print(f"--- Verifying Language: {lang} ---")
    service = LineBotService()
    
    mock_citizens = [
        {
            "id": i, 
            "name": f"Citizen_{i}", 
            "age": 20+i, 
            "gender": "M",
            "location": "Taipei" if lang != "en" else "London",
            "occupation": "Tester",
            "traits": ["Serious"],
            "bazi_profile": {"day_master": "A", "structure": "B", "element": "Wood"}
        }
        for i in range(5)
    ]
    
    sim_id = f"test-{lang}"
    pdf_bytes = b"%PDF-1.4 mock core"
    
    with patch('app.services.line_bot_service.get_random_citizens', return_value=mock_citizens), \
         patch('app.services.line_bot_service.update_simulation') as mock_update, \
         patch.object(LineBotService, '_call_gemini_rest', return_value=(None, "Mock Timeout")), \
         patch.object(LineBotService, '_run_abm_simulation', return_value={"evolution_data": {}, "analytics_data": {}, "comments_data": []}):
        
        await service.run_simulation_with_pdf_data(sim_id, pdf_bytes, "test.pdf", language=lang)
        
        args, kwargs = mock_update.call_args
        data = args[2]
        
        comments = data.get("arena_comments", [])
        personas = data.get("genesis", {}).get("personas", [])
        
        if not comments:
            print(f"[FAILED] [{lang}] arena_comments empty")
            return False
        
        first_comment = comments[0]["text"]
        print(f"Sample Comment: {first_comment}")
        
        if lang == "en":
            if any(word in first_comment.lower() for word in ["potential", "perspective", "entrepreneur", "revenue"]):
                print(f"[SUCCESS] [{lang}] English keywords detected")
            else:
                print(f"[FAILED] [{lang}] No English keywords")
                return False
        elif lang == "zh-CN":
            if "计划书" in first_comment or "创业者" in first_comment:
                 print(f"[SUCCESS] [{lang}] Simplified Chinese keywords detected")
            else:
                 print(f"[FAILED] [{lang}] No Simplified Chinese")
                 return False
        else:
            if "計劃書" in first_comment or "創業者" in first_comment:
                 print(f"[SUCCESS] [{lang}] Traditional Chinese keywords detected")
            else:
                 print(f"[FAILED] [{lang}] No Traditional Chinese")
                 return False
        
        if len(personas) == 5:
            print(f"[SUCCESS] [{lang}] Personas count correct")
        else:
            print(f"[FAILED] [{lang}] Personas count incorrect: {len(personas)}")
            return False
            
        return True

async def main():
    langs = ["zh-TW", "zh-CN", "en"]
    success = True
    for lang in langs:
        if not await verify_lang(lang):
            success = False
    
    if success:
        print("\nAll Multi-lang PDF Fixes Verified!")
        sys.exit(0)
    else:
        print("\nVerification FAILED")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

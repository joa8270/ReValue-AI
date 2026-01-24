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

async def test_pdf_fallback():
    print("🚀 [TEST] 啟動 PDF Fallback 邏輯測試...")
    service = LineBotService()
    
    # 模擬 5 位市民
    mock_citizens = [
        {
            "id": i, 
            "name": f"市民_{i}", 
            "age": 20+i, 
            "gender": "M",
            "location": "Taipei",
            "occupation": "Tester",
            "traits": ["認真", "負責"],
            "bazi_profile": {
                "day_master": "甲",
                "structure": "正官",
                "element": "Wood",
                "luck_timeline": [],
                "current_luck": {}
            }
        }
        for i in range(5)
    ]
    
    sim_id = "test-sim-id"
    pdf_bytes = b"%PDF-1.4 mock content"
    
    # Mocking external calls
    with patch('app.services.line_bot_service.get_random_citizens', return_value=mock_citizens), \
         patch('app.services.line_bot_service.update_simulation') as mock_update, \
         patch.object(LineBotService, '_call_gemini_rest', return_value=(None, "Mock Timeout")), \
         patch.object(LineBotService, '_run_abm_simulation', return_value={"evolution_data": {}, "analytics_data": {}, "comments_data": []}):
        
        print("📥 正在執行 run_simulation_with_pdf_data (注入 Gemini 失敗情境)...")
        await service.run_simulation_with_pdf_data(pdf_bytes, sim_id, "test.pdf")
        
        # 取得最後一次更新的數據
        args, kwargs = mock_update.call_args
        updated_data = args[2]
        
        # 驗證結果
        print(f"\n--- 測試結果 ---")
        print(f"📊 狀態: {updated_data.get('status')}")
        print(f"📉 分數: {updated_data.get('score')}")
        print(f"📝 總結: {updated_data.get('summary')[:30]}...")
        
        comments = updated_data.get("arena_comments", [])
        print(f"💬 評論數量: {len(comments)}")
        
        personas = updated_data.get("genesis", {}).get("personas", [])
        print(f"👥 參與市民數量: {len(personas)}")
        
        # 檢查 Bug: arena_comments 是否為空
        if not comments:
            print("❌ [FAILED] arena_comments 為空")
        else:
            print(f"✅ [SUCCESS] arena_comments 包含 {len(comments)} 條")
            
        # 檢查 Bug: personas 是否為空
        if not personas:
            print("❌ [FAILED] personas 為空")
        else:
            print(f"✅ [SUCCESS] personas 包含 {len(personas)} 位")
        print(f"--- 測試結束 ---\n")

if __name__ == "__main__":
    asyncio.run(test_pdf_fallback())

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

# 關鍵：從 LineBotService 引入那個暫存的資料庫
# 這樣 API 才能看到 LINE 機器人寫入的資料
from backend.app.services.line_bot_service import MOCK_DB

router = APIRouter()

@router.get("/{sim_id}")
async def get_simulation_status(sim_id: str):
    """
    戰情室前端會不斷呼叫這個 API 來取得最新數據
    """
    # 1. 檢查資料庫有沒有這個模擬 ID
    if sim_id not in MOCK_DB:
        # 🟢 新版邏輯：如果找不到，回傳「等待中」，絕對不要報 404 錯誤！
        return {
            "status": "waiting", 
            "message": "Simulation not found or not started yet."
        }
    
    # 2. 取得資料
    sim_data = MOCK_DB[sim_id]
    
    # 3. 判斷是否有結果
    if "result" in sim_data:
        return {
            "status": "completed",
            "result": sim_data["result"],
            "logs": sim_data.get("logs", []) # 把日誌也傳回去
        }
    else:
        return {
            "status": "running",
            "logs": sim_data.get("logs", [])
        }
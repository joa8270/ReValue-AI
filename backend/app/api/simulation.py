from fastapi import APIRouter
from app.core.database import get_simulation

router = APIRouter()

@router.get("/{sim_id}")
async def get_simulation_status(sim_id: str):
    """
    戰情室前端會不斷呼叫這個 API 來取得最新數據
    """
    # 1. 從資料庫讀取
    sim_data = get_simulation(sim_id)

    # 2. 如果找不到，回傳「等待中」
    if not sim_data:
        return {
            "status": "waiting", 
            "message": "Simulation not found or not started yet."
        }
    
    # 3. 直接回傳資料庫中的 JSON 結構
    # get_simulation 已經把 status 合併進去了
    return sim_data

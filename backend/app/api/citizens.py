from fastapi import APIRouter, Query
from backend.app.core.database import get_all_citizens, get_citizens_count

router = APIRouter()


@router.get("/")
async def list_citizens(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """
    獲取市民庫資料
    可用於前端展示完整 1000 位市民資訊
    """
    citizens = get_all_citizens(limit=limit, offset=offset)
    total = get_citizens_count()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "citizens": citizens
    }


@router.get("/count")
async def citizens_count():
    """獲取市民總數"""
    return {"count": get_citizens_count()}


@router.get("/genesis")
async def get_genesis_citizens():
    """Retrieve citizens from DB (Fallback to JSON if DB fails)"""
    try:
        # Try DB first (Real source of truth)
        citizens = get_all_citizens(limit=1000, offset=0)
        if citizens and len(citizens) > 0:
            return {"citizens": citizens, "total": len(citizens), "source": "db"}
    except Exception as e:
        print(f"[API] DB fetch failed: {e}")

    import json
    import os
    
    # Fallback to backend/app/data/citizens.json
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(base_dir, "app", "data", "citizens.json")
    
    if not os.path.exists(file_path):
        return {"citizens": [], "total": 0, "message": "Genesis data not found"}
        
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    data["source"] = "json"
    return data

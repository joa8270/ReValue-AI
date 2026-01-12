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

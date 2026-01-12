import os
import sys

# 🔧 修正 Python Path (讓 Render 環境能找到 app 模組)
# Render Root Directory = backend, 所以需要將 backend 加入 sys.path
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from linebot.v3.webhook import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError

from app.services.line_bot_service import LineBotService, get_simulation_data
from app.core.config import settings
from app.core.database import get_all_citizens, get_citizens_count
from app.api.web import router as web_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

line_bot_service = LineBotService()
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

# Register Web Router
app.include_router(web_router, prefix="/api/web", tags=["Web Trigger"])

@app.get("/")
async def root():
    return {"status": "alive", "message": "MIRRA Backend is running with PostgreSQL!"}


# --- 市民庫 API ---
@app.get("/citizens")
async def list_citizens(limit: int = 100, offset: int = 0):
    """獲取市民庫資料"""
    citizens = get_all_citizens(limit=limit, offset=offset)
    total = get_citizens_count()
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "citizens": citizens
    }

# --- PostgreSQL 模式：從資料庫獲取資料 ---
@app.get("/simulation/{sim_id}")
async def get_simulation_endpoint(sim_id: str):
    # 從 PostgreSQL 撈資料
    data = get_simulation_data(sim_id)
    
    if not data:
        # 如果資料庫找不到，回傳 processing (可能尚未寫入)
        return {
            "status": "processing",
            "score": 0,
            "intent": "Computing...",
            "summary": "正在等待 Gemini AI 生成 AI 虛擬市民數據...",
            "genesis": {"total_population": 0, "sample_size": 0, "personas": []},
            "comments": []
        }
    
    # 有資料就直接回傳
    return data
# ------------------------------------

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    body_str = body.decode("utf-8")

    try:
        events = parser.parse(body_str, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        await line_bot_service.handle_event(event)

    return "OK"
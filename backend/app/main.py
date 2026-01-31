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
from app.core.database import get_all_citizens, get_citizens_count, init_db
from app.api.web import router as web_router
from app.services.skill_registry import skill_registry # Import Skill Registry

app = FastAPI()

# Initialize Skill Registry
@app.on_event("startup")
async def startup_event():
    print(">> [System] Starting up... Scanning for Skills...")
    skill_registry.discover_skills()
    
    print(">> [System] Initializing Database...")
    init_db()

# 🔄 Force Update: 2026-01-14 01:15

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

@app.get("/api/health")
async def health_check():
    """系統健康檢查接口"""
    return {"status": "ok", "version": "1.0"}

# --- Skills API ---
@app.get("/api/skills")
async def list_skills():
    """列出所有可用技能"""
    return skill_registry.list_skills()

@app.post("/api/skills/{slug}/execute")
async def execute_skill(slug: str, request: Request):
    """執行特定技能"""
    skill = skill_registry.get_skill(slug)
    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill '{slug}' not found")
    
    try:
        body = await request.json()
    except Exception:
        body = {}
        
    try:
        result = await skill.execute(body)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill execution failed: {str(e)}")

# --- 市民庫 API ---
@app.get("/citizens/genesis")
async def get_genesis_citizens():
    """Retrieve genesis prototype citizens from JSON"""
    import json
    
    # Path to backend/data/citizens.json (Corrected path)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # backend/
    file_path = os.path.join(base_dir, "data", "citizens.json")
    
    if not os.path.exists(file_path):
        return {"citizens": [], "total": 0, "message": "Genesis data not found"}
        
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    return data

@app.get("/citizens")
async def list_citizens(limit: int = 100, offset: int = 0, search: str = None):
    """獲取市民庫資料"""
    citizens = get_all_citizens(limit=limit, offset=offset, search=search)
    total = get_citizens_count(search=search)
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
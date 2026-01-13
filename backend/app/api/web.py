from fastapi import APIRouter, File, UploadFile, Form, BackgroundTasks
from app.core.database import create_simulation
import uuid

router = APIRouter()

# 移除全域 import 和實例化，避免循環引用
# from app.services.line_bot_service import LineBotService
# line_service = LineBotService()

@router.post("/trigger")
async def trigger_simulation(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    product_name: str = Form(None),
    price: str = Form(None),
    description: str = Form(None)
):
    from app.services.line_bot_service import LineBotService
    line_service = LineBotService()

    sim_id = str(uuid.uuid4())
    
    # 建立初始狀態
    initial_data = {
        "status": "processing",
        "score": 0,
        "intent": "Calculating...",
        "summary": "AI 正在啟動並讀取您的資料...",
        "genesis": {"total_population": 0, "sample_size": 0, "personas": []},
        "comments": []
    }
    # 建立 DB 紀錄
    create_simulation(sim_id, initial_data)
    
    # 讀取檔案
    file_bytes = await file.read()
    filename = file.filename.lower()
    
    # 組合 Text Context (僅對圖片有效，PDF 有自己的 prompt 邏輯但也可以考慮加入 metadata)
    text_context = ""
    if product_name: text_context += f"產品名稱：{product_name}\n"
    if price: text_context += f"建議售價：{price}\n"
    if description: text_context += f"產品描述：{description}\n"
    text_context = text_context.strip() if text_context else None

    # 判斷類型並啟動背景任務
    if filename.endswith(".pdf"):
        # PDF 處理
        background_tasks.add_task(line_service.run_simulation_with_pdf_data, file_bytes, sim_id, filename)
    else:
        # 圖片處理
        background_tasks.add_task(line_service.run_simulation_with_image_data, file_bytes, sim_id, text_context)
        
    return {"status": "ok", "sim_id": sim_id}

@router.post("/generate-description")
async def generate_description(
    file: UploadFile = File(...),
    product_name: str = Form(...),
    price: str = Form(...)
):
    try:
        from app.services.line_bot_service import LineBotService
        line_service = LineBotService()

        file_bytes = await file.read()
        
        # Call LineBotService to generate copy
        result = await line_service.generate_marketing_copy(file_bytes, product_name, price)
        
        if "error" in result:
            return {"error": result["error"]}
            
        return result
        
    except Exception as e:
        return {"error": str(e)}

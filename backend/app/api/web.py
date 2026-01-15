from fastapi import APIRouter, File, UploadFile, Form, BackgroundTasks
from app.core.database import create_simulation, insert_citizens_batch, get_citizens_count, clear_citizens
import uuid
import sys
import os

# 確保可以導入 create_citizens
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from create_citizens import generate_citizen

router = APIRouter()

@router.get("/admin/reset-citizens")
async def reset_citizens_endpoint(count: int = 1000):
    """
    [Admin] 重置並重新生成 AI 市民數據庫
    """
    try:
        print(f"🔄 開始重置市民數據，目標: {count} 位...")
        clear_citizens()
        
        citizens = [generate_citizen(i) for i in range(count)]
        
        batch_size = 100
        for i in range(0, len(citizens), batch_size):
            insert_citizens_batch(citizens[i:i+batch_size])
            
        final_count = get_citizens_count()
        return {"status": "success", "message": f"成功重置並生成 {final_count} 位 AI 市民", "count": final_count}
    except Exception as e:
        print(f"❌ 重置失敗: {e}")
        return {"status": "error", "message": str(e)}

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
    filename = file.filename.lower() if file.filename else ""
    
    # 組合 Text Context
    text_context = ""
    if product_name: text_context += f"產品名稱：{product_name}\n"
    if price: text_context += f"建議售價：{price}\n"
    if description: text_context += f"產品描述：{description}\n"
    text_context = text_context.strip() if text_context else None

    # 判斷檔案類型
    from app.utils.document_parser import parse_document, get_file_extension
    ext = get_file_extension(filename)
    
    # 文件類型處理 (Word, PPT, TXT)
    document_extensions = ["docx", "pptx", "txt"]
    audio_extensions = ["webm", "mp3", "wav", "m4a", "ogg"]
    
    if ext == "pdf":
        # PDF 處理 (現有流程)
        background_tasks.add_task(line_service.run_simulation_with_pdf_data, file_bytes, sim_id, filename)
    elif ext in document_extensions:
        # Word/PPT/TXT: 解析文字後傳給文字分析流程
        parsed_text = parse_document(file_bytes, filename)
        if parsed_text:
            # 合併解析內容與用戶額外輸入
            full_context = parsed_text
            if text_context:
                full_context = f"{text_context}\n\n---\n\n{parsed_text}"
            background_tasks.add_task(line_service.run_simulation_with_text_data, full_context, sim_id, ext)
        else:
            # 設置錯誤狀態
            from app.core.database import update_simulation
            update_simulation(sim_id, "error", {"status": "error", "summary": f"無法解析 {ext.upper()} 文件"})
    elif ext in audio_extensions:
        # 音訊檔: 傳給語音轉文字處理
        background_tasks.add_task(line_service.run_simulation_with_audio_data, file_bytes, sim_id, ext)
    else:
        # 預設為圖片處理
        background_tasks.add_task(line_service.run_simulation_with_image_data, file_bytes, sim_id, text_context)
        
    return {"status": "ok", "sim_id": sim_id}

@router.post("/generate-description")
async def generate_description(
    file: UploadFile = File(...),
    product_name: str = Form(...),
    price: str = Form(...),
    style: str = Form("professional")
):
    try:
        from app.services.line_bot_service import LineBotService
        line_service = LineBotService()

        file_bytes = await file.read()
        
        # Call LineBotService to generate copy with selected style
        result = await line_service.generate_marketing_copy(file_bytes, product_name, price, style)
        
        if "error" in result:
            return {"error": result["error"]}
            
        return result
        
    except Exception as e:
        return {"error": str(e)}

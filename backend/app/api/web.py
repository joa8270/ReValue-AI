from fastapi import APIRouter, File, UploadFile, Form, BackgroundTasks
from typing import List
from app.core.database import create_simulation, insert_citizens_batch, get_citizens_count, clear_citizens, get_citizen_by_id, update_simulation
import uuid
from app.services.video_analysis_service import video_analysis_service

import sys
import os
import json

print("[WEB] Module web.py loaded!", flush=True)

# 確保可以導入 create_citizens
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from create_citizens import generate_citizen

router = APIRouter()

# 🔧 Debug wrapper to catch background task exceptions
async def safe_run_pdf_task(line_service, *args, **kwargs):
    """Wrapper to catch and log any exceptions from PDF background task"""
    try:
        with open("debug_trace.log", "a", encoding="utf-8") as f:
            f.write(f"[WRAPPER] Starting PDF task with {len(args)} args, {len(kwargs)} kwargs\n")
        await line_service.run_simulation_with_pdf_data(*args, **kwargs)
    except Exception as e:
        import traceback
        error_msg = f"[WRAPPER] PDF Task Failed: {e}\n{traceback.format_exc()}"
        print(error_msg, flush=True)
        with open("debug_trace.log", "a", encoding="utf-8") as f:
            f.write(error_msg + "\n")
        with open("last_error.txt", "w", encoding="utf-8") as f:
            f.write(error_msg)
        
        # 🛡️ Update DB to error state so frontend knows it failed
        try:
            # Assuming sim_id is the first argument in args
            if args:
                sim_id = args[0]
                update_simulation(sim_id, "error", {
                    "status": "error",
                    "summary": f"系統錯誤: {str(e)}",
                    "score": 0,
                    "intent": "Error",
                    "genesis": {"total_population": 0, "sample_size": 0, "personas": []},
                    "comments": []
                })
        except:
            pass

async def run_video_audit_task(
    sim_id: str, 
    video_url: str, 
    product_name: str = None, 
    price: str = None,
    description: str = None,
    style: str = "專業穩重",
    language: str = "zh-TW",
    targeting_data: dict = None,
    is_expert_mode: bool = False,
    is_force_random: bool = False,
    analysis_scenario: str = "b2c",
    seed_salt: int = 0
):
    """Background task for video analysis and simulation with full params"""
    try:
        print(f">> [Task] Starting video audit for {video_url} (ID: {sim_id})")
        
        # ⏬ 階段 1：開始下載視頻
        update_simulation(sim_id, "processing", {
            "status": "processing",
            "summary": "📥 正在下載視頻（限制前60秒）...",
            "score": 0,
            "intent": "Processing..."
        })
        
        # 1. AI 視覺審片
        report_data = video_analysis_service.analyze_video_content(video_url)
        
        # [CRITICAL FIX] 完整錯誤攔截（包含 None 和 error 字段）
        # 避免使用錯誤的 citizen_briefing 進行市民模擬
        if not report_data or report_data.get("error"):
            error_type = report_data.get("error", "UNKNOWN_ERROR") if report_data else "NO_RESPONSE"
            error_msg = report_data.get("message", "AI 審片失敗") if report_data else "無回應"
            
            # 根據錯誤類型提供針對性建議
            suggestion_map = {
                "VIDEO_DOWNLOAD_FAILED": "影片下載失敗。請確認：1.連結是否有效 2.是否有防盜鏈限制 3.嘗試上傳本地 MP4 檔案",
                "VIDEO_UNREADABLE": "AI 無法識別影片內容。可能是下載了非影片文件（如 HTML 錯誤頁面）。請更換連結。",
                "UPLOAD_FAILED": "影片上傳至 AI 服務失敗。請稍後重試。",
                "PROCESSING_FAILED": "AI 處理影片時發生錯誤。請嘗試較短或較小的影片。",
            }
            suggestion = suggestion_map.get(error_type, "請嘗試：1.更換有效的影片連結 2.確保連結可直接下載 3.上傳本地 MP4 檔案")
            
            update_simulation(sim_id, "error", {
                "status": "error",
                "summary": f"[{error_type}] {error_msg}",
                "score": 0,
                "intent": "Error",
                "genesis": {"total_population": 0, "sample_size": 0, "personas": []},
                "comments": [],
                "error_details": {
                    "type": error_type,
                    "message": error_msg,
                    "suggestion": suggestion
                }
            })
            print(f">> [Task] Video audit BLOCKED due to error: {error_type} - {error_msg}")
            return
        
        # ⏬ 階段 2：AI 分析完成，開始市民模擬
        update_simulation(sim_id, "processing", {
            "status": "processing",
            "summary": "🤖 AI 視覺分析完成，正在召喚 1,000 位市民進行評估...",
            "score": 0,
            "intent": "Processing..."
        })
             
        # 2. 市民市場模擬 (傳入完整產品資訊與目標市場參數)
        sim_result = video_analysis_service.run_market_simulation(
            report_data, 
            video_url, 
            product_name=product_name, 
            price=price,
            description=description,
            style=style,
            language=language,
            targeting_data=targeting_data,
            is_expert_mode=is_expert_mode,
            is_force_random=is_force_random,
            analysis_scenario=analysis_scenario,
            seed_salt=seed_salt
        )
        
        # 3. 組合最終結果
        final_data = {
            "status": "completed",
            "report": report_data,
            "simulation": sim_result,
            "simulation_logs": sim_result.get("simulation_logs", []),
            # 前端相容性轉換
            "score": sim_result["score"],
            "summary": report_data.get("citizen_briefing", ""),
            "intent": sim_result["decision"],
            "comments": sim_result["top_reviews"],
            "genesis": {
                "total_population": 1000,
                "sample_size": len(sim_result["top_reviews"]),
                "personas": sim_result["top_reviews"]
            }
        }
        update_simulation(sim_id, "completed", final_data)
        print(f">> [Task] Video audit completed for {sim_id}")
    except Exception as e:
        import traceback
        print(f"!! [Task] Video audit failed: {e}\n{traceback.format_exc()}")
        update_simulation(sim_id, "error", {
            "status": "error", 
            "summary": f"處理失敗: {str(e)}"
        })

@router.post("/video-audit")
async def video_audit_endpoint(
    background_tasks: BackgroundTasks,
    url: str = Form(...),
    product_name: str = Form(None),
    price: str = Form(None)
):
    """[New] Video Audit API Endpoint"""
    sim_id = f"video_{str(uuid.uuid4())}"
    
    initial_data = {
        "status": "processing",
        "summary": "正在下載並解析影片內容...",
        "report": {},
        "simulation": {},
        "intent": "Processing...",
        "score": 0,
        "video_url": url # Store URL for history
    }
    create_simulation(sim_id, initial_data)
    
    background_tasks.add_task(run_video_audit_task, sim_id, url, product_name, price)
    
    return {"status": "ok", "sim_id": sim_id}

@router.get("/video-audits/recent")
async def list_recent_video_audits():
    """Fetch recent video audit simulations from DB"""
    from app.core.database import SessionLocal, Simulation
    db = SessionLocal()
    try:
        # Filter by ID prefix "video_"
        audits = db.query(Simulation).filter(Simulation.sim_id.like("video_%")).order_by(Simulation.created_at.desc()).limit(10).all()
        result = []
        for a in audits:
            data = a.data or {}
            result.append({
                "sim_id": a.sim_id,
                "status": a.status,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "score": data.get("score", 0),
                "intent": data.get("intent", "Unknown"),
                "video_url": data.get("video_url", "Unknown")
            })
        return {"audits": result}
    except Exception as e:
        print(f"!! Error fetching recent audits: {e}")
        return {"audits": [], "error": str(e)}
    finally:
        db.close()




@router.get("/citizen/{citizen_id}")
async def get_citizen_data(citizen_id: str):
    """
    根據 ID 查詢市民的完整資料（包括八字命盤、大運等）
    前端 Modal 用此 API 取得完整資料
    """
    citizen = get_citizen_by_id(citizen_id)
    if citizen:
        return citizen
    else:
        return {"error": "Citizen not found", "id": citizen_id}

@router.get("/citizens/genesis")
async def get_all_citizens_endpoint(limit: int = 1000, offset: int = 0):
    """
    [Frontend] 取得所有市民資料 (用於瀏覽頁面)
    """
    try:
        from app.core.database import get_all_citizens, SessionLocal, Citizen
        
        # 🔍 Debug: Check DB Connection directly in the API process
        db = SessionLocal()
        raw_count = db.query(Citizen).count()
        db_url = str(db.get_bind().url)
        # Mask password for security
        safe_db_url = db_url.split("@")[-1] if "@" in db_url else "Unknown"
        db.close()

        citizens = get_all_citizens(limit=limit, offset=offset)
        
        return {
            "citizens": citizens, 
            "total": len(citizens),
            "debug_info": {
                "raw_db_count": raw_count,
                "db_host": safe_db_url,
                "limit_param": limit,
                "fetched_count": len(citizens)
            }
        }
    except Exception as e:
        print(f"❌ Get all citizens failed: {e}")
        return {"citizens": [], "error": str(e)}

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
    files: List[UploadFile] = File(None),
    product_name: str = Form(None),

    price: str = Form(None),
    description: str = Form(None),
    market_prices: str = Form(None),  # JSON 字串格式的市場比價資料
    style: str = Form(None),  # 新增 style 欄位
    language: str = Form("zh-TW"),  # 新增 language 欄位
    targeting: str = Form(None), # JSON string of targeting options
    expert_mode: str = Form("false"), # "true"/"false" string
    force_random: str = Form("false"), # "true"/"false" string
    seed_salt: int = Form(0), # [New] Batch Control Salt
    analysis_scenario: str = Form("b2c"), # "b2c" / "b2b"
    video_url: str = Form(None) # [New] Video URL for integration
):
    print(f"[WEB] trigger_simulation called! salt={seed_salt}, video={video_url}", flush=True)  

    try:
        with open("debug_trace.log", "a", encoding="utf-8") as f:
            f.write(f"👉 [WEB] trigger_simulation called with salt={seed_salt}, expert_mode={expert_mode}\n")
    except Exception as e:
        print(f"Failed to write log: {e}")

    from app.services.line_bot_service import LineBotService
    line_service = LineBotService()

    sim_id = str(uuid.uuid4())
    
    # 🔍 [Ghost Buster] Debug DB Source & Sampling
    try:
        from app.core.database import engine, get_random_citizens
        db_url = str(engine.url)
        print(f"[Ghost] Runtime DB: {db_url}")
        
        # Test Sample
        sample = get_random_citizens(sample_size=5)
        sample_names = [c["name"] for c in sample]
        
        with open("debug_ghost.log", "a", encoding="utf-8") as f:
            f.write(f"\n[{sim_id}] TRIGGERED\n")
            f.write(f"[{sim_id}] DB URL: {db_url}\n")
            f.write(f"[{sim_id}] Sample Check (5): {sample_names}\n")
            if "彭冠宇" in sample_names:
                f.write(f"[{sim_id}] ⚠️ GHOST DETECTED IN SAMPLE!\n")
            else:
                f.write(f"[{sim_id}] ✅ Sample Clean.\n")
                
    except Exception as e:
        print(f"[Ghost] Check Failed: {e}")


    
    # 預先定義 ext，避免 initial_data 引用錯誤
    ext = ""
    if files and len(files) > 0 and files[0].filename:
        ext = files[0].filename.split(".")[-1].lower() if "." in files[0].filename else ""

    
    # 解析市場比價資料
    market_prices_data = None
    if market_prices:
        try:
            import json
            market_prices_data = json.loads(market_prices)
        except:
            pass
            
    # 解析受眾定錨資料
    targeting_data = None
    if targeting:
        try:
            import json
            targeting_data = json.loads(targeting)
        except:
            pass
            
    # 解析 Expert Mode & Force Random
    is_expert_mode = expert_mode.lower() == 'true'
    is_force_random = force_random.lower() == 'true'
    
    # 建立初始狀態
    initial_data = {
        "status": "processing",
        "score": 0,
        "intent": "Calculating...",
        "summary": "AI 正在啟動並讀取您的資料...",
        "genesis": {"total_population": 0, "sample_size": 0, "personas": []},
        "comments": [],
        "product_name": product_name, # 保存用戶輸入
        "price": price,              # 保存用戶輸入
        "description": description,  # 保存用戶輸入
        "video_url": video_url,      # [New] Save video URL
        "market_prices": market_prices_data,


        "simulation_metadata": {
            "style": style,
            "language": language, # 儲存語言設定
            "product_name": product_name, # 冗餘備份，確保前端引用相容
            "source_type": "pdf" if ext == "pdf" or ext in ["docx", "txt"] else "image",
            "targeting": targeting_data,
            "expert_mode": is_expert_mode,
            "force_random": is_force_random,
            "analysis_scenario": analysis_scenario
        }
    }
    # 建立 DB 紀錄
    create_simulation(sim_id, initial_data)
    
    # 讀取檔案
    file_bytes_list = []
    filenames = []
    
    # <--- 關鍵：只有當 files 不為 None 時才執行讀取
    if files:
        for file in files:
            content = await file.read()
            file_bytes_list.append(content)
            filenames.append(file.filename.lower() if file.filename else "")
    
    # 主要檔案 (用於判斷類型)
    main_filename = filenames[0] if filenames else ""
    main_file_bytes = file_bytes_list[0] if file_bytes_list else b""
    
    # 組合 Text Context
    text_context = ""
    if product_name: text_context += f"產品名稱：{product_name}\n"
    if price: text_context += f"建議售價：{price}\n"
    if description: text_context += f"產品描述：{description}\n"
    text_context = text_context.strip() if text_context else None

    # 判斷檔案類型
    from app.utils.document_parser import parse_document, get_file_extension
    ext = get_file_extension(main_filename)
    
    # 文件類型處理 (Word, PPT, TXT)
    document_extensions = ["docx", "pptx", "txt"]
    audio_extensions = ["webm", "mp3", "wav", "m4a", "ogg"]
    
    # [MODE SWITCH] 根據輸入類型選擇處理流程
    
    # ⭐ 純視頻模式：沒有上傳文件，只有 video_url
    if video_url and not file_bytes_list:
        print(f"[WEB] 🎬 Pure Video Mode detected! URL: {video_url}", flush=True)
        
        # 不要同步探測（會超時），直接啟動後台任務
        background_tasks.add_task(
            run_video_audit_task,
            sim_id,
            video_url,
            product_name,
            price,
            description=description,
            style=style,
            language=language,
            targeting_data=targeting_data,
            is_expert_mode=is_expert_mode,
            is_force_random=is_force_random,
            analysis_scenario=analysis_scenario,
            seed_salt=seed_salt
        )
    
    elif ext == "pdf":
        # PDF Processing - use wrapper to catch exceptions
        background_tasks.add_task(
            safe_run_pdf_task, 
            line_service,  # Pass service instance to wrapper
            sim_id, 
            main_file_bytes,
            main_filename,
            product_name or "Unknown Product", 
            price or "Unknown Price",
            description or "",
            market_prices_data,
            style,
            language,
            targeting_data,
            is_expert_mode,
            is_force_random,
            analysis_scenario,
            seed_salt,
            video_url=video_url # [Fix] Use keyword for safety
        )


    elif ext in document_extensions:
        # Word/PPT/TXT: 解析文字後傳給文字分析流程
        parsed_text = parse_document(main_file_bytes, main_filename)
        if parsed_text:
            # 合併解析內容與用戶額外輸入
            full_context = parsed_text
            if text_context:
                full_context = f"{text_context}\n\n---\n\n{parsed_text}"
            background_tasks.add_task(line_service.run_simulation_with_text_data, full_context, sim_id, ext, language)
        else:
            # 設置錯誤狀態
            from app.core.database import update_simulation
            update_simulation(sim_id, "error", {"status": "error", "summary": f"無法解析 {ext.upper()} 文件"})
    elif ext in audio_extensions:
        # 音訊檔: 傳給語音轉文字處理
        background_tasks.add_task(line_service.run_simulation_with_audio_data, main_file_bytes, sim_id, ext, language)
    else:
        # Image Processing (default)
        # NOTE: file_bytes_list is already populated at line 167-172, no need to read again
        # UploadFile can only be read once!
            
        background_tasks.add_task(
            line_service.run_simulation_with_image_data, 
            file_bytes_list, 
            sim_id, 
            text_context=text_context, 
            language=language,
            force_random=is_force_random,
            seed_salt=seed_salt,
            video_url=video_url
        )


        
    return {"status": "ok", "sim_id": sim_id}


@router.post("/generate-description")
async def generate_description(
    files: List[UploadFile] = File(...),
    product_name: str = Form(...),
    price: str = Form(...),
    style: str = Form("professional"),
    language: str = Form("zh-TW")
):
    try:
        from app.services.line_bot_service import LineBotService
        line_service = LineBotService()

        # Read multiple files
        file_bytes_list = []
        for file in files:
            file_bytes_list.append(await file.read())
        
        # Call LineBotService to generate copy with selected style and language
        result = await line_service.generate_marketing_copy(file_bytes_list, product_name, price, style, language)
        
        if "error" in result:
            return {"error": result["error"]}
            
        return result
        
    except Exception as e:
        return {"error": str(e)}

@router.post("/identify-product")
async def identify_product(
    files: List[UploadFile] = File(...),
    language: str = Form("zh-TW")
):
    """
    使用 Gemini 2.5 Pro 識別圖片中的產品名稱並估算市場價格
    """
    try:
        from app.services.line_bot_service import LineBotService
        import base64
        import os
        import requests
        import json
        import re
        import time
        
        line_service = LineBotService()
        
        # 讀取所有圖片
        image_parts = []
        for file in files:
            file_bytes = await file.read()
            # 將圖片轉為 base64
            image_b64 = base64.b64encode(file_bytes).decode('utf-8')
            
            # 判斷 MIME type
            filename = file.filename.lower() if file.filename else ""
            if filename.endswith('.png'):
                mime_type = "image/png"
            elif filename.endswith('.webp'):
                mime_type = "image/webp"
            elif filename.endswith('.gif'):
                mime_type = "image/gif"
            else:
                mime_type = "image/jpeg"
            
            image_parts.append({"inline_data": {"mime_type": mime_type, "data": image_b64}})
            
        # 根據語言設定 Prompt
        lang_config = {
            "en": {
                "desc_instruction": "Describe the product in English (3-8 words)",
                "price_instruction": "Estimate average market price in USD based on global platforms (Amazon, eBay, Walmart)",
                "currency": "USD",
                "price_source_instruction": "Basis for price estimation (short, under 20 words)",
                "fallback_source": "Estimated based on Amazon/eBay market data",
                "market_calibration": "Calibrated with real data from {count} global platforms",
                "prompt_template": """Analyze this product image(s) and answer the following:
1. **Same Product Check**: If multiple images uploaded, are they different angles of the same product, or different products? (If different, focus on the most prominent one)
2. **Product Identification**: What is this product? {desc_instruction}
3. **Price Estimation**: {price_instruction}

Respond ONLY in this JSON format:
{{
  "is_same_product": true/false,
  "product_name": "Product Name in English",
  "estimated_price": number (without currency symbol),
  "currency": "{currency}",
  "price_range": "min-max",
  "price_source": "{price_source_instruction}"
}}

Only return JSON, no other text."""
            },
            "zh-CN": {
                "desc_instruction": "用简短的中文描述（3-8个字）",
                "price_instruction": "根据中国主流电商平台（淘宝、京东、天猫）估算市场平均售价（人民币 CNY）",
                "currency": "CNY",
                "price_source_instruction": "价格估算依据说明（简短30字内）",
                "fallback_source": "根据淘宝/京东同类产品估算",
                "market_calibration": "已连动 {count} 个电商平台真实数据进行校准",
                "prompt_template": """请观察这张（或多张）产品图片，回答以下问题：
1. **是否为同一产品**：如果上传了多张图片，请判断它们是否为同一个产品的不同角度？还是完全不同的产品？（如果是不同产品，请以最显著的那个为主进行回答）
2. **产品识别**：这张图片中的产品是什么？{desc_instruction}
3. **价格估算**：{price_instruction}

请用以下 JSON 格式回答：
{{
  "is_same_product": true/false,
  "product_name": "产品名称",
  "estimated_price": 数字（不含货币符号），
  "currency": "{currency}",
  "price_range": "最低价-最高价",
  "price_source": "{price_source_instruction}"
}}

只回答 JSON，不要加任何其他说明。"""
            },
            "zh-TW": {
                "desc_instruction": "用簡短的中文描述（3-8個字）",
                "price_instruction": "根據台灣主流電商平台（蝦皮、PChome、MOMO）估算市場平均售價（新台幣 TWD）",
                "currency": "TWD",
                "price_source_instruction": "價格估算依據說明（簡短30字內）",
                "fallback_source": "根據蝦皮/PChome同類產品估算",
                "market_calibration": "已連動 {count} 個電商平台真實數據進行校準",
                "prompt_template": """請觀察這張（或多張）產品圖片，回答以下問題：
1. **是否為同一產品**：如果上傳了多張圖片，請判斷它們是否為同一個產品的不同角度？還是完全不同的產品？（如果是不同產品，請以最顯著的那個為主進行回答）
2. **產品識別**：這張圖片中的產品是什麼？{desc_instruction}
3. **價格估算**：{price_instruction}

請用以下 JSON 格式回答：
{{
  "is_same_product": true/false,
  "product_name": "產品名稱",
  "estimated_price": 數字（不含貨幣符號），
  "currency": "{currency}",
  "price_range": "最低價-最高價",
  "price_source": "{price_source_instruction}"
}}

只回答 JSON，不要加任何其他說明。"""
            }
        }
        lc = lang_config.get(language, lang_config["zh-TW"])

        # 構建識別 prompt（根據語言使用對應模板）
        prompt = lc["prompt_template"].format(
            desc_instruction=lc["desc_instruction"],
            price_instruction=lc["price_instruction"],
            currency=lc["currency"],
            price_source_instruction=lc["price_source_instruction"]
        )

        # 調用 Gemini API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {"error": "API Key not configured"}
        
        # 組合 prompt + 圖片
        content_parts = [{"text": prompt}] + image_parts
        
        payload = {
            "contents": [{
                "parts": content_parts
            }],
            "generationConfig": {
                "temperature": 0.3,
                "responseMimeType": "application/json"
            }
        }

        # [Fix] Prioritize Gemini 2.5 Pro as requested by the user
        models = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-flash-latest"]
        api_key = os.getenv("GOOGLE_API_KEY")
        response = None
        last_error = ""
        clean_text = "" 

        raw_text = ""
        for model in models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                print(f"[Identify] Trying model: {model}...", flush=True)
                start_time = time.time()
                response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload, timeout=90)
                duration = time.time() - start_time
                print(f"[Identify] Model {model} responded in {duration:.2f}s with status {response.status_code}", flush=True)
                
                if response.status_code == 200:
                    result = response.json()
                    raw_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    print(f"[Identify] Raw AI output: {raw_text[:200]}...", flush=True)
                    # 清理可能的 markdown 標記
                    clean_text = raw_text.replace('```json', '').replace('```', '').strip()
                    break
                else:
                    last_error = f"{model}: {response.status_code} {response.text[:100]}"
                    print(f"[Identify] Model {model} error: {last_error}", flush=True)
            except Exception as e:
                last_error = str(e)
                print(f"[Identify] Model {model} exception: {last_error}", flush=True)

        if response is not None and getattr(response, "status_code", 0) == 200 and clean_text:
            print(f"[Identify] Attempting to parse JSON: {clean_text[:100]}...", flush=True)
            # 嘗試直接解析
            try:
                data = json.loads(clean_text)
            except json.JSONDecodeError:
                print("[Identify] Direct JSON parse failed, trying regex...", flush=True)
                # 如果直接解析失敗，嘗試用正則表達式提取 JSON
                json_match = re.search(r'\{.*"product_name".*\}', clean_text, re.DOTALL)
                if json_match:
                    try:
                        data = json.loads(json_match.group())
                    except json.JSONDecodeError:
                        data = {}
                else:
                    data = {}
            
            if data.get("product_name"):
                product_name = str(data.get("product_name", "")).strip('"').strip("'").strip()
                estimated_price = data.get("estimated_price", 0) or 0  # Ensure not None
                print(f"[Identify] Product Identified: {product_name}, Est Price: {estimated_price}", flush=True)
                
                # 🔍 新增：搜尋市場真實價格
                from app.services.price_search import search_market_prices_sync
                print(f"[MarketSearch] Starting search for: {product_name}...", flush=True)
                search_start = time.time()
                market_prices = search_market_prices_sync(product_name, estimated_price)
                print(f"[MarketSearch] Completed in {time.time() - search_start:.2f}s. Results: {len(market_prices.get('prices', []))} items found.", flush=True)
                
                # 🛡️ 模型校準：如果搜尋到的平均價格存在且有效，優先採用真實市場數據
                final_estimated_price = estimated_price
                final_price_range = data.get("price_range", "")
                final_price_source = data.get("price_source", lc['fallback_source'])

                if market_prices.get("avg_price") and market_prices["avg_price"] > 0:
                    # 如果搜尋到的平均預算與 AI 估算差異超過 20%，則進行調整
                    avg_p = market_prices["avg_price"]
                    # Ensure estimated_price is not 0 to avoid division issues
                    diff_pct = abs(avg_p - estimated_price) / max(estimated_price, 1)
                    print(f"[Calibration] Market Avg: {avg_p}, Diff: {diff_pct:.2%}", flush=True)
                    if diff_pct > 0.2:
                        print(f"[Calibration] Overriding AI estimate with market average.", flush=True)
                        final_estimated_price = avg_p
                        final_price_range = f"{market_prices['min_price']}-{market_prices['max_price']}"
                        final_price_source = lc['market_calibration'].replace('{count}', str(len(market_prices.get('prices', []))))

                print(f"[Identify] Returning: {product_name}, Price: {final_estimated_price}", flush=True)
                return {
                    "product_name": product_name,
                    "estimated_price": final_estimated_price,
                    "price_range": final_price_range,
                    "price_source": final_price_source,
                    "market_prices": market_prices
                }
            else:
                print(f"[Identify] FAILED: Could not identify product name in data: {data}", flush=True)
                # 最後嘗試：取第一行作為產品名稱
                first_line = clean_text.split('\n')[0].strip()
                return {"error": "AI could not identify the product", "raw_text": raw_text, "product_name": first_line[:30] if first_line else "未知產品"}
        else:
            status_code = getattr(response, "status_code", "Unknown")
            return {"error": f"API Error: {status_code}"}

            
    except Exception as e:
        print(f"[ERROR] Product identification failed: {e}", flush=True)
        return {"error": str(e)}

# Model specifically for this endpoint
from pydantic import BaseModel

class RefineCopyRequest(BaseModel):
    sim_id: str
    current_copy: str
    product_name: str | None = None
    price: str | None = None
    style: str | None = None
    source_type: str | None = "image"
    language: str = "zh-TW" # Default to zh-TW

@router.post("/refine-copy")
async def refine_copy(request: RefineCopyRequest):
    """
    根據模擬結果中的負評，優化文案
    """
    try:
        from app.services.line_bot_service import LineBotService
        from app.core.database import get_simulation
        
        sim_data = get_simulation(request.sim_id)
        if not sim_data:
            return {"error": "Simulation found"}
            
        comments = sim_data.get("arena_comments", [])
        if not comments:
            return {"error": "No comments found in simulation"}
            
        # 準備資料
        line_service = LineBotService()
        product_name = request.product_name or sim_data.get("product_name", "產品")
        price = request.price or str(sim_data.get("price", "未定"))
        style = request.style or sim_data.get("simulation_metadata", {}).get("style", "professional")
        source_type = request.source_type or sim_data.get("simulation_metadata", {}).get("source_type", "image")

        # 執行優化
        result = await line_service.refine_marketing_copy(
            comments=comments, 
            product_name=product_name, 
            price=price,
            original_copy=request.current_copy,
            style=style,
            source_type=source_type,
            language=request.language
        )
        
        return result
        
    except Exception as e:
        print(f"❌ Refine copy failed: {e}")
        return {"error": str(e)}

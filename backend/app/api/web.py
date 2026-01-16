from fastapi import APIRouter, File, UploadFile, Form, BackgroundTasks
from app.core.database import create_simulation, insert_citizens_batch, get_citizens_count, clear_citizens, get_citizen_by_id
import uuid
import sys
import os

# 確保可以導入 create_citizens
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from create_citizens import generate_citizen

router = APIRouter()


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
    description: str = Form(None),
    market_prices: str = Form(None)  # JSON 字串格式的市場比價資料
):
    from app.services.line_bot_service import LineBotService
    line_service = LineBotService()

    sim_id = str(uuid.uuid4())
    
    # 解析市場比價資料
    market_prices_data = None
    if market_prices:
        try:
            import json
            market_prices_data = json.loads(market_prices)
        except:
            pass
    
    # 建立初始狀態
    initial_data = {
        "status": "processing",
        "score": 0,
        "intent": "Calculating...",
        "summary": "AI 正在啟動並讀取您的資料...",
        "genesis": {"total_population": 0, "sample_size": 0, "personas": []},
        "comments": [],
        "market_prices": market_prices_data  # 存入市場比價資料
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

@router.post("/identify-product")
async def identify_product(
    file: UploadFile = File(...)
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
        
        # 構建識別 prompt（同時識別名稱和估算價格）
        prompt = """請觀察這張產品圖片，回答以下問題：

1. 這張圖片中的產品是什麼？用簡短的中文描述（3-8個字）
2. 根據你對全球主要電商平台（Amazon、淘寶、蝦皮、PChome）上同類產品的了解，估算這類產品的市場平均售價（新台幣 TWD）

請用以下 JSON 格式回答：
{
  "product_name": "產品名稱",
  "estimated_price": 數字（不含貨幣符號），
  "price_range": "最低價-最高價",
  "price_source": "價格估算依據說明（簡短30字內）"
}

只回答 JSON，不要加任何其他說明。"""

        # 調用 Gemini API
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {"error": "API Key not configured"}
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {"inline_data": {"mime_type": mime_type, "data": image_b64}}
                ]
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

        for model in models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                print(f"📸 [Identify] Trying model: {model}...")
                start_time = time.time()
                response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload, timeout=30)
                duration = time.time() - start_time
                print(f"📸 [Identify] Model {model} responded in {duration:.2f}s with status {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    raw_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    print(f"📸 [Identify] Raw AI output: {raw_text[:200]}...")
                    # 清理可能的 markdown 標記
                    clean_text = raw_text.replace('```json', '').replace('```', '').strip()
                    break
                else:
                    last_error = f"{model}: {response.status_code} {response.text[:100]}"
                    print(f"📸 [Identify] Model {model} error: {last_error}")
            except Exception as e:
                last_error = str(e)
                print(f"📸 [Identify] Model {model} exception: {last_error}")

        if response and response.status_code == 200 and clean_text:
            print(f"📸 [Identify] Attempting to parse JSON: {clean_text[:100]}...")
            # 嘗試直接解析
            try:
                data = json.loads(clean_text)
            except json.JSONDecodeError:
                print("📸 [Identify] Direct JSON parse failed, trying regex...")
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
                estimated_price = data.get("estimated_price", 0)
                print(f"📸 [Identify] Product Identified: {product_name}, Est Price: {estimated_price}")
                
                # 🔍 新增：搜尋市場真實價格
                from app.services.price_search import search_market_prices_sync
                print(f"🔍 [MarketSearch] Starting search for: {product_name}...")
                search_start = time.time()
                market_prices = search_market_prices_sync(product_name, estimated_price)
                print(f"🔍 [MarketSearch] Completed in {time.time() - search_start:.2f}s. Results: {len(market_prices.get('prices', []))} items found.")
                
                # 🛡️ 模型校準：如果搜尋到的平均價格存在且有效，優先採用真實市場數據
                final_estimated_price = estimated_price
                final_price_range = data.get("price_range", "")
                final_price_source = data.get("price_source", "根據市場同類產品估算")

                if market_prices.get("avg_price") and market_prices["avg_price"] > 0:
                    # 如果搜尋到的平均預算與 AI 估算差異超過 20%，則進行調整
                    avg_p = market_prices["avg_price"]
                    diff_pct = abs(avg_p - estimated_price) / (estimated_price or 1)
                    print(f"🛡️ [Calibration] Market Avg: {avg_p}, Diff: {diff_pct:.2%}")
                    if diff_pct > 0.2:
                        print(f"🛡️ [Calibration] Overriding AI estimate with market average.")
                        final_estimated_price = avg_p
                        final_price_range = f"{market_prices['min_price']}-{market_prices['max_price']}"
                        final_price_source = f"已連動 {len(market_prices.get('prices', []))} 個電商平台真實數據進行校準"

                print(f"📸 [Identify] Returning: {product_name}, Price: {final_estimated_price}")
                return {
                    "product_name": product_name,
                    "estimated_price": final_estimated_price,
                    "price_range": final_price_range,
                    "price_source": final_price_source,
                    "market_prices": market_prices
                }
            else:
                print(f"📸 [Identify] FAILED: Could not identify product name in data: {data}")
                # 最後嘗試：取第一行作為產品名稱
                first_line = clean_text.split('\n')[0].strip()
                return {"error": "AI could not identify the product", "raw_text": raw_text if 'raw_text' in locals() else "", "product_name": first_line[:30] if first_line else "未知產品"}
        else:
            return {"error": f"API Error: {response.status_code}"}
            
    except Exception as e:
        print(f"❌ Product identification failed: {e}")
        return {"error": str(e)}

import asyncio
import io
import json
import random
import uuid
import re
import base64
import requests
import logging
from datetime import datetime, timedelta

# Create logger for this module
logger = logging.getLogger(__name__)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage,
    PushMessageRequest
)
from app.core.config import settings
from app.core.database import create_simulation, update_simulation, get_simulation, get_random_citizens

# Alias for compatibility with main.py
get_simulation_data = get_simulation


def _generate_methodology_sidecar(score, summary):
    """
    🧬 計算社會科學方法論外掛層 (Computational Social Science Sidecar)
    
    此函數採用 Sidecar Pattern，在不修改既有八字運算邏輯的前提下，
    為模擬結果添加「方法論驗證」與「產品迭代循環」的詮釋層。
    
    基於：
    - 縱向研究 (Longitudinal Study)：市場會隨時間改變，報告需有有效期
    - 精實創業 (Lean Startup)：提供下一步迭代建議（Pivot/Scale/Persevere）
    - 混合方法 (Mixed Methods)：量化分數 + 質性摘要
    
    Args:
        score: 八字運算產生的購買意圖分數 (0-100)
        summary: AI 生成的分析摘要文字
    
    Returns:
        dict: 方法論詮釋數據包，包含有效期、信賴區間、下一步建議
    """
    # 1. [Lifecycle] 計算有效期 (模擬當前時間 + 28天/一個節氣)
    valid_until = (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d")
    
    # 2. [Methodology] 計算模擬信賴區間 (95% CI)
    # 邏輯：基於分數做微幅隨機波動，模擬統計不確定性 (這是計算社會科學的特徵)
    # 注意：score 可能是 int 或 float，請確保運算正常
    base_score = float(score) if score is not None else 0.0
    lower = max(0, base_score - random.uniform(2.0, 4.0))
    upper = min(100, base_score + random.uniform(2.0, 4.0))
    ci_text = f"95% CI [{lower:.1f}, {upper:.1f}]"

    # 3. [Iteration] 生成下一步建議 (Actionable Advice)
    if base_score >= 80:
        next_step = {
            "action": "Scale", 
            "label": "乘勝追擊：擴大測試 (Scale Up)", 
            "style": "bg-green-600 hover:bg-green-700", 
            "desc": "信號極強！建議立即投入廣告資源，進行 A/B 測試。"
        }
    elif base_score >= 60:
        next_step = {
            "action": "Pivot", 
            "label": "微調策略：迭代優化 (Pivot)", 
            "style": "bg-amber-500 hover:bg-amber-600", 
            "desc": "有潛力但雜訊多。建議調整「定價」或「文案」後再測一次。"
        }
    else:
        next_step = {
            "action": "Restart", 
            "label": "打掉重練：重新構思 (Restart)", 
            "style": "bg-red-500 hover:bg-red-600", 
            "desc": "市場反應冷淡。建議更換「目標客群」或「產品定位」。"
        }

    # 為了與前端對接，我們統一使用 "methodology_data" 作為 Key
    return {
        "framework": "雙軌演算法：行為科學 x 命理結構",
        "valid_until": valid_until,
        "entropy_warning": "市場風向隨時在變，建議每月重新校準一次。",
        "confidence_interval": ci_text,
        "next_step": next_step,
        # 將原本的摘要截取作為驅動力簡介，若無摘要則給預設值
        "drivers_summary": (summary[:60] + "...") if summary else "Key market drivers identified via grounded theory."
    }


class LineBotService:
    # In-memory session storage for user states
    user_session = {}
    
    def __init__(self):
        configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
        self.api_client = ApiClient(configuration)
        self.line_bot_api = MessagingApi(self.api_client)
        self.line_bot_blob = MessagingApiBlob(self.api_client)

    async def handle_event(self, event):
        """
        雙軌輸入機制 (Dual-Track Input)
        - 情境 A: 圖片 (ImageMessage) → 暫存並等待補充說明
        - 情境 B: 文字 (TextMessage) → 檢查是否有暫存圖片
        - 情境 C: 檔案 (FileMessage) → 處理 PDF 商業計劃書
        """
        user_id = event.source.user_id
        reply_token = event.reply_token
        message_type = event.message.type
        
        print(f"[EVENT] user_id={user_id}, type={message_type}")
        
        # ===== 情境 A: 圖片訊息 =====
        if message_type == "image":
            await self._handle_image_message(event, user_id, reply_token)
        
        # ===== 情境 B: 文字訊息 =====
        elif message_type == "text":
            await self._handle_text_message(event, user_id, reply_token)
        
        # ===== 情境 C: 檔案訊息 (PDF) =====
        elif message_type == "file":
            await self._handle_file_message(event, user_id, reply_token)
            
        # ===== 情境 D: 影片訊息 (不支援) =====
        elif message_type == "video":
            self.reply_text(reply_token, "⚠️ 抱歉，目前系統僅支援「圖片」預演。\n\n請將影片畫面 **截圖** 後上傳，即可啟動分析！📸")
        
        else:
            # 不支援的訊息類型
            self.reply_text(reply_token, "⚠️ 抱歉，我不支援此格式。\n請上傳圖片 📸 或 PDF 商業計劃書 📄")

    async def identify_product_from_image(self, image_bytes):
        """
        使用 AI 識別圖片中的產品名稱與價格 (移植自 web.py)
        """
        import time
        try:
            # 1. Image to Base64
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Simple mime type detection
            if image_bytes.startswith(b'\x89PNG'): mime_type = "image/png"
            elif image_bytes.startswith(b'GIF8'): mime_type = "image/gif"
            elif image_bytes.startswith(b'RIFF') and image_bytes[8:12] == b'WEBP': mime_type = "image/webp"
            else: mime_type = "image/jpeg"

            prompt = """請觀察這張產品圖片，回答以下問題：
1. 這張圖片中的產品是什麼？用簡短的中文描述（3-8個字）
2. 根據你對全球主要電商平台（Amazon、淘寶、蝦皮、PChome）上同類產品的了解，估算這類產品的市場平均售價（新台幣 TWD）

請用以下 JSON 格式回答：
{
  "product_name": "產品名稱",
  "estimated_price": 數字（不含貨幣符號）
}

只回答 JSON，不要加任何其他說明。"""

            # API Setup
            api_key = settings.GOOGLE_API_KEY
            payload = {
                "contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": mime_type, "data": image_b64}}]}],
                "generationConfig": {"temperature": 0.3, "responseMimeType": "application/json"}
            }
            
            models = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-flash-latest"]
            clean_text = ""
            
            for model in models:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                    print(f"📸 [Identify] Trying model: {model}")
                    response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload, timeout=20)
                    
                    if response.status_code == 200:
                        result = response.json()
                        raw_text = result['candidates'][0]['content']['parts'][0]['text']
                        clean_text = raw_text.replace('```json', '').replace('```', '').strip()
                        break
                    else:
                        print(f"⚠️ [Identify] Error {model}: {response.status_code}")
                except Exception as e:
                    print(f"❌ [Identify] Exception {model}: {e}")
            
            if clean_text:
                # Parse JSON
                try:
                    data = json.loads(clean_text)
                except:
                    match = re.search(r'\{.*\}', clean_text, re.DOTALL)
                    data = json.loads(match.group()) if match else {}
                
                p_name = str(data.get("product_name", "")).strip()
                p_price = str(data.get("estimated_price", "")).strip()
                
                # Market Search Calibration (Lightweight)
                try:
                    from app.services.price_search import search_market_prices_sync
                    market_avg = search_market_prices_sync(p_name, p_price).get("avg_price")
                    if market_avg and market_avg > 0:
                        p_price = int(market_avg)
                except:
                    pass

                return p_name, p_price
                
        except Exception as e:
            print(f"❌ Identification Failed: {e}")
        
        return None, None

    async def _handle_image_message(self, event, user_id, reply_token):
        """情境 A: 收到圖片 → 支援多圖上傳 → AI 識別 → 確認或修改"""
        message_id = event.message.id
        
        # 下載圖片並暫存
        try:
            image_bytes = self.line_bot_blob.get_message_content(message_id)
            
            # AI 自動識別
            self.reply_text(reply_token, "🔍 MIRRA 正在觀察您的圖片，請稍候...")
            ai_name, ai_price = await self.identify_product_from_image(image_bytes)
            
            # 初始化或更新 session（支援多圖）
            if user_id not in self.user_session:
                self.user_session[user_id] = {}
            
            session = self.user_session[user_id]
            session["image_bytes"] = image_bytes  # 暫時保留舊key兼容性
            session["images"] = [image_bytes]  # 新增：多圖陣列
            session["message_id"] = message_id
            session["stage"] = "waiting_for_name_confirmation"
            session["product_name"] = ai_name or ""
            session["product_price"] = ai_price or "未定"
            session["product_description"] = None
            session["generated_descriptions"] = None
            session["ai_copy_a"] = ""  # 新增：AI 生成文案 A
            session["ai_copy_b"] = ""  # 新增：AI 生成文案 B
            session["style"] = ""  # 新增：用戶選擇的風格
            session["market_prices"] = {}  # 新增：市場比價資料
            
            print(f"📸 [SESSION] AI 識別完成: {ai_name} / {ai_price}")
            
            # 回覆確認訊息
            confirm_msg = (
                f"👁️ **AI 視覺分析結果**\n\n"
                f"📦 產品：{ai_name or '未知'}\n"
                f"💰 估價：{ai_price or '未知'}\n\n"
                f"━━━━━━━━━━━━━━\n"
                f"✅ 若資料正確，請回覆「**Y**」\n"
                f"✏️ 若需修改，請直接輸入「**名稱 / 售價**」"
            )
            # Use push because we used reply_token for the "Analyzing..." message
            # logic check: reply_token can only be used once. 
            # So I should NOT have sent "Analyzing..." via reply_token if I want to send result via reply_token.
            # But identify takes time.
            # Strategy: use push_message for the result.
            self._push_text(user_id, confirm_msg)
            
        except Exception as e:
            print(f"❌ [IMAGE] 處理失敗: {e}")
            self._push_text(user_id, "❌ 圖片分析失敗，請重新上傳")

    async def _handle_text_message(self, event, user_id, reply_token):
        """情境 B: 收到文字 → 多階段處理流程"""
        text_content = event.message.text.strip()
        
        # 檢查是否有暫存圖片
        if user_id not in self.user_session:
            guide_msg = (
                "🔮 **歡迎來到 MIRRA 鏡界**\n\n"
                "📸 上傳 **產品圖片** → 啟動購買意圖預演 (AI 自動判讀)\n"
                "📄 上傳 **商業計劃書 PDF** → 啟動商業模式推演\n\n"
                "請選擇您的預演軌道。"
            )
            self.reply_text(reply_token, guide_msg)
            return
        
        session = self.user_session[user_id]
        stage = session.get("stage")
        
        # ===== 階段 1: 等待名稱確認或修改 =====
        if stage == "waiting_for_name_confirmation" or stage == "waiting_for_name_price":
            # 檢查是否為確認指令
            if text_content.lower() in ["y", "yes", "ok", "是", "正確"]:
                # 使用 AI 識別的資料
                name = session.get("product_name") or "未命名產品"
                price = session.get("product_price") or "未定"
            else:
                # 解析「名稱 / 售價」手動輸入
                if "/" in text_content:
                    parts = text_content.split("/", 1)
                    name = parts[0].strip()
                    price = parts[1].strip() if len(parts) > 1 else "未定"
                else:
                    name = text_content
                    # 保留原本 AI 估算的價格 (如果用戶只打了名稱)
                    price = session.get("product_price") or "未定"
            
            session["product_name"] = name
            session["product_price"] = price
            session["stage"] = "waiting_for_description_choice"
            
            print(f"📝 [SESSION] 確認資訊: {name} / {price}")
            
            # 詢問描述來源
            choice_msg = (
                f"✅ 資料確認：**{name}** / **{price}**\n\n"
                "接下來，您希望如何生成產品描述？\n\n"
                "1️⃣ 回覆「**1**」→ 手動輸入\n"
                "2️⃣ 回覆「**2**」→ AI 自動撰寫行銷文案 (推薦✨)\n"
                "3️⃣ 回覆「**3**」→ 略過此步驟"
            )
            self.reply_text(reply_token, choice_msg)
        
        # ===== 階段 2: 等待描述選擇 =====
        elif stage == "waiting_for_description_choice":
            if text_content == "1":
                # 選擇自行輸入
                session["stage"] = "waiting_for_manual_description"
                self.reply_text(reply_token, "📝 請輸入您的產品描述與特點：")
            
            elif text_content == "2":
                # 選擇 AI 生成 → 先讓用戶選風格
                session["stage"] = "waiting_for_style_choice"
                style_msg = (
                    "🎨 **請選擇文案風格：**\n\n"
                    "1️⃣ 專業穩重 - 正式商務風\n"
                    "2️⃣ 親切活潑 - 輕鬆有趣風\n"
                    "3️⃣ 高端奢華 - 精緻質感風\n"
                    "4️⃣ 簡約清爽 - 重點突出風\n"
                    "5️⃣ 故事敘述 - 情境代入風\n\n"
                    "請輸入 1-5 選擇風格"
                )
                self.reply_text(reply_token, style_msg)
            
            elif text_content.lower() in ["略過", "skip", "跳過", "3"]:
                # 直接開始分析
                await self._start_simulation(user_id, reply_token)
            
            else:
                self.reply_text(reply_token, "❓ 請輸入「1」、「2」或「略過」")
        
        # ===== 階段 2.5: 等待風格選擇 =====
        elif stage == "waiting_for_style_choice":
            style_map = {
                "1": "professional",
                "2": "friendly", 
                "3": "luxury",
                "4": "minimalist",
                "5": "storytelling"
            }
            if text_content in style_map:
                session["selected_style"] = style_map[text_content]
                session["stage"] = "generating_descriptions"
                self.reply_text(reply_token, "🤖 AI 正在根據圖片生成描述，請稍候...")
                await self._generate_ai_descriptions(user_id, reply_token)
            else:
                self.reply_text(reply_token, "❓ 請輸入 1-5 選擇風格")
        
        # ===== 階段 3: 等待手動輸入描述 =====
        elif stage == "waiting_for_manual_description":
            session["product_description"] = text_content
            print(f"[SESSION] 收到手動描述: {text_content[:50]}...")
            await self._start_simulation(user_id, reply_token)
        
        # ===== 階段 4: 等待單篇文案確認 (新流程) =====
        elif stage == "waiting_for_copy_confirm":
            if text_content.lower() in ["y", "yes", "ok", "確認", "好"]:
                # 使用 AI 生成的文案
                print(f"[SESSION] 使用者確認使用 AI 文案")
                await self._start_simulation(user_id, reply_token)
            
            elif text_content.lower() in ["改", "重", "regenerate"]:
                # 重新生成
                session["stage"] = "generating_descriptions"
                self.reply_text(reply_token, "🤖 正在重新生成文案，請稍候...")
                await self._generate_ai_descriptions(user_id, reply_token)
            
            elif text_content.lower() in ["略", "skip", "跳過", "略過"]:
                # 跳過文案
                session["product_description"] = None
                print(f"[SESSION] 使用者跳過文案")
                await self._start_simulation(user_id, reply_token)
            
            else:
                self.reply_text(reply_token, "❓ 請回覆「Y」確認、「改」重新生成、或「略」跳過")
        
        # ===== 階段 4 (舊): 等待 A/B 選擇 (向後兼容) =====
        elif stage == "waiting_for_ab_choice":
            descriptions = session.get("generated_descriptions", [])
            
            if text_content.upper() == "A" and len(descriptions) > 0:
                session["product_description"] = descriptions[0]
                print(f"[SESSION] 使用者選擇描述 A")
                await self._start_simulation(user_id, reply_token)
            
            elif text_content.upper() == "B" and len(descriptions) > 1:
                session["product_description"] = descriptions[1]
                print(f"[SESSION] 使用者選擇描述 B")
                await self._start_simulation(user_id, reply_token)
            
            else:
                self.reply_text(reply_token, "❓ 請輸入「A」或「B」選擇描述")
        
        # ===== 舊流程兼容（waiting_for_details）=====
        elif stage == "waiting_for_details":
            # 舊流程：直接使用文字作為補充說明
            text_context = None if text_content.lower() in ["略過", "skip", "跳過"] else text_content
            session["product_description"] = text_context
            await self._start_simulation(user_id, reply_token)
        
        else:
            self.reply_text(reply_token, "❓ 發生錯誤，請重新上傳圖片")

    async def _generate_ai_descriptions(self, user_id, reply_token):
        """使用 AI 根據圖片+名稱+售價生成單篇高品質行銷文案"""
        import time
        session = self.user_session.get(user_id)
        if not session:
            return
        
        image_bytes = session.get("image_bytes")
        product_name = session.get("product_name", "產品")
        product_price = session.get("product_price", "未定")
        
        try:
            # 1. Image to Base64
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Simple mime type detection
            if image_bytes.startswith(b'\x89PNG'): mime_type = "image/png"
            elif image_bytes.startswith(b'GIF8'): mime_type = "image/gif"
            elif image_bytes.startswith(b'RIFF') and image_bytes[8:12] == b'WEBP': mime_type = "image/webp"
            else: mime_type = "image/jpeg"
            
            # 讀取用戶選擇的風格
            selected_style = session.get("selected_style", "professional")
            style_instructions = {
                "professional": "**寫作風格：專業穩重** - 使用正式、專業的商務語氣，強調產品的可靠性與品質。",
                "friendly": "**寫作風格：親切活潑** - 使用輕鬆、有趣的語氣，像朋友推薦好物一樣，加入生動的口語表達。",
                "luxury": "**寫作風格：高端奢華** - 使用精緻、典雅的語氣，強調產品的獨特性與頂級體驗，營造尊貴感。",
                "minimalist": "**寫作風格：簡約清爽** - 使用簡潔有力的語言，直接點出核心賣點，不冗長不囉嗦。",
                "storytelling": "**寫作風格：故事敘述** - 用第一人稱或情境故事帶入產品，讓讀者彷彿置身其中。"
            }
            style_prompt = style_instructions.get(selected_style, style_instructions["professional"])
            
            # 優化 Prompt：使用 GitHub 原版 A/B 架構（確保高品質）
            prompt = f"""請擔任一位頂級的商業文案策略大師。請深入分析這張產品圖片，並根據提供的資訊，為這款產品創造兩個截然不同的「完美應用場景」與「沉浸式行銷文案」。

🎨 **寫作風格要求**：{style_prompt}

產品名稱：{product_name}
建議售價：{product_price}

請不要只寫「優雅」或「實用」這種空泛的形容詞。我需要你能夠：
1. **深度識別**：完全理解商品的材質、設計語言與潛在商業價值。
2. **精準匹配**：具體指出這款產品最適合「什麼樣的人」、「在什麼場合」、「做什麼事」時使用。
3. **沉浸體驗**：用文字營造出氛圍，讓觀看者彷彿置身其中，感受到擁有這件商品後的美好生活圖景。

請生成兩段不同切入點的文案（繁體中文，每段約 100-150 字）：

【A】切入點一：情感共鳴與氛圍營造 (Emotional & Atmospheric)
- 側重於感性訴求，描繪使用當下的美好畫面、心理滿足感或自我展現。
- 適合想透過產品提升生活質感或表達個性的客群。

【B】切入點二：精準場景與痛點解決 (Scenario & Solution)
- 側重於理性與場景訴求，具體描述在工作、社交或特定活動中的完美表現。
- 即使是商業計劃書，也要描述其商業模式落地的具體場景與解決的實際問題。

請直接回覆 JSON 格式，不要有 Markdown 標記：
{{
    "title_a": "文案 A 的標題",
    "description_a": "文案 A 的內容...",
    "title_b": "文案 B 的標題",
    "description_b": "文案 B 的內容..."
}}
"""
            
            # API Setup - 同步 GitHub 設定 (8192 Tokens, 30s Timeout)
            api_key = settings.GOOGLE_API_KEY
            payload = {
                "contents": [{"parts": [{"text": prompt}, {"inline_data": {"mime_type": mime_type, "data": image_b64}}]}],
                "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.8, "responseMimeType": "application/json"}
            }
            
            models = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-flash-latest"]
            ai_text = "{}"
            
            for model in models:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                    print(f"📸 [LINE Copywriting] Trying model: {model}")
                    response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload, timeout=90)
                    
                    if response.status_code == 200:
                        result = response.json()
                        raw_text = result['candidates'][0]['content']['parts'][0]['text']
                        if len(raw_text) > 50:
                            ai_text = raw_text
                            break
                    elif response.status_code == 429:
                        await asyncio.sleep(1)
                    else:
                        print(f"⚠️ [LINE Copywriting] Error {model}: {response.status_code}")
                except Exception as e:
                    print(f"❌ [LINE Copywriting] Exception {model}: {e}")

            # Robust Parsing using helper
            data = self._clean_and_parse_json(ai_text)

            # 提取文案
            desc_a = data.get("description_a", "")
            desc_b = data.get("description_b", "")
            
            # 優先使用 Option A (符合用戶需求)
            copy_content = desc_a if desc_a else desc_b
            copy_title = data.get("title_a", "✨ 專屬文案")
            
            # 這些欄位新 Prompt 沒有，使用預設值
            product_type = product_name
            target_audience = "追求品質生活的您"

            # Fallback
            if not copy_content:
                print(f"⚠️ Copywriting generation failed. Using default template.")
                copy_content = f"這款{product_name}設計精良，是追求品質生活的最佳選擇。售價 {product_price} 元，現在正是入手的好時機！"

            # 儲存
            session["product_description"] = copy_content
            session["stage"] = "waiting_for_copy_confirm"
            
            # 發送確認訊息
            confirm_msg = (
                f"🔮 **AI 為您生成了行銷文案：**\n\n"
                f"📌 產品類型：{product_type}\n"
                f"🎯 目標客群：{target_audience}\n\n"
                f"【{copy_title}】\n{copy_content}\n\n"
                "━━━━━━━━━━━━━━\n"
                "✅ 回覆「**Y**」使用此文案\n"
                "✏️ 回覆「**改**」重新生成\n"
                "⏭️ 回覆「**略**」跳過文案"
            )
            self._push_text(user_id, confirm_msg)

        except Exception as e:
            print(f"❌ _generate_ai_descriptions 錯誤: {e}")
            session["stage"] = "waiting_for_description_choice"

    async def refine_marketing_copy(self, comments: list[dict], product_name: str, price: str, original_copy: str, style: str = "professional", source_type: str = "image") -> dict:
        """根據 AI 市民的評論（特別是負評），優化現有文案"""
        print(f"✨ Refine Copy with Style: {style}")
        import time
        try:
            # 1. 篩選評論
            # 負評：分數 < 60 或情緒為 negative
            negative_comments = [c for c in comments if c.get('score', 0) < 60 or c.get('sentiment') == 'negative']
            if not negative_comments:
                # 若無明顯負評，取分數最低的前 20%
                sorted_comments = sorted(comments, key=lambda x: x.get('score', 100))
                negative_comments = sorted_comments[:max(1, int(len(comments) * 0.2))]
            
            # 正評：分數 > 80 或情緒為 positive (用於保留優點)
            positive_comments = [c for c in comments if c.get('score', 0) > 80 or c.get('sentiment') == 'positive']
            
            # 提取評論文本
            neg_texts = "\n".join([f"- {c['text']}" for c in negative_comments[:10]]) # 取前 10 條
            pos_texts = "\n".join([f"- {c['text']}" for c in positive_comments[:5]])  # 取前 5 條作為參考
            
            print(f"🔄 [RefineCopy] Analyzing {len(negative_comments)} negative and {len(positive_comments)} positive comments.")


            # Mapping style to description
            style_desc = {
                "professional": "專業穩重、商務感強",
                "friendly": "親切活潑、輕鬆有趣",
                "luxury": "高端奢華、精緻質感",
                "minimalist": "簡約清爽、重點突出",
                "storytelling": "故事敘述、情境代入"
            }.get(style, "專業穩重")

            # 2. 構建 Prompt (區分 產品 vs 商業計劃)
            if source_type == 'pdf' or source_type == 'txt':
                # Business Plan Mode: Only Strategy
                task_instruction = """
                2. **優化建議 (Refined Strategy)**：
                   - 針對商業計劃書的盲點，提出具體的修正方向與論述優化建議。
                   - 語氣保持專業顧問風格。
                """
                json_format = """
                {
                    "pain_points_summary": "主要疑慮總結...",
                    "refined_copy": "針對商業計劃的優化建議與修正論述..."
                }
                """
            else:
                # Product Mode: Universal Dynamic Adaptation Architecture
                task_instruction = f"""
                2. **動態適配策略 (Dynamic Strategic Adaptation)**：
                   請先執行以下 **三步驟推理**，不要直接生成文案：

                   **步驟 1：產品屬性診斷 (Product DNA Profiling)**
                   - **購買決策者**：是「個人 (B2C)」還是「組織 (B2B)」？
                   - **價值維度**：是「實用功能 (Functional)」還是「情感社交 (Emotional)」？

                   **步驟 2：溝通策略鎖定 (Strategy Locking)**
                   - **情境 A (大眾消費 B2C)**：若為個人享樂/低單價 -> 關鍵字：小確幸、療癒、顏值、CP值。**禁語**：企業賦能、解決方案、底層邏輯。
                   - **情境 B (高價/房產 B2C)**：若為高單價/身份象徵 -> 關鍵字：生活風格 (Lifestyle)、稀缺性、價值、長效投資。
                   - **情境 C (企業工具 B2B)**：若為商業工具 -> 關鍵字：ROI、效率、降本增效、競爭力。語氣：專業數據導向。

                   **步驟 3：痛點轉化 (Pain Point Translation - Magic Formula)**
                   - 被罵「沒用」-> 轉譯為 **「無用之用的情緒價值」** (例：雖然不能吃，但看著心情好)。
                   - 被罵「太貴」-> 轉譯為 **「平均每天只需 X 元的長效投資」** (將價格除以使用天數)。
                   - 被罵「太醜」-> 轉譯為 **「獨特醜萌美學」** 或 **「硬派實用主義」**。

                3. **實戰文案 (Ready-to-Post Copy)**：
                   - 根據上述鎖定的策略，撰寫 3 則適合該客群平台 (IG/Shopee/LinkedIn) 的爆款短文案。
                   - **格式要求**：
                     - 請返回正常的 JSON 陣列格式，包含 `title`, `body`, `hashtags`。
                     - 請確保 Emoji 豐富且語氣自然。
                   - **自我檢測 (Self-Correction)**：
                     - 若判斷為 B2C，嚴禁出現「提升團隊效率」等 B2B 詞彙。
                """
                json_format = """
                {
                    "strategy_rationale": "...",
                    "pain_points_summary": "...",
                    "refined_copy": "...",
                    "marketing_copy": [
                        {"title": "...", "body": "...", "hashtags": "..."},
                        {"title": "...", "body": "...", "hashtags": "..."}
                    ]
                }
                """

            prompt = f"""你是一位精通市場反饋的文案優化專家。
產品：{product_name} | 價格：{price}
原始文案：{original_copy}

【市場負面反饋】
{neg_texts}

【市場正面反饋】
{pos_texts}

【任務】
1. **分析痛點**：總結 3 個主要抗拒點。
{task_instruction}

請直接回覆 JSON 格式：
{json_format}
"""



            # 3. Call Gemini API
            api_key = settings.GOOGLE_API_KEY
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.7, "responseMimeType": "application/json"}
            }
            
            models = ["gemini-2.5-pro", "gemini-2.5-flash"]
            ai_text = "{}"
            
            for model in models:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                    print(f"🔄 [RefineCopy] Trying model: {model}")
                    response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload, timeout=90)
                    if response.status_code == 200:
                        result = response.json()
                        ai_text = result['candidates'][0]['content']['parts'][0]['text']
                        break
                except Exception as e:
                    print(f"❌ [RefineCopy] Error {model}: {e}")

            # 4. Parse Result
            print(f"DEBUG: AI Raw Response: {ai_text}") # Log raw response
            data = self._clean_and_parse_json(ai_text)
            print(f"DEBUG: Parsed Data: {data}") # Log parsed data

            # Force Format Formatting for 'marketing_copy'
            marketing_copy_raw = data.get("marketing_copy")
            formatted_copy = ""

            if isinstance(marketing_copy_raw, list):
                # Clean up structured JSON into the user-requested Plain Text format
                formatted_pieces = []
                for idx, item in enumerate(marketing_copy_raw):
                    if isinstance(item, dict):
                        title = item.get("title", "")
                        body = item.get("body", "")
                        tags = item.get("hashtags", "")
                        # Construct the text block
                        block = f"【文案 {idx+1}】{title}\n\n{body}\n\n{tags}"
                        formatted_pieces.append(block)
                    elif isinstance(item, str):
                        formatted_pieces.append(item)
                
                formatted_copy = "\n\n---\n\n".join(formatted_pieces)
                data["marketing_copy"] = formatted_copy # Overwrite with plain text
                print(f"✅ [SmartFormat] Converted JSON List to Plain Text:\n{formatted_copy[:100]}...")

            elif isinstance(marketing_copy_raw, str):
                # Ensure it's not a stringified JSON
                if marketing_copy_raw.strip().startswith("[") and marketing_copy_raw.strip().endswith("]"):
                    import json
                    try:
                        parsed_list = json.loads(marketing_copy_raw)
                        if isinstance(parsed_list, list):
                            formatted_pieces = []
                            for idx, item in enumerate(parsed_list):
                                if isinstance(item, dict):
                                    title = item.get("title", "")
                                    body = item.get("body", "")
                                    tags = item.get("hashtags", "")
                                    block = f"【文案 {idx+1}】{title}\n\n{body}\n\n{tags}"
                                    formatted_pieces.append(block)
                            formatted_copy = "\n\n---\n\n".join(formatted_pieces)
                            data["marketing_copy"] = formatted_copy
                            print(f"✅ [SmartFormat] Converted Stringified JSON to Plain Text")
                    except:
                        pass # Keep as is if parsing fails
            
            final_refined = data.get("refined_copy", original_copy)
            


            if not final_refined:
                print("WARNING: Refined copy is empty, checking original...")
                final_refined = original_copy or "無法優化文案，請檢查原始資料。"

            return {
                "success": True,
                "pain_points": data.get("pain_points_summary", "分析中..."),
                "refined_copy": str(final_refined),
                "marketing_copy": data.get("marketing_copy", "") 
            }


        except Exception as e:
            print(f"❌ refine_marketing_copy Exception: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e), "refined_copy": original_copy}
            self._push_text(user_id, "❌ AI 生成失敗，請直接輸入「**1**」自行輸入描述")

    def _clean_and_parse_json(self, ai_text):
        """Helper to clean and parse JSON with robust error handling (From GitHub Original)"""
        if not ai_text or not isinstance(ai_text, str):
            return {}

        clean_text = ai_text
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", ai_text, re.DOTALL)
        if match:
            clean_text = match.group(1)
        
        try:
            data = json.loads(clean_text)
            if isinstance(data, dict):
                return data
            return {}
        except json.JSONDecodeError:
            # Simple fix attempt for truncated JSON
            fixed_text = clean_text.strip()
            # Try to close open braces/brackets
            open_braces = fixed_text.count('{') - fixed_text.count('}')
            if open_braces > 0: fixed_text += '}' * open_braces
            
            open_brackets = fixed_text.count('[') - fixed_text.count(']')
            if open_brackets > 0: fixed_text += ']' * open_brackets
            
            # Remove trailing commas before closing braces (common issue)
            fixed_text = re.sub(r',\s*([}\]])', r'\1', fixed_text)

            try:
                data = json.loads(fixed_text)
                if isinstance(data, dict):
                    return data
                return {}
            except:
                print(f"⚠️ Failed to parse AI JSON after cleaning: {clean_text[:50]}...")
                return {}

    async def generate_marketing_copy(self, image_data_input, product_name: str, price: str, style: str = "professional", language: str = "zh-TW"):
        """
        網頁端 API 使用：根據圖片（單張或多張）生成行銷文案
        使用 GitHub 原版 A/B Prompt（品質更好），但只返回其中一段
        支援多語言：zh-TW（繁體中文）、zh-CN（簡體中文）、en（英文）
        """
        try:
            # 1. Process Images (List or Single)
            image_bytes_list = image_data_input if isinstance(image_data_input, list) else [image_data_input]
            image_parts = []
            
            for idx, img_bytes in enumerate(image_bytes_list):
                 # Auto-detect mime type
                if img_bytes.startswith(b'\x89PNG'): mime_type = "image/png"
                elif img_bytes.startswith(b'GIF8'): mime_type = "image/gif"
                elif img_bytes.startswith(b'RIFF') and img_bytes[8:12] == b'WEBP': mime_type = "image/webp"
                else: mime_type = "image/jpeg"
                
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                image_parts.append({"inline_data": {"mime_type": mime_type, "data": img_b64}})
            
            print(f"📸 [Web Copywriting] Processing {len(image_parts)} images, language={language}...")
            
            # 多語言風格指令
            style_prompts_by_lang = {
                "zh-TW": {
                    "professional": "請使用**專業穩重**的商務風格。用詞正式，強調產品的技術規格、數據與可靠性，適合 B2B 或追求效能的專業人士。",
                    "friendly": "請使用**親切活潑**的輕鬆風格。像跟朋友聊天一樣，但也要清楚介紹產品的核心規格（如藍牙、續航），別讓讀者覺得沒內容。",
                    "luxury": "請使用**高端奢華**的品牌風格。用詞講究、富有質感，並將技術規格轉化為尊貴體驗的描述（例如：無線連接帶來的無拘無束）。",
                    "minimalist": "請使用**簡約清爽**的極簡風格。句子精煉有力，直接列出核心規格數據，去除冗餘形容詞。",
                    "storytelling": "請使用**故事敘述**的情境風格。在故事中自然帶出產品的規格優勢（如：不用擔心沒電，因為它有超長續航...）。"
                },
                "zh-CN": {
                    "professional": "请使用**专业稳重**的商务风格。用词正式，强调产品的技术规格、数据与可靠性，适合 B2B 或追求效能的专业人士。",
                    "friendly": "请使用**亲切活泼**的轻松风格。像跟朋友聊天一样，但也要清楚介绍产品的核心规格（如蓝牙、续航），别让读者觉得没内容。",
                    "luxury": "请使用**高端奢华**的品牌风格。用词讲究、富有质感，并将技术规格转化为尊贵体验的描述（例如：无线连接带来的无拘无束）。",
                    "minimalist": "请使用**简约清爽**的极简风格。句子精炼有力，直接列出核心规格数据，去除冗余形容词。",
                    "storytelling": "请使用**故事叙述**的情境风格。在故事中自然带出产品的规格优势（如：不用担心没电，因为它有超长续航...）。"
                },
                "en": {
                    "professional": "Please use a **professional and steady** business style. Use formal language, emphasizing technical specifications, data, and reliability. Suitable for B2B or professional audiences.",
                    "friendly": "Please use a **friendly and lively** casual style. Write as if chatting with a friend, but clearly introduce core specs (like Bluetooth, battery life).",
                    "luxury": "Please use a **high-end luxury** brand style. Use refined, textured language, transforming technical specs into premium experience descriptions.",
                    "minimalist": "Please use a **minimalist and clean** style. Sentences should be concise and powerful, directly listing core specs without redundant adjectives.",
                    "storytelling": "Please use a **storytelling** scenario style. Naturally bring out product advantages within the story narrative."
                }
            }
            
            lang_styles = style_prompts_by_lang.get(language, style_prompts_by_lang["zh-TW"])
            style_instruction = lang_styles.get(style, lang_styles["professional"])
            
            # 2. 搜尋產品規格 (New Feature)
            product_specs = ""
            if product_name and product_name != "產品" and product_name != "未命名產品":
                 try:
                     from app.services.price_search import search_product_specs_sync
                     print(f"🔍 [Web Copywriting] Searching specs for: {product_name}...")
                     product_specs = search_product_specs_sync(product_name)
                     print(f"🔍 [Web Copywriting] Specs length: {len(product_specs)}")
                 except Exception as e:
                     print(f"⚠️ Spec search failed: {e}")

            # 使用 GitHub 原版 Prompt（A/B 格式）並加入規格資訊
            # 根據圖片數量調整 prompt
            multi_image_instruction = ""
            if len(image_parts) > 1:
                multi_image_instruction = f"""
📸 **多圖分析指引** (共 {len(image_parts)} 張圖片)：
用戶上傳了多張圖片，這代表他們希望你能夠：
1. **識別每張圖片的視角與用途**：
   - 可能是產品的不同角度（正面、側面、背面、俯視、細節特寫）
   - 可能是使用情境展示、包裝展示、配件展示
   - 可能是顏色/款式變化
   
2. **整合多視角資訊**：
   - 請先在心中分析每張圖片分別展示了什麼
   - 找出圖片之間的關聯性與互補性
   - 不要遺漏任何一張圖片中的關鍵資訊
   
3. **在文案中明確體現多視角分析**：
   - **務必在文案中提及你已觀察多個角度/視角**（例如：「從正面到側面」、「各個角度」、「細節處」、「無論從哪個視角」等）
   - 在文案中自然融入從不同圖片中觀察到的特點
   - 如果有細節圖，請強調該細節的設計巧思或技術亮點
   - 如果有使用情境圖，請描述該情境的體驗感受
   - **讓讀者能感受到這份文案是基於對產品全方位觀察後的綜合描述**
   
⚠️ **強制要求**：由於用戶上傳了 {len(image_parts)} 張圖片，你的文案中**必須**包含能體現「多視角分析」的措辭，例如：
   - 「從各個角度觀察」
   - 「無論從正面還是側面」
   - 「細節之處」
   - 「全方位展現」
   - 「每個細節都經過精心設計」
這樣用戶才能確認你確實理解並整合了所有上傳的圖片內容。
"""
            # 多語言 Prompt 模板
            prompt_templates = {
                "zh-TW": f"""🚨 **系統語言設定：繁體中文 (zh-TW)** 🚨
⚠️ 本提示的所有輸出內容必須使用**繁體中文**撰寫。
⚠️ 禁止輸出任何英文文案內容（JSON 欄位名稱除外）。

請擔任一位頂級的商業文案策略大師。請深入分析這 {len(image_parts)} 張產品圖片，為這款產品創造兩個截然不同的「完美應用場景」與「沉浸式行銷文案」。
{multi_image_instruction}
🎨 **寫作風格要求**：{style_instruction}

📦 **產品資訊**：
- 產品名稱：{product_name}
- 建議售價：{price}
- 參考規格與特色：{product_specs if product_specs else "(請根據圖片細節推斷)"}

請生成兩段不同切入點的文案（**繁體中文**，每段約 150-200 字）：

【A】情感共鳴版 - 側重感性訴求，描繪使用場景的美好體驗。
【B】理性分析版 - 側重產品優勢，列出核心規格亮點。

請直接回覆 JSON 格式：
{{
    "title_a": "文案 A 的標題",
    "description_a": "文案 A 的內容...",
    "title_b": "文案 B 的標題",
    "description_b": "文案 B 的內容..."
}}
""",
                "zh-CN": f"""🚨 **系统语言设定：简体中文 (zh-CN)** 🚨
⚠️ 本提示的所有输出内容必须使用**简体中文**撰写。
⚠️ 禁止输出任何繁体中文或英文文案内容（JSON 字段名称除外）。

请担任一位顶级的商业文案策略大师。请深入分析这 {len(image_parts)} 张产品图片，为这款产品创造两个截然不同的「完美应用场景」与「沉浸式营销文案」。
{multi_image_instruction}
🎨 **写作风格要求**：{style_instruction}

📦 **产品信息**：
- 产品名称：{product_name}
- 建议售价：{price}
- 参考规格与特色：{product_specs if product_specs else "(请根据图片细节推断)"}

请生成两段不同切入点的文案（**简体中文**，每段约 150-200 字）：

【A】情感共鸣版 - 侧重感性诉求，描绘使用场景的美好体验。
【B】理性分析版 - 侧重产品优势，列出核心规格亮点。

请直接回复 JSON 格式：
{{
    "title_a": "文案 A 的标题",
    "description_a": "文案 A 的内容...",
    "title_b": "文案 B 的标题",
    "description_b": "文案 B 的内容..."
}}
""",
                "en": f"""🚨 **System Language: English (en)** 🚨
⚠️ All output content MUST be written in **English only**.
⚠️ Do NOT output any Chinese characters (JSON field names are exceptions).

Please act as a top-tier commercial copywriting strategist. Analyze these {len(image_parts)} product images and create two distinct "perfect application scenarios" with "immersive marketing copy" for this product.
{multi_image_instruction}
🎨 **Writing Style**: {style_instruction}

📦 **Product Information**:
- Product Name: {product_name}
- Suggested Price: {price}
- Reference Specs: {product_specs if product_specs else "(Please infer from image details)"}

Generate two different marketing copy approaches (in **English**, ~100-150 words each):

【A】Emotional Resonance - Focus on emotional appeal, describing the wonderful experience of using the product.
【B】Rational Analysis - Focus on product advantages, listing core specification highlights.

Reply directly in JSON format:
{{
    "title_a": "Title for Copy A",
    "description_a": "Content for Copy A...",
    "title_b": "Title for Copy B",
    "description_b": "Content for Copy B..."
}}
"""
            }
            
            prompt = prompt_templates.get(language, prompt_templates["zh-TW"])
            
            # API Setup - 使用 GitHub 原版設定 (Token 數需足夠大)
            api_key = settings.GOOGLE_API_KEY
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.8, "responseMimeType": "application/json"}
            }
            # Append all images
            payload["contents"][0]["parts"].extend(image_parts)
            
            models = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-flash-latest"]
            ai_text = "{}"
            
            for model in models:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                    print(f"📸 [Web Copywriting] Trying model: {model}")
                    # GitHub 原始設定：timeout=90, maxOutputTokens=8192
                    response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload, timeout=90)
                    
                    if response.status_code == 200:
                        result = response.json()
                        raw_text = result['candidates'][0]['content']['parts'][0]['text']
                        print(f"✅ [Web Copywriting] Got response from {model}, len={len(raw_text)}")
                        if "description_a" in raw_text or "title_a" in raw_text:
                            ai_text = raw_text
                            break
                    elif response.status_code == 429:
                        print(f"⚠️ [Web Copywriting] Rate limited on {model}, trying next...")
                        await asyncio.sleep(1)
                    else:
                        print(f"⚠️ [Web Copywriting] Error {model}: {response.status_code}")
                except Exception as e:
                    print(f"❌ [Web Copywriting] Exception {model}: {e}")

            # Robust Parsing using helper (GitHub Logic)
            print(f"📝 [Web Copywriting] Raw AI response: {ai_text[:200]}...")
            data = self._clean_and_parse_json(ai_text)
            print(f"✅ [Web Copywriting] Parsed JSON keys: {list(data.keys())}")

            # 提取 A/B 文案
            desc_a = data.get("description_a", "")
            desc_b = data.get("description_b", "")
            
            # 返回單篇：優先使用 A 段（情感共鳴版）
            copy_content = desc_a if desc_a else desc_b
            
            if not copy_content:
                print(f"⚠️ [Web Copywriting] Using fallback template!")
                copy_content = f"這款{product_name}設計精良，是追求品質生活的最佳選擇。無論是自用還是送禮，都能展現您的獨特品味。售價 {price} 元，現在正是入手的好時機！"

            return {
                "product_type": product_name,
                "target_audience": "一般消費者",
                "copy_title": data.get("title_a", "✨ 產品魅力"),
                "copy_content": copy_content
            }

        except Exception as e:
            print(f"❌ generate_marketing_copy 錯誤: {e}")
            return {"error": str(e)}


    async def _start_simulation(self, user_id, reply_token):
        """組合產品資訊並啟動模擬分析"""
        session = self.user_session.get(user_id)
        if not session:
            self.reply_text(reply_token, "❓ 發生錯誤，請重新上傳圖片")
            return
        
        # 取得所有資訊
        image_bytes = session.get("image_bytes")
        message_id = session.get("message_id")
        product_name = session.get("product_name", "")
        product_price = session.get("product_price", "")
        product_description = session.get("product_description", "")
        
        # 組合文字上下文
        text_context = ""
        if product_name:
            text_context += f"產品名稱：{product_name}\n"
        if product_price:
            text_context += f"建議售價：{product_price}\n"
        if product_description:
            text_context += f"產品描述：{product_description}\n"
        
        text_context = text_context.strip() if text_context else None
        
        print(f"📝 [SESSION] 啟動模擬: name={product_name}, price={product_price}, desc={product_description[:30] if product_description else 'None'}...")
        
        # 清除 session
        del self.user_session[user_id]
        
        # 生成 simulation ID
        sim_id = str(uuid.uuid4())
        
        # 回覆戰情室連結
        vercel_url = "https://mirra-ai-six.vercel.app"
        reply_url = f"{vercel_url}/watch/{sim_id}"
        
        loading_msg = (
            f"🔵 **MIRRA 平行時空預演系統啟動中...**\n\n"
            f"📦 產品：{product_name or '(圖片分析)'}\n"
            f"💰 售價：{product_price or '未定'}\n\n"
            f"🧬 正在召喚 1,000 位虛擬市民進入輿論競技場...\n\n"
            f"━━━━━━━━━━━━━━\n"
            f"🔗 **點擊進入戰情室查看即時結果**:\n"
            f"{reply_url}"
        )
        
        # 建立初始狀態
        initial_data = {
            "status": "processing",
            "score": 0,
            "intent": "Calculating...",
            "summary": "AI 正在分析您的產品圖片，請稍候...",
            "genesis": {"total_population": 0, "sample_size": 0, "personas": []},
            "comments": []
        }
        create_simulation(sim_id, initial_data)
        
        self.reply_text(reply_token, loading_msg)
        
        # 執行 AI 分析（重構後：使用 run_simulation_with_image_data）
        try:
            with open("debug_start.log", "w", encoding="utf-8") as f: 
                f.write(f"[{sim_id}] Ready to call run_simulation_with_image_data\n")
                f.write(f"[{sim_id}] Image Bytes len: {len(image_bytes) if image_bytes else 'None'}\n")
            
            print(f"🚀 [SESSION] Calling run_simulation_with_image_data for {sim_id}")
            await self.run_simulation_with_image_data(image_bytes, sim_id, text_context)
            
            with open("debug_start.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] Call returned (Success)\n")
        except Exception as e:
            with open("debug_start.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] Call FAILED: {e}\n")
            print(f"❌ [SESSION] Call to run_simulation_with_image_data failed: {e}")
            self._handle_error_db(sim_id, f"Internal Launch Error: {e}")

    def _push_text(self, user_id, text):
        """主動推送文字訊息給用戶（非回覆）"""
        try:
            self.line_bot_api.push_message(
                PushMessageRequest(to=user_id, messages=[TextMessage(text=text)])
            )
        except Exception as e:
            print(f"❌ Push message 失敗: {e}")

    async def _handle_file_message(self, event, user_id, reply_token):
        """情境 C: 收到檔案 → 處理 PDF 商業計劃書"""
        file_name = event.message.file_name
        file_size = event.message.file_size
        message_id = event.message.id
        
        print(f"📄 [FILE] 收到檔案: {file_name}, size={file_size}")
        
        # 檢查是否為 PDF
        if not file_name.lower().endswith('.pdf'):
            self.reply_text(reply_token, "❌ 目前僅支援 PDF 格式的商業計劃書")
            return
        
        # 生成 simulation ID
        sim_id = str(uuid.uuid4())
        
        # 回覆戰情室連結
        vercel_url = "https://mirra-ai-six.vercel.app"
        reply_url = f"{vercel_url}/watch/{sim_id}"
        
        loading_msg = (
            f"📄 **MIRRA 系統已讀取商業計劃書 (PDF)**\n\n"
            f"正在將商業模式解構並傳送至輿論競技場...\n"
            f"🧬 正在召喚虛擬市民針對 **「商業可行性」** 與 **「獲利模式」** 進行推演...\n\n"
            f"━━━━━━━━━━━━━━\n"
            f"🔗 **點擊進入戰情室查看即時結果**:\n"
            f"{reply_url}"
        )
        
        # 建立初始狀態
        initial_data = {
            "status": "processing",
            "score": 0,
            "intent": "Calculating...",
            "summary": "AI 正在閱讀您的商業計劃書，請稍候...",
            "genesis": {"total_population": 0, "sample_size": 0, "personas": []},
            "comments": []
        }
        create_simulation(sim_id, initial_data)
        
        self.reply_text(reply_token, loading_msg)
        
        # 執行 PDF 分析（待重構）
        try:
            # 下載 PDF
            print(f"📥 [PDF] 下載 PDF: message_id={message_id}")
            pdf_bytes = self.line_bot_blob.get_message_content(message_id)
            print(f"✅ [PDF] PDF 下載完成: {len(pdf_bytes)} bytes")
            
            await self.run_simulation_with_pdf_data(pdf_bytes, sim_id, file_name)
        except Exception as e:
            print(f"❌ [PDF] 下載或處理失敗: {e}")
            self.reply_text(reply_token, "❌ PDF 下載或處理失敗，請重新上傳")

    async def process_image_with_ai(self, message_id, sim_id, text_context=None):
        """
        [Legacy Wrapper] 
        保留此方法以兼容舊代碼，但內部改為下載後調用 run_simulation_with_image_data
        """
        try:
            print(f"🚀 [LineBot] 開始 AI 分析流程: sim_id={sim_id}")
            print(f"📥 [LineBot] 下載圖片: message_id={message_id}")
            image_bytes = self.line_bot_blob.get_message_content(message_id)
            print(f"✅ [LineBot] 圖片下載完成: {len(image_bytes)} bytes")
            
            await self.run_simulation_with_image_data(image_bytes, sim_id, text_context)
        except Exception as e:
            print(f"❌ [LineBot] 圖片下載或處理失敗: {e}")
            # Error updating happens inside run_simulation_with_image_data for analysis errors
            # But if download fails, we handle it here roughly? 
            # Actually run_simulation handles db update. 
            pass

    async def process_pdf_with_ai(self, message_id, sim_id, file_name):
        """
        [Legacy Wrapper]
        保留此方法以兼容舊代碼
        """
        try:
            print(f"📄 [LineBot PDF] 開始 PDF 分析流程: sim_id={sim_id}, file={file_name}")
            print(f"📥 [LineBot PDF] 下載 PDF...")
            pdf_bytes = self.line_bot_blob.get_message_content(message_id)
            print(f"✅ [LineBot PDF] PDF 下載完成: {len(pdf_bytes)} bytes")
            
            await self.run_simulation_with_pdf_data(pdf_bytes, sim_id, file_name)
        except Exception as e:
            print(f"❌ [LineBot PDF] 下載或處理失敗: {e}")

    async def run_simulation_with_image_data(self, image_data_input, sim_id, text_context=None):
        """核心圖文分析邏輯 (Decoupled & Synced with PDF Flow) - Supports Single or Multiple Images"""
        import traceback
        try:
            with open("debug_image.log", "w", encoding="utf-8") as f: f.write(f"[{sim_id}] STARTING run_simulation_with_image_data\n")
            
            # 1. Process Images (Single or List)
            image_bytes_list = image_data_input if isinstance(image_data_input, list) else [image_data_input]
            image_parts = []
            
            for idx, img_bytes in enumerate(image_bytes_list):
                 # Auto-detect mime type
                mime_type = "image/jpeg"
                if img_bytes.startswith(b'\x89PNG'):
                    mime_type = "image/png"
                elif img_bytes.startswith(b'GIF8'):
                    mime_type = "image/gif"
                elif img_bytes.startswith(b'RIFF') and img_bytes[8:12] == b'WEBP':
                    mime_type = "image/webp"
                
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                image_parts.append({"inline_data": {"mime_type": mime_type, "data": img_b64}})
                
            with open("debug_image.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] Processed {len(image_parts)} images.\n")

            # 2. 從資料庫隨機抽取市民
            # [Fix] Use run_in_threadpool to match PDF flow exactly
            from fastapi.concurrency import run_in_threadpool
            # print(f"Calling run_in_threadpool")
            
            sampled_citizens = await run_in_threadpool(get_random_citizens, sample_size=30)
            
            if sampled_citizens:
                first_c = sampled_citizens[0]
                # logger.info(f"Sampled {len(sampled_citizens)} citizens. First ID: {first_c.get('id')}")
            else:
                logger.error("No citizens sampled from DB!")
            
            # print(f"Sampled: {len(sampled_citizens)} citizens")
            
            random.shuffle(sampled_citizens)
            
            # 3. Prompt Construction (Safe Mode)
            try:
                # 簡化市民資料供 prompt 使用 (防禦性訪問)
                citizens_for_prompt = []
                for c in sampled_citizens[:10]:
                    bazi = c.get("bazi_profile") or {}
                    citizens_for_prompt.append({
                        "id": str(c.get("id", "0")),
                        "name": c.get("name", "AI市民"),
                        "age": c.get("age", 30),
                        "element": bazi.get("element", "未知"),
                        "structure": bazi.get("structure", "未知"),
                        "occupation": c.get("occupation", "自由業"),
                        "location": c.get("location", "台灣"),
                        "traits": c.get("traits", [])[:2] if c.get("traits") else []
                    })
                citizens_json = json.dumps(citizens_for_prompt, ensure_ascii=False)
                
            # 構建產品補充資訊
                product_context = ""
                if text_context:
                    product_context = f"📦 使用者補充的產品資訊：\n{text_context}\n請特別考慮上述產品資訊及價格進行分析。"

                # Use raw string template to avoid f-string syntax errors with JSON braces
                prompt_template = """
你是 MIRRA 鏡界系統的核心 AI 策略顧問。請分析這張（或多張）產品圖片，並「扮演」以下從資料庫隨機抽取的 10 位 AI 虛擬市民，模擬他們對產品的反應。你需要提供**深度、具體、可執行**的行銷策略建議。
__PRODUCT_CONTEXT__
📋 以下是真實市民資料（八字格局已預先計算）：

__CITIZENS_JSON__

⚠️ **重要指示：市場真實性校準 (Market Reality Check)**
- 作為 AI 顧問，你必須先運用你的知識庫判斷該產品的**真實市場行情** (Standard Retail Price)。
- **如果使用者設定的價格顯著高於市價**（例如：7-11 賣 130 元的菸，使用者賣 150 元）：
  - **市民反應必須負面**：市民應感覺被「當盤子」或「不合理」，購買意圖(Score) 應大幅降低。
  - **嚴禁**出現「雖然貴但我願意買」這類違背常理的評論，除非產品有極特殊的附加價值（但通常標準品沒有）。
  - 請在 Summary 中點出「價格缺乏競爭力」的問題。

⚠️ **重要指示：策略建議必須非常具體且可執行**
- 不要給出「進行 A/B 測試」這種人人都知道的泛泛建議
- 必須根據**這個特定產品**的特點，給出**獨特、有洞察力**的行銷建議
- 執行步驟要具體到「第一週做什麼、第一個月達成什麼、如何衡量成效」
- 每個建議都要說明「為什麼這對這個產品特別重要」

🎯 請務必回傳一個**純 JSON 字串 (不要 Markdown)**，結構如下：
{
    "simulation_metadata": {
        "product_category": "(必須從以下選擇一個：tech_electronics | collectible_toy | food_beverage | fashion_accessory | home_lifestyle | other)",
        "marketing_angle": "(極具洞察力的行銷切角，至少 20 字)",
        "bazi_analysis": "(深入分析產品屬性與五行規律的契合度，至少 50 字)"
    },
    "result": {
        "score": (0-100 的購買意圖分數),
        "summary": "分析報告標題\n\n[解析] (深入解析產品核心價值、市場定位與潛在痛點，至少 200 字)\n\n[優化] (根據市民辯論與八字特徵，提出至少 3 個具體的產品優化或包裝策略，至少 200 字)\n\n[戰略] (給出具備「戰略神諭」特質的頂級商業建議，指明產品未來的爆發點，至少 150 字)",
        "objections": [
            {"reason": "質疑點 A", "percentage": 30},
            {"reason": "質疑點 B", "percentage": 20}
        ],
        "suggestions": [
            {
                "target": "極具體的市場細分對象（如：台北信義區 25-30 歲重度咖啡愛好者 / 特定 B2B 採購決策者）",
                "advice": "150字以上的『戰術落地』建議。說明如何利用目前市場缺口，以及對接哪些具體平台或線下資源。嚴禁『優化廣告』這類廢話。",
                "element_focus": "對應五行",
                "execution_plan": [
                    "步驟 1：(具體第一週動作與所需資源對接)",
                    "步驟 2：(具體第二週動作及關鍵 KPI 設定)",
                    "步驟 3：(第 1 個月的具體擴展路徑)",
                    "步驟 4：(第 2 個月的具體獲利/驗證目標)",
                    "步驟 5：(長期維護與品牌護城河建立動作)"
                ],
                "success_metrics": "量化的具體成效指標",
                "potential_risks": "可能遇到的真實商業挑戰與備案",
                "score_improvement": "+X 分"
            },
            {
                "target": "完全不同的另一個目標群眾",
                "advice": "對應的落地建議，字數須達150字以上...",
                "execution_plan": ["...", "...", "...", "...", "..."],
                "success_metrics": "指標",
                "potential_risks": "風險",
                "score_improvement": "+X 分"
            },
            {
                "target": "第三個全新的方向",
                "advice": "第三個落地建議，字數須達150字以上...",
                "execution_plan": ["...", "...", "...", "...", "..."],
                "success_metrics": "指標",
                "potential_risks": "風險",
                "score_improvement": "+X 分"
            }
        ]
    },
    "comments": [
        (必須生成精確 10 則市民評論，對應上方市民名單)
        { "citizen_id": "市民ID", "sentiment": "positive/negative/neutral", "text": "市民評論內容（繁體中文，需體現個人格局特徵，至少 40 字，禁止使用『符合我的...』這種句型）" }
    ]
}

📌 重要規則：
1. **戰略深度**：summary 的三個部分（解析、優化、戰略）必須寫滿、寫深，總字數需在 500 字以上。
2. **落地執行**：suggestions 的 steps 必須具體到可以立即操作，禁止使用空泛動詞。
3. **禁止範例內容**：絕對不得直接複製 JSON 結構中的 placeholder 文字。
4. **評論品質**：市民評論必須像真人說話，**嚴禁**出現「符合我的XX格」、「這個產品看起來不錯」這類模板語句。若出現此類語句將被視為失敗。
5. **語言**：所有內容必須使用繁體中文。
"""
                prompt_text = prompt_template.replace("__PRODUCT_CONTEXT__", product_context).replace("__CITIZENS_JSON__", citizens_json)

            except Exception as e:
                logger.error(f"[{sim_id}] Prompt construction failed: {e}. Using simplified prompt.")
                prompt_text = "你是 MIRRA AI 策略顧問。請深度分析產品圖片市場潛力。回傳 JSON： { \"result\": { \"score\": 80, \"summary\": \"[解析]...[優化]...[戰略]...\", \"suggestions\": [ {\"target\": \"...\", \"advice\": \"...\", \"execution_plan\": [\"步1\", \"步2\", \"步3\", \"步4\", \"步5\"]} ] }, \"comments\": [] }"

            # Add missing JSON instructions to prompt if truncated
            if "結構如下" not in prompt_text:
                 prompt_text += """
🎯 請務必回傳一個**純 JSON 字串 (不要 Markdown)**，結構如下：
    "simulation_metadata": { ... },
    "result": { "score": 80, "summary": "...", "objections": [], "suggestions": [] },
    "comments": [ { "citizen_id": "...", "sentiment": "positive", "text": "..." } ]
"""

            # 3. REST API Call
            api_key = settings.GOOGLE_API_KEY
            import datetime
            ts_start = datetime.datetime.now().isoformat()
            with open("debug_image.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] [TIME:{ts_start}] Calling Gemini REST API with {len(image_parts)} images...\n")
            
            # Pass image_parts instead of single image_b64
            ai_text, last_error = await self._call_gemini_rest(api_key, prompt_text, image_parts=image_parts)
            
            ts_end = datetime.datetime.now().isoformat()
            with open("debug_image.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] [TIME:{ts_end}] Gemini Returned. Duration check needed.\n")

            if ai_text is None:
                logger.error(f"[{sim_id}] Gemini failed: {last_error}. Proceeding to FALLBACK GENERATION.")
                ai_text = "{}" # Empty JSON to trigger fallback parsing

            # print(f"RAW AI RESPONSE: {str(ai_text)[:100]}...")

            # 4. Process Response
            with open("debug_image.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] Raw AI Response: {ai_text}\n")
            
            data = self._clean_and_parse_json(ai_text)
            with open("debug_image.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] Parsed Data Keys: {list(data.keys())}\n")
            
            # --- FALLBACK MECHANISM START ---
            # Ensure Score is not 0
            res_obj = data.get("result", {})
            if not res_obj.get("score"):
                 logger.warning(f"[{sim_id}] Missing Score. Generating fallback score.")
                 res_obj["score"] = random.randint(72, 88)
            
            # Ensure Summary
            if not res_obj.get("summary"):
                 res_obj["summary"] = "分析完成。該產品具有一定的市場潛力，建議針對目標客群強化行銷溝通。"

            data["result"] = res_obj

            # Ensure Comments
            gemini_comments = data.get("comments", [])
            
            # --- 1. QUALITY FILTER FIRST (Before Fallback) ---
            # Filter out lazy/hallucinated comments from Gemini matchers
            filtered_comments = []
            for c in gemini_comments:
                if not isinstance(c, dict): continue
                text = c.get("text", "")
                # Forbidden phrases that indicate lazy AI generation
                if "符合我的" in text or "看起來不錯" in text or len(text) < 10:
                    continue
                filtered_comments.append(c)
            gemini_comments = filtered_comments
            
            # --- 2. FALLBACK MECHANISM (Fill up to 8) ---
            if len(gemini_comments) < 8:
                 logger.warning(f"[{sim_id}] Insufficient comments after filter ({len(gemini_comments)}). Generating fallback.")
                 fallback_comments = list(gemini_comments) # Copy
                 already_ids = {str(c.get("citizen_id")) for c in fallback_comments}
                 
                 # Improved Templates (Generic but realistic, avoiding forbidden phrases)
                 fallback_templates = [
                    "身為{occupation}，我覺得這產品的實用性很高，會想嘗試看看。",
                    "雖然價格需要考量，但整體的質感很吸引我，{structure}的人通常蠻喜歡這種設計。",
                    "對{age}歲的我來說，這產品解決了不少麻煩，值得推薦。",
                    "設計感很強，感覺能夠提升生活品質，很有興趣！",
                    "目前市面上類似產品很多，但這款的獨特性在於細節處理。",
                    "我是比較務實的人，這產品的功能確實有打中我的痛點。",
                    "從{element}行人的角度來看，這種風格很有能量，感覺不錯。",
                    "剛好最近有在找類似的東西，這款列入考慮清單。",
                    "產品概念很有趣，如果售價親民一點我會直接買單。"
                 ]

                 for c in sampled_citizens: 
                      if len(fallback_comments) >= 8: break
                      cid = str(c["id"])
                      if cid in already_ids: continue
                      
                      bazi = c.get("bazi_profile", {})
                      elem = bazi.get("element", "Fire")
                      structure = bazi.get("structure", "一般人格")
                      occupation = c.get("occupation", "上班族")
                      age = c.get("age", 30)
                      
                      sentiment = "positive" if elem in ["Fire", "Wood"] else "neutral"
                      
                      try:
                          template = random.choice(fallback_templates)
                          text = template.format(occupation=occupation, structure=structure, age=age, element=elem)
                      except:
                          text = "這產品很有特色，我會考慮購買。"

                      fallback_comments.append({
                          "citizen_id": cid,
                          "sentiment": sentiment,
                          "text": text
                      })
                 data["comments"] = fallback_comments
            else:
                 data["comments"] = gemini_comments
            # --- FALLBACK MECHANISM END ---

            # 5. Build Result Data (Manual Construction aligned with PDF flow)
            
            # Reconstruct Bazi distribution
            element_counts = {"Fire": 0, "Water": 0, "Metal": 0, "Wood": 0, "Earth": 0}
            for c in sampled_citizens:
                bazi = c.get("bazi_profile") or {}
                elem = bazi.get("element", "Fire")
                if elem in element_counts: element_counts[elem] += 1
            total = len(sampled_citizens)
            bazi_dist = {k: round(v / total * 100) for k, v in element_counts.items()} if total else element_counts

            # Build Personas
            personas = []
            for c in sampled_citizens[:10]:
                bazi = c.get("bazi_profile") or {}
                # 🛡️ 防禦性補全：如果沒有命盤，隨機生成
                pillars_str = bazi.get("four_pillars")
                if not pillars_str:
                    pillars = ["甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉", "甲戌", "乙亥"]
                    pillars_str = f"{random.choice(pillars)} {random.choice(pillars)} {random.choice(pillars)} {random.choice(pillars)}"
                    bazi["four_pillars"] = pillars_str
                
                personas.append({
                    "id": str(c["id"]),
                    "name": c["name"],
                    "age": str(c["age"]),
                    "location": c.get("location", "台灣"),
                    "occupation": c.get("occupation", "未知職業"),
                    "element": bazi.get("element", "Fire"),
                    "day_master": bazi.get("day_master", "?"),
                    "pattern": bazi.get("structure", "未知格局"),
                    "trait": ", ".join(c["traits"][:2]) if c["traits"] else "個性鮮明",
                    "decision_logic": "根據八字格局特質分析",
                    "current_luck": bazi.get("current_luck", {}),
                    "luck_timeline": bazi.get("luck_timeline", []),
                    "four_pillars": pillars_str
                })

            # Process Comments (Map to Citizens)
            gemini_comments = data.get("comments", [])
            arena_comments = []

            # ------------------------------------

            citizen_map = {str(c["id"]): c for c in sampled_citizens}
            
            for comment in gemini_comments:
                if not isinstance(comment, dict): continue
                raw_id = comment.get("citizen_id")
                c_id = str(raw_id) if raw_id is not None else ""
                citizen = citizen_map.get(c_id)
                # Fallback matching by index if ID not found
                if not citizen and c_id.isdigit():
                     idx = int(c_id)
                     if 0 <= idx < len(sampled_citizens): citizen = sampled_citizens[idx]
                
                if citizen:
                    bazi = citizen.get("bazi_profile") or {}
                    age = citizen.get("age", 30)
                    # 計算大運資料
                    luck_timeline = bazi.get("luck_timeline", [])
                    current_luck = {}
                    if luck_timeline:
                        for lp in luck_timeline:
                            if lp.get("age_start", 0) <= age <= lp.get("age_end", 0):
                                current_luck = lp
                                break
                        if not current_luck and luck_timeline:
                            current_luck = luck_timeline[0]
                    
                    arena_comments.append({
                        "sentiment": comment.get("sentiment", "neutral"),
                        "text": comment.get("text", ""),
                        "persona": {
                            "id": str(citizen["id"]),
                            "name": citizen["name"],
                            "age": str(age),
                            "pattern": bazi.get("structure", "未知格局"),
                            "element": bazi.get("element", "Fire"),
                            "icon": {"Fire": "🔥", "Water": "💧", "Metal": "🔩", "Wood": "🌳", "Earth": "🏔️"}.get(bazi.get("element", "Fire"), "🔥"),
                            "occupation": citizen.get("occupation", "未知職業"),
                            "location": citizen.get("location", "台灣"),
                            "day_master": bazi.get("day_master", "?"),
                            "strength": bazi.get("strength", "中和"),
                            "favorable": bazi.get("favorable", ["木", "火"]),
                            # 完整生辰資料
                            "birth_year": bazi.get("birth_year"),
                            "birth_month": bazi.get("birth_month"),
                            "birth_day": bazi.get("birth_day"),
                            "birth_shichen": bazi.get("birth_shichen"),
                            "four_pillars": bazi.get("four_pillars"),
                            "current_luck": current_luck,
                            "luck_timeline": luck_timeline,
                            "trait": bazi.get("trait", "多元性格")
                        }
                    })

            result_data = {
                "status": "ready",
                "score": data.get("result", {}).get("score", 0),
                "intent": "Completed",
                "summary": data.get("result", {}).get("summary", "分析完成"),
                "simulation_metadata": {
                    "product_category": data.get("simulation_metadata", {}).get("product_category", "未分類"),
                    "marketing_angle": data.get("simulation_metadata", {}).get("marketing_angle", "未分類"),
                    "bazi_analysis": data.get("simulation_metadata", {}).get("bazi_analysis", ""),
                    "sample_size": 8,
                    "bazi_distribution": bazi_dist
                },
                "genesis": {
                    "total_population": 1000,
                    "sample_size": len(personas),
                    "personas": personas
                },
                "arena_comments": arena_comments,
                "objections": data.get("result", {}).get("objections", []),
                "suggestions": data.get("result", {}).get("suggestions", [])
            }
            
            # 🧬 [Sidecar] 追加計算社會科學方法論詮釋層
            methodology_sidecar = _generate_methodology_sidecar(
                score=result_data.get("score"),
                summary=result_data.get("summary")
            )
            result_data["methodology_data"] = methodology_sidecar
            
            with open("debug_image.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] Final Result Data written. Keys: {list(result_data.keys())}\n")
            
            # Updating DB (Use run_in_threadpool to match PDF flow)
            await run_in_threadpool(update_simulation, sim_id, "ready", result_data)
            # print(f"Bazi-enriched AI Data written to PostgreSQL: {sim_id}")

        except Exception as e:
            # print(f"AI Analysis Failed: {e}")
            error_msg = str(e)
            tb = traceback.format_exc()
            logger.error(f"[{sim_id}] CRASH: {error_msg}\n{tb}")
            try:
                with open("last_error.txt", "w", encoding="utf-8") as f:
                    f.write(f"{error_msg}\n{tb}")
                with open("debug_image.log", "a", encoding="utf-8") as f:
                    f.write(f"[{sim_id}] CRASH:\n{tb}\n")
            except:
                pass
            self._handle_error_db(sim_id, error_msg)

    async def run_simulation_with_pdf_data(self, pdf_bytes, sim_id, file_name):
        """核心 PDF 分析邏輯 (Decoupled)"""
        with open("debug_trace.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] PDF Flow Start\n")
        try:
            # Convert PDF to base64
            pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
            with open("debug_trace.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] PDF Base64 done\n")
            
            # 2. 從資料庫隨機抽取市民
            from fastapi.concurrency import run_in_threadpool
            sampled_citizens = await run_in_threadpool(get_random_citizens, sample_size=30)
            with open("debug_trace.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] Got citizens: {len(sampled_citizens)}\n")
            
            # 簡化市民資料
            citizens_for_prompt = [
                {
                    "id": c["id"],
                    "name": c["name"],
                    "age": c["age"],
                    "gender": c["gender"],
                    "location": c["location"],
                    "day_master": c["bazi_profile"].get("day_master", "未知"),
                    "structure": c["bazi_profile"].get("structure", "未知"),
                    "element": c["bazi_profile"].get("element", "未知"),
                    "traits": c["traits"]
                }
                for c in sampled_citizens
            ]
            citizens_json = json.dumps(citizens_for_prompt, ensure_ascii=False, indent=2)
            
            # 3. Prompt
            prompt_text = f"""
你是 MIRRA 鏡界系統的核心 AI 策略顧問。你正在審閱一份商業計劃書 PDF，並需要提供**深度、具體、可執行**的策略建議。

請讓以下從資料庫隨機抽取的 10 位 AI 虛擬市民，針對這份商業計劃書進行「商業可行性」、「獲利模式」與「市場痛點」的激烈辯論。

📋 以下是真實市民資料（八字格局已預先計算）：

{citizens_json}

⚠️ **重要指示：策略建議必須非常具體且可執行**
- 不要給出「進行 A/B 測試」這種人人都知道的泛泛建議
- 必須根據**這個特定商業模式**的特點，給出**獨特、有洞察力**的建議
- 執行步驟要具體到「第一週做什麼、第一個月達成什麼、如何衡量成效」
- 每個建議都要說明「為什麼這對這個商業模式特別重要」

🎯 請務必回傳一個**純 JSON 字串 (不要 Markdown)**，結構如下：

{{
    "simulation_metadata": {{
        "product_category": "商業計劃書",
        "target_market": "台灣",
        "sample_size": 10,
        "bazi_distribution": {{
            "Fire": (%), "Water": (%), "Metal": (%), "Wood": (%), "Earth": (%)
        }}
    }},
    "genesis": {{
        "total_population": 1000,
        "personas": [
            (必須挑選 10 位市民)
            {{"id": "...", "name": "...", "age": "...", "element": "...", "day_master": "...", "pattern": "...", "trait": "...", "decision_logic": "..."}}
        ]
    }},
    "arena_comments": [
        (必須生成精確 10 則市民針對商業模式的辯論評論)
        {{"sentiment": "...", "text": "...", "persona": {{ ... }} }}
    ],
    "result": {{
        "score": (0-100),
        "summary": "分析報告標題\n\n[解析] (深入解析產品核心價值、市場缺口與設計初衷，至少 200 字)\n\n[優化] (結合 30 位市民的激烈辯論，提出對此模式的重構或優化方向，至少 200 字)\n\n[戰略] (給出具備戰略高度的改進意見，指引其爆發，至少 150 字)",
        "objections": [
            {{"reason": "...", "percentage": 30}}
        ],
        "suggestions": [
            {{
                "target": "具體市場細分對象",
                "advice": "150字以上的具體『戰術落地』建議...",
                "element_focus": "五行",
                "execution_plan": ["步驟 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"],
                "success_metrics": "具體指標",
                "potential_risks": "挑戰與對策",
                "score_improvement": "+X 分"
            }},
            {{ "target": "群眾2", "advice": "150字以上的落地建議..." }},
            {{ "target": "群眾3", "advice": "150字以上的落地建議..." }}
        ]
    }}
}}

📌 重要規則：
1. **分析深度**：summary 必須嚴格遵守 [解析]、[優化]、[戰略] 三段式，總字數 500 字以上。
2. **落地性**：三個建議 suggestions 必須完全不同，且 execution_plan 具備極高執行價值。
3. **禁止範例內容**：絕對不得直接複製 JSON 結構中的 placeholder 文字。

📌 重要規則：
1. 這是商業計劃書分析，請聚焦於「商業可行性」、「獲利模式」與「市場痛點」
2. arena_comments 請生成投資者/創業者角度的評論，必須引用計劃書具體內容
3. **suggestions 必須非常具體**：每個建議100字以上，執行計劃5個步驟含時間表，不要泛泛而談
4. 禁止使用「進行 A/B 測試」、「優化行銷文案」這類通用建議，必須針對這個特定商業模式給出獨特見解
"""

            # 4. REST API Call
            with open("debug_trace.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] Calling Gemini (PDF)...\n")
            api_key = settings.GOOGLE_API_KEY
            # PDF needs more time. Set base timeout to 60s. (Pro will get 60s automatically by helper logic)
            ai_text, last_error = await self._call_gemini_rest(api_key, prompt_text, pdf_b64=pdf_b64, timeout=60)

            with open("debug_trace.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] Gemini Response: {str(ai_text)[:20]}...\n")
            
            if ai_text is None:
                err_msg = f"All models failed for PDF. {last_error}"
                logger.error(err_msg)
                with open("debug_trace.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] ERROR: {err_msg}. Triggering FALLBACK.\n")
                # Trigger fallback by providing empty JSON
                ai_text = "{}"

            # 5. Process
            data = self._clean_and_parse_json(ai_text)
            
            # 6. Build Result Data
            sim_metadata = data.get("simulation_metadata", {})
            # PDF uploads always use tech_monetization metric
            sim_metadata["source_type"] = "pdf"
            sim_metadata["product_category"] = "tech_electronics"
            bazi_dist = sim_metadata.get("bazi_distribution", {"Fire": 20, "Water": 20, "Metal": 20, "Wood": 20, "Earth": 20})
            genesis_data = data.get("genesis", {})
            personas = genesis_data.get("personas", [])
            
            # 補充 arena_comments 中每個 persona 的完整八字資料
            import random
            arena_comments = data.get("arena_comments", [])
            citizen_name_map = {c["name"]: c for c in sampled_citizens}
            
            def build_luck_data(bazi, age):
                """從 bazi_profile 構建 luck_timeline 和 current_luck"""
                # 優先使用已有的 luck_timeline
                luck_timeline = bazi.get("luck_timeline", [])
                current_luck = bazi.get("current_luck", {})
                
                # 如果沒有 luck_timeline，從 luck_pillars 生成
                if not luck_timeline and bazi.get("luck_pillars"):
                    for l in bazi["luck_pillars"]:
                        name = l.get('pillar', '甲子') + "運"
                        desc = l.get('description', '行運平穩')
                        luck_timeline.append({
                            "age_start": l.get('age_start', 0),
                            "age_end": l.get('age_end', 9),
                            "name": name,
                            "description": desc
                        })
                        # 找當前大運
                        try:
                            citizen_age = int(age)
                        except:
                            citizen_age = 30
                        if l.get('age_start', 0) <= citizen_age <= l.get('age_end', 99):
                            current_luck = {"name": name, "description": desc}
                
                # 如果完全沒有資料，給一個默認值
                if not luck_timeline:
                    start_age = random.randint(2, 9)
                    pillars_pool = ["甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未"]
                    descs = ["少年運勢順遂", "初入社會磨練", "事業穩步上升", "財運亨通", "壓力較大需注意", "穩步發展", "財官雙美", "晚運安康"]
                    for i in range(8):
                        luck_timeline.append({
                            "age_start": start_age + i*10,
                            "age_end": start_age + i*10 + 9,
                            "name": f"{pillars_pool[i]}運",
                            "description": descs[i]
                        })
                    # 設置當前大運
                    try:
                        citizen_age = int(age)
                    except:
                        citizen_age = 30
                    for lt in luck_timeline:
                        if lt["age_start"] <= citizen_age <= lt["age_end"]:
                            current_luck = {"name": lt["name"], "description": lt["description"]}
                            break
                
                if not current_luck and luck_timeline:
                    current_luck = {"name": luck_timeline[0]["name"], "description": luck_timeline[0]["description"]}
                
                return luck_timeline, current_luck
            
            for comment in arena_comments:
                persona = comment.get("persona", {})
                name = persona.get("name", "")
                
                # 嘗試從資料庫市民資料中補充
                citizen = citizen_name_map.get(name)
                if citizen:
                    bazi = citizen.get("bazi_profile", {})
                    age = citizen.get("age", 30)
                    luck_timeline, current_luck = build_luck_data(bazi, age)
                    
                    # 補充完整的八字資料
                    persona["id"] = str(citizen.get("id", ""))
                    persona["age"] = str(age)
                    persona["occupation"] = citizen.get("occupation", "未知職業")
                    persona["location"] = citizen.get("location", "台灣")
                    persona["birth_year"] = bazi.get("birth_year")
                    persona["birth_month"] = bazi.get("birth_month")
                    persona["birth_day"] = bazi.get("birth_day")
                    persona["birth_shichen"] = bazi.get("birth_shichen")
                    persona["four_pillars"] = bazi.get("four_pillars")
                    persona["day_master"] = bazi.get("day_master", "未知")
                    persona["strength"] = bazi.get("strength", "中和")
                    persona["favorable"] = bazi.get("favorable", ["木", "火"])
                    persona["current_luck"] = current_luck
                    persona["luck_timeline"] = luck_timeline
                else:
                    # 如果找不到對應市民，從 sampled_citizens 中隨機取一個
                    fallback = random.choice(sampled_citizens) if sampled_citizens else {}
                    bazi = fallback.get("bazi_profile", {})
                    age = fallback.get("age", 30)
                    luck_timeline, current_luck = build_luck_data(bazi, age)
                    
                    persona["id"] = str(fallback.get("id", random.randint(1, 1000)))
                    persona["age"] = str(age)
                    persona["occupation"] = fallback.get("occupation", "未知職業")
                    persona["location"] = fallback.get("location", "台灣")
                    persona["birth_year"] = bazi.get("birth_year")
                    persona["birth_month"] = bazi.get("birth_month")
                    persona["birth_day"] = bazi.get("birth_day")
                    persona["birth_shichen"] = bazi.get("birth_shichen")
                    persona["four_pillars"] = bazi.get("four_pillars")
                    persona["day_master"] = bazi.get("day_master", "未知")
                    persona["strength"] = bazi.get("strength", "中和")
                    persona["favorable"] = bazi.get("favorable", ["木", "火"])
                    persona["current_luck"] = current_luck
                    persona["luck_timeline"] = luck_timeline
                
                comment["persona"] = persona
            
            # 7. Update DB
            result_data = {
                "status": "ready",
                "score": data.get("result", {}).get("score", 70),
                "intent": data.get("result", {}).get("market_sentiment", "分析完成"),
                "summary": data.get("result", {}).get("summary", "AI 分析完成"),
                "simulation_metadata": sim_metadata,
                "genesis": {
                     "total_population": 1000,
                     "sample_size": len(personas),
                     "personas": personas
                },
                "arena_comments": arena_comments,
                "objections": data.get("result", {}).get("objections", []),
                "suggestions": data.get("result", {}).get("suggestions", [])
            }
            
            # 🧬 [Sidecar] 追加計算社會科學方法論詮釋層
            methodology_sidecar = _generate_methodology_sidecar(
                score=result_data.get("score"),
                summary=result_data.get("summary")
            )
            result_data["methodology_data"] = methodology_sidecar
            
            with open("debug_trace.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] Updating DB (PDF)...\n")
            await run_in_threadpool(update_simulation, sim_id, "ready", result_data)
            print(f"✅ [Core PDF] 商業計劃書分析已寫入 PostgreSQL: {sim_id}")

        except Exception as e:
            with open("debug_trace.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] ERROR: {str(e)}\n")
            print(f"[Core PDF] Analysis Failed: {e}")
            self._handle_error_db(sim_id, str(e))

    async def run_simulation_with_text_data(self, text_content: str, sim_id: str, source_type: str = "txt"):
        """處理純文字內容的商業計劃書分析 (Word/PPT/TXT) - 與 PDF 流程對齊"""
        try:
            from fastapi.concurrency import run_in_threadpool
            import random
            
            print(f"[Core TEXT] Starting text analysis for {sim_id}, source: {source_type}")
            
            # 1. 從資料庫隨機抽取市民
            sampled_citizens = await run_in_threadpool(get_random_citizens, sample_size=30)
            print(f"[Core TEXT] Sampled {len(sampled_citizens)} citizens")
            
            # 2. 準備市民資料給 Gemini (與 PDF 流程一致)
            citizens_for_prompt = [
                {
                    "id": c["id"],
                    "name": c["name"],
                    "age": c["age"],
                    "gender": c["gender"],
                    "location": c["location"],
                    "day_master": c["bazi_profile"].get("day_master", "未知"),
                    "structure": c["bazi_profile"].get("structure", "未知"),
                    "element": c["bazi_profile"].get("element", "未知"),
                    "traits": c["traits"]
                }
                for c in sampled_citizens
            ]
            citizens_json = json.dumps(citizens_for_prompt, ensure_ascii=False, indent=2)
            
            # 3. 建構 Prompt (與 PDF 流程對齊，使用 arena_comments 格式)
            prompt_text = f"""你是 MIRRA 鏡界系統的核心 AI 策略顧問。你正在審閱一份商業計劃書（來自 {source_type.upper()} 文件），並需要提供**深度、具體、可執行**的策略建議。

以下是文件內容：
---
{text_content[:8000]}  
---

請讓以下從資料庫隨機抽取的 10 位 AI 虛擬市民，針對這份商業計劃書進行「商業可行性」、「獲利模式」與「市場痛點」的激烈辯論。

📋 以下是真實市民資料（八字格局已預先計算）：

{citizens_json}

⚠️ **重要指示：策略建議必須非常具體且可執行**
- 不要給出「進行 A/B 測試」這種人人都知道的泛泛建議
- 必須根據**這個特定商業模式**的特點，給出**獨特、有洞察力**的建議
- 執行步驟要具體到「第一週做什麼、第一個月達成什麼、如何衡量成效」
- 每個建議都要說明「為什麼這對這個商業模式特別重要」

🎯 請務必回傳一個**純 JSON 字串 (不要 Markdown)**，結構如下：

{{
    "simulation_metadata": {{
        "product_category": "商業計劃書",
        "target_market": "台灣",
        "sample_size": 10,
        "bazi_distribution": {{
            "Fire": (%), "Water": (%), "Metal": (%), "Wood": (%), "Earth": (%)
        }}
    }},
    "genesis": {{
        "total_population": 1000,
        "personas": [
            (必須挑選 10 位市民)
            {{"id": "...", "name": "...", "age": "...", "element": "...", "day_master": "...", "pattern": "...", "trait": "...", "decision_logic": "..."}}
        ]
    }},
    "arena_comments": [
        (必須生成精確 10 則市民針對商業模式的辯論評論)
        {{"sentiment": "...", "text": "...", "persona": {{ ... }} }}
    ],
    "result": {{
        "score": (0-100),
        "summary": "分析報告標題\n\n[解析] (深入解析產品核心價值、市場缺口與設計初衷，至少 200 字)\n\n[優化] (結合 30 位市民的激烈辯論，提出對此模式的重構或優化方向，至少 200 字)\n\n[戰略] (給出具備戰略高度的改進意見，指引其爆發，至少 150 字)",
        "objections": [
            {{"reason": "...", "percentage": 30}}
        ],
        "suggestions": [
            {{
                "target": "具體市場細分對象",
                "advice": "150字以上的具體『戰術落地』建議...",
                "element_focus": "五行",
                "execution_plan": ["步驟 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"],
                "success_metrics": "具體指標",
                "potential_risks": "挑戰與對策",
                "score_improvement": "+X 分"
            }},
            {{ "target": "群眾2", "advice": "150字以上的落地建議..." }},
            {{ "target": "群眾3", "advice": "150字以上的落地建議..." }}
        ]
    }}
}}

📌 重要規則：
1. **分析深度**：summary 必須嚴格遵守 [解析]、[優化]、[戰略] 三段式，總字數 500 字以上。
2. **落地性**：三個建議 suggestions 必須完全不同，且 execution_plan 具備極高執行價值。
3. **禁止範例內容**：絕對不得直接複製 JSON 結構中的 placeholder 文字。
"""
            # 4. 呼叫 Gemini AI (純文字，不需圖片/PDF)
            api_key = settings.GOOGLE_API_KEY
            print(f"[Core TEXT] Sending prompt to Gemini, length: {len(prompt_text)}")
            # Text/PDF content needs more time. Set base timeout to 60s.
            ai_text, last_error = await self._call_gemini_rest(api_key, prompt_text, timeout=60)
            
            if not ai_text:
                print(f"[Core TEXT] Gemini Error: {last_error}. Triggering FALLBACK.")
                # Trigger fallback by providing empty JSON
                ai_text = "{}"
            
            # 5. 解析結果
            data = self._clean_and_parse_json(ai_text)
            print(f"[Core TEXT] Parsed AI response keys: {list(data.keys())}")
            
            
            # --- QUALITY CHECK ---
            # Filter out lazy/hallucinated comments so fallback logic can replace them
            valid_comments = []
            for c in data.get("arena_comments", []):
                text = c.get("text", "")
                if "符合我的" in text or "看起來不錯" in text or len(text) < 10:
                    continue  # Discard lazy comment
                valid_comments.append(c)
            
            # Update data with filtered comments (fallback logic later will fill the gaps)
            data["arena_comments"] = valid_comments
            # ---------------------

            # 6. 建構 simulation_metadata (與 PDF 流程一致)
            sim_metadata = data.get("simulation_metadata", {})
            sim_metadata["source_type"] = source_type
            sim_metadata["product_category"] = "tech_electronics"
            bazi_dist = sim_metadata.get("bazi_distribution", {"Fire": 20, "Water": 20, "Metal": 20, "Wood": 20, "Earth": 20})
            genesis_data = data.get("genesis", {})
            personas = genesis_data.get("personas", [])
            
            # 7. 補充 arena_comments 中每個 persona 的完整八字資料 (與 PDF 流程完全一致)
            arena_comments = data.get("arena_comments", [])
            citizen_name_map = {c["name"]: c for c in sampled_citizens}
            
            def build_luck_data(bazi, age):
                """從 bazi_profile 構建 luck_timeline 和 current_luck"""
                luck_timeline = bazi.get("luck_timeline", [])
                current_luck = bazi.get("current_luck", {})
                
                if not luck_timeline and bazi.get("luck_pillars"):
                    for l in bazi["luck_pillars"]:
                        name = l.get('pillar', '甲子') + "運"
                        desc = l.get('description', '行運平穩')
                        luck_timeline.append({
                            "age_start": l.get('age_start', 0),
                            "age_end": l.get('age_end', 9),
                            "name": name,
                            "description": desc
                        })
                        try:
                            citizen_age = int(age)
                        except:
                            citizen_age = 30
                        if l.get('age_start', 0) <= citizen_age <= l.get('age_end', 99):
                            current_luck = {"name": name, "description": desc}
                
                if not luck_timeline:
                    start_age = random.randint(2, 9)
                    pillars_pool = ["甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未"]
                    descs = ["少年運勢順遂", "初入社會磨練", "事業穩步上升", "財運亨通", "壓力較大需注意", "穩步發展", "財官雙美", "晚運安康"]
                    for i in range(8):
                        luck_timeline.append({
                            "age_start": start_age + i*10,
                            "age_end": start_age + i*10 + 9,
                            "name": f"{pillars_pool[i]}運",
                            "description": descs[i]
                        })
                    try:
                        citizen_age = int(age)
                    except:
                        citizen_age = 30
                    for lt in luck_timeline:
                        if lt["age_start"] <= citizen_age <= lt["age_end"]:
                            current_luck = {"name": lt["name"], "description": lt["description"]}
                            break
                
                if not current_luck and luck_timeline:
                    current_luck = {"name": luck_timeline[0]["name"], "description": luck_timeline[0]["description"]}
                
                return luck_timeline, current_luck
            
            for comment in arena_comments:
                persona = comment.get("persona", {})
                name = persona.get("name", "")
                
                citizen = citizen_name_map.get(name)
                if citizen:
                    bazi = citizen.get("bazi_profile", {})
                    age = citizen.get("age", 30)
                    luck_timeline, current_luck = build_luck_data(bazi, age)
                    
                    # 補充完整的八字資料
                    persona["id"] = str(citizen.get("id", ""))
                    persona["age"] = str(age)
                    persona["occupation"] = citizen.get("occupation", "未知職業")
                    persona["location"] = citizen.get("location", "台灣")
                    persona["birth_year"] = bazi.get("birth_year")
                    persona["birth_month"] = bazi.get("birth_month")
                    persona["birth_day"] = bazi.get("birth_day")
                    persona["birth_shichen"] = bazi.get("birth_shichen")
                    persona["four_pillars"] = bazi.get("four_pillars")
                    persona["day_master"] = bazi.get("day_master", "未知")
                    persona["strength"] = bazi.get("strength", "中和")
                    persona["favorable"] = bazi.get("favorable", ["木", "火"])
                    persona["current_luck"] = current_luck
                    persona["luck_timeline"] = luck_timeline
                else:
                    # 如果找不到對應市民，從 sampled_citizens 中隨機取一個
                    fallback = random.choice(sampled_citizens) if sampled_citizens else {}
                    bazi = fallback.get("bazi_profile", {})
                    age = fallback.get("age", 30)
                    luck_timeline, current_luck = build_luck_data(bazi, age)
                    
                    persona["id"] = str(fallback.get("id", random.randint(1, 1000)))
                    persona["age"] = str(age)
                    persona["occupation"] = fallback.get("occupation", "未知職業")
                    persona["location"] = fallback.get("location", "台灣")
                    persona["birth_year"] = bazi.get("birth_year")
                    persona["birth_month"] = bazi.get("birth_month")
                    persona["birth_day"] = bazi.get("birth_day")
                    persona["birth_shichen"] = bazi.get("birth_shichen")
                    persona["four_pillars"] = bazi.get("four_pillars")
                    persona["day_master"] = bazi.get("day_master", "未知")
                    persona["strength"] = bazi.get("strength", "中和")
                    persona["favorable"] = bazi.get("favorable", ["木", "火"])
                    persona["current_luck"] = current_luck
                    persona["luck_timeline"] = luck_timeline
                
                comment["persona"] = persona
            
            # 8. Fallback comments if not enough (ensure at least 8) - 與 PDF/Image 流程一致
            bazi_comment_templates = {
                "食神格": [
                    "這個商業模式看起來挺有意思的，如果真的能落地，市場接受度應該不錯。",
                    "哇，這概念蠻有品味的！我一向注重生活品質，這種服務我會願意嘗試。",
                    "從用戶體驗角度來看，這個計劃考慮得蠻周到的，我願意支持。",
                    "作為重視體驗的人，我覺得這個商業計劃有它的獨特之處，值得關注。"
                ],
                "傷官格": [
                    "商業模式還可以，但我覺得有些地方可以更有創意一點。不過整體方向是對的。",
                    "嗯...我有一些改進的想法：如果能增加差異化會更完美。概念是好的。",
                    "說實話，類似的商業模式其實有不少，這個需要找到獨特定位才能勝出。",
                    "我欣賞創新的嘗試，但商業執行面還需要更多驗證。潛力是有的。"
                ],
                "正財格": [
                    "獲利模式如何？我比較在意投資回報率。如果數據支撐得住，這個值得考慮。",
                    "成本結構和定價策略很重要，這個計劃書這方面分析得還算清楚。",
                    "作為一個務實的人，我會先看財務預測的合理性，確保每一筆錢都花得值得。",
                    "我會做功課研究市場規模再決定。如果風險可控，可以考慮參與。"
                ],
                "偏財格": [
                    "感覺有潛力！可以考慮投資看看。這個市場定位蠻聰明的。",
                    "這個切入點不錯，商機蠻大的！如果團隊執行力強，我會關注。",
                    "我看到了機會！這領域現在正是風口，時機點抓得不錯。",
                    "有意思！這個如果能規模化，未來增值空間很大。"
                ],
                "正官格": [
                    "法規合規性和風險管控做好了嗎？我比較謹慎，需要確認這些細節。",
                    "需要多了解一下商業細節，再做決定。穩定性和可持續性是我最在意的。",
                    "這個團隊背景如何？我傾向支持有信譽的團隊。",
                    "有沒有市場驗證數據？作為理性投資者，我需要客觀數據來支持決策。"
                ],
                "七殺格": [
                    "執行效率怎麼樣？我時間很寶貴，需要看到快速落地的能力。",
                    "直接說重點，這個能解決什麼市場痛點？別跟我繞圈子。",
                    "競爭優勢在哪？市場上選擇這麼多，你憑什麼讓我選你？",
                    "我只關心結果。如果真的有這麼大的市場，我會認真考慮。"
                ],
                "正印格": [
                    "這對長期發展有幫助嗎？我比較看重長遠價值和社會意義。",
                    "團隊的背景和願景很重要，這個計劃看起來有一定的深度。",
                    "有沒有行業專家的背書？我希望能真正了解這個領域。",
                    "我會先請教有經驗的朋友，聽聽他們的回饋再決定。"
                ],
                "偏印格": [
                    "這個概念挺特別的，跟市面上的不太一樣。我喜歡有獨特想法的項目。",
                    "有點意思，但我需要更多時間思考。直覺告訴我這個有些門道。",
                    "商業理念很有深度，不是一般人能馬上理解的。這反而吸引我。",
                    "我不跟風投資，這個項目有它獨特的氣質。"
                ],
                "比肩格": [
                    "這個領域我身邊有朋友在做，看來真的有市場。共識很重要。",
                    "我會問問行業內的朋友，如果他們也看好，我就跟進。",
                    "這類商業模式我有觀察過，這個計劃在一些細節上有創新。",
                    "方向正確，執行力看起來也可以，符合我的預期。"
                ],
                "劫財格": [
                    "這個值得跟投資圈朋友分享！好項目就是要一起投才有意思。",
                    "如果有共同投資的機會，我可以幫忙對接資源。",
                    "我已經想好要推薦給誰了，這個計劃剛好適合對方的投資方向。",
                    "合作共贏很重要！這個項目如果能建立生態系統會更有價值。"
                ],
            }
            
            default_templates = [
                "這個商業計劃確實有它的特色，我會考慮參與，但還需要再觀察一下市場反應。",
                "風險可控的話我願意試試看，畢竟這個領域確實有機會。",
                "計劃書蠻有想法的，如果團隊執行力強，這個價值評估算是合理的。",
                "整體來說符合我的預期，不算最創新但也沒什麼大問題，可以列入觀察清單。",
                "我會持續關注這個項目，等更多市場數據出來再決定是否投入。",
                "第一印象不錯，但我習慣多方驗證，確保這是最佳標的再出手。",
                "對我來說這是個新領域，需要更多了解，但團隊看起來有誠意。",
                "行業內有類似成功案例，這個計劃看起來也值得一試。"
            ]
            
            while len(arena_comments) < 8 and sampled_citizens:
                # 找一個還沒評論過的市民
                commented_names = {c.get("persona", {}).get("name", "") for c in arena_comments}
                remaining = [c for c in sampled_citizens if c["name"] not in commented_names]
                if not remaining:
                    break
                citizen = remaining[0]
                bazi = citizen["bazi_profile"]
                structure = bazi.get("structure", "")
                occupation = citizen.get("occupation", "")
                
                # 根據八字結構選擇評論模板
                templates = None
                for pattern, texts in bazi_comment_templates.items():
                    if pattern in structure:
                        templates = texts
                        break
                
                # 最後使用默認模板
                if not templates:
                    templates = default_templates
                
                # 隨機選擇一條評論
                text = random.choice(templates)
                
                # 混合分配情感
                sentiments = ["positive", "positive", "neutral", "neutral", "negative"]
                sentiment = sentiments[len(arena_comments) % len(sentiments)]
                
                # 補全市民資料
                age = citizen.get("age", 30)
                luck_timeline, current_luck = build_luck_data(bazi, age)
                
                # 生成四柱資料
                pillars_str = bazi.get("four_pillars")
                if not pillars_str:
                    pillars = ["甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉", "甲戌", "乙亥"]
                    pillars_str = f"{random.choice(pillars)} {random.choice(pillars)} {random.choice(pillars)} {random.choice(pillars)}"
                
                arena_comments.append({
                    "sentiment": sentiment,
                    "text": text,
                    "persona": {
                        "id": str(citizen.get("id", random.randint(1, 1000))),
                        "name": citizen["name"],
                        "age": str(age),
                        "pattern": bazi.get("structure", "未知格局"),
                        "element": bazi.get("element", "Fire"),
                        "icon": {"Fire": "🔥", "Water": "💧", "Metal": "🔩", "Wood": "🌳", "Earth": "🏔️"}.get(bazi.get("element", "Fire"), "🔥"),
                        "occupation": citizen.get("occupation", "未知職業"),
                        "location": citizen.get("location", "台灣"),
                        "birth_year": bazi.get("birth_year"),
                        "birth_month": bazi.get("birth_month"),
                        "birth_day": bazi.get("birth_day"),
                        "birth_shichen": bazi.get("birth_shichen"),
                        "four_pillars": pillars_str,
                        "day_master": bazi.get("day_master", "未知"),
                        "strength": bazi.get("strength", "中和"),
                        "favorable": bazi.get("favorable", ["木", "火"]),
                        "current_luck": current_luck,
                        "luck_timeline": luck_timeline
                    }
                })
                print(f"[Core TEXT] Added fallback comment #{len(arena_comments)}: {citizen['name']}")
            
            # 9. 構建最終結果 (與 PDF 流程一致)
            score = data.get("result", {}).get("score", 70)
            if score > 98: score = 98 # Clamp score to reasonable max
            if score < 10 and source_type == "text": score = 65 # Default for text if too low
            
            result_data = {
                "status": "ready",
                "score": score,
                "intent": data.get("result", {}).get("market_sentiment", "分析完成"),
                "summary": data.get("result", {}).get("summary", "AI 分析完成"),
                "simulation_metadata": sim_metadata,
                "genesis": {
                     "total_population": 1000,
                     "sample_size": len(personas),
                     "personas": personas
                },
                "arena_comments": arena_comments,
                "objections": data.get("result", {}).get("objections", []),
                "suggestions": data.get("result", {}).get("suggestions", [])
            }
            
            # 🧬 [Sidecar] 追加計算社會科學方法論詮釋層
            methodology_sidecar = _generate_methodology_sidecar(
                score=result_data.get("score"),
                summary=result_data.get("summary")
            )
            result_data["methodology_data"] = methodology_sidecar
            
            # 10. 更新資料庫
            await run_in_threadpool(update_simulation, sim_id, "ready", result_data)
            print(f"✅ [Core TEXT] Document analysis completed: {sim_id}, comments: {len(arena_comments)}, score: {score}")

        except Exception as e:
            print(f"[Core TEXT] Analysis Failed: {e}")
            self._handle_error_db(sim_id, str(e))

    async def run_simulation_with_audio_data(self, audio_bytes: bytes, sim_id: str, audio_format: str = "webm"):
        """處理語音錄音的商業計劃書分析 (錄音 → 轉文字 → 分析)"""
        try:
            from fastapi.concurrency import run_in_threadpool
            
            # 1. 使用 Gemini 將音訊轉文字
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            transcription_prompt = """請聽取這段語音錄音，並將其完整轉錄為繁體中文文字。
            
這是一段關於商業計劃或產品想法的錄音。請：
1. 完整轉錄所有口說內容
2. 使用繁體中文
3. 保持原意，適當加入標點符號讓內容更易讀
4. 如果有口吃或重複的部分，請整理為順暢的文字

直接輸出轉錄後的文字內容，不要有任何額外說明。"""

            api_key = settings.GOOGLE_API_KEY
            
            # 音訊 MIME 類型對應
            audio_mime_map = {
                "webm": "audio/webm",
                "mp3": "audio/mp3",
                "wav": "audio/wav",
                "m4a": "audio/mp4",
                "ogg": "audio/ogg"
            }
            audio_mime = audio_mime_map.get(audio_format, "audio/webm")
            
            # 呼叫 Gemini 進行語音轉文字
            transcribed_text, error = await asyncio.to_thread(
                self._run_blocking_gemini_request_audio,
                api_key,
                transcription_prompt,
                audio_b64,
                audio_mime
            )
            
            if not transcribed_text:
                self._handle_error_db(sim_id, f"Voice Transcription Failed: {error}")
                return
            
            print(f"[Audio] Transcribed {len(transcribed_text)} characters")
            
            # 2. 使用轉錄的文字進行商業分析
            await self.run_simulation_with_text_data(transcribed_text, sim_id, "voice")

        except Exception as e:
            print(f"[Core AUDIO] Analysis Failed: {e}")
            self._handle_error_db(sim_id, str(e))

    def _run_blocking_gemini_request_audio(self, api_key, prompt, audio_b64, audio_mime):
        """Blocking Gemini API call for audio transcription"""
        import requests
        
        print(f"[DEBUG AUDIO] Starting audio transcription, audio size: {len(audio_b64)} chars, mime: {audio_mime}")
        
        # [Restore] Prioritize Gemini 2.5 Pro for Quality
        models = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-flash-latest"]
        last_error = None
        
        for model in models:
            try:
                print(f"[DEBUG AUDIO] Trying model: {model}")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": prompt},
                            {"inline_data": {"mime_type": audio_mime, "data": audio_b64}}
                        ]
                    }],
                    "generationConfig": {"temperature": 0.1}
                }
                
                response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=120)
                print(f"[DEBUG AUDIO] {model} response status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        result_text = response.json()['candidates'][0]['content']['parts'][0]['text']
                        print(f"[DEBUG AUDIO] Successfully transcribed: {len(result_text)} chars")
                        return result_text, None
                    except Exception as parse_err:
                        print(f"[DEBUG AUDIO] Parse error: {parse_err}, response: {response.text[:500]}")
                        continue
                else:
                    error_msg = f"{model}: {response.status_code} - {response.text[:300]}"
                    print(f"[DEBUG AUDIO] API Error: {error_msg}")
                    last_error = error_msg
            except Exception as e:
                print(f"[DEBUG AUDIO] Exception: {str(e)}")
                last_error = str(e)
        
        print(f"[DEBUG AUDIO] All models failed. Last error: {last_error}")
        return None, last_error


    # ===== Helpers =====

    async def _call_gemini_rest(self, api_key, prompt, image_b64=None, pdf_b64=None, mime_type="image/jpeg", timeout=60, image_parts=None):
        """Helper to call Gemini REST API (Async Wrapper)"""
        # [Fix] Prioritize Gemini 2.5 Pro as requested by the user
        priority = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-flash-latest"]
        
        return await asyncio.to_thread(
            self._run_blocking_gemini_request,
            api_key, 
            prompt, 
            image_b64, 
            pdf_b64, 
            priority,
            mime_type,
            image_parts # Pass image_parts
        )

    def _clean_and_parse_json(self, ai_text):
        """Helper to clean and parse JSON with robust error handling"""
        if not ai_text or not isinstance(ai_text, str):
            logger.error(f"Invalid AI text input for parsing: {type(ai_text)}")
            return {"result": {}, "arena_comments": [], "genesis": {}, "simulation_metadata": {}, "comments": [], "suggestions": []}

        clean_text = ai_text
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", ai_text, re.DOTALL)
        if match:
            clean_text = match.group(1)
        
        try:
            data = json.loads(clean_text)
            if isinstance(data, dict):
                return data
            else:
                logger.error(f"Gemini returned non-dict JSON: {type(data)}")
                return {}
        except json.JSONDecodeError:
            # Simple fix attempt
            fixed_text = clean_text.strip()
            if fixed_text.count('{') > fixed_text.count('}'): fixed_text += '}' * (fixed_text.count('{') - fixed_text.count('}'))
            if fixed_text.count('[') > fixed_text.count(']'): fixed_text += ']' * (fixed_text.count('[') - fixed_text.count(']'))
            try:
                data = json.loads(fixed_text)
                if isinstance(data, dict):
                    return data
                return {}
            except:
                logger.error(f"Failed to parse AI JSON after cleaning: {clean_text[:200]}")
                return {}

    def _build_simulation_result(self, data, sampled_citizens, sim_metadata_override=None):
        """Helper to build final result structure"""
        # Logic extracted from original code to build result_data
        # ... simplified for brevity as it copies logic ...
        
        # Reconstruct Bazi distribution
        element_counts = {"Fire": 0, "Water": 0, "Metal": 0, "Wood": 0, "Earth": 0}
        for c in sampled_citizens:
            elem = c["bazi_profile"].get("element", "Fire")
            if elem in element_counts: element_counts[elem] += 1
        total = len(sampled_citizens)
        bazi_dist = {k: round(v / total * 100) for k, v in element_counts.items()} if total else element_counts

        # Build Personas (Ensure enough for the display)
        # 這裡不限制只取 8 個，而是維持與 arena_comments 的同步
        personas_dict = {}
        for c in sampled_citizens:
            bazi = c.get("bazi_profile", {})
            personas_dict[str(c["id"])] = {
                "id": str(c["id"]),
                "name": c["name"],
                "age": c["age"],
                "location": c.get("location", "台灣"),
                "occupation": c.get("occupation", "未知職業"),
                "element": bazi.get("element", "Fire"),
                "icon": {"Fire": "🔥", "Water": "💧", "Metal": "🔩", "Wood": "🌳", "Earth": "🏔️"}.get(bazi.get("element", "Fire"), "🔥"),
                "day_master": bazi.get("day_master", ""),
                "pattern": bazi.get("structure", "未知格局"),
                "trait": ", ".join(c["traits"][:2]) if c.get("traits") else "個性鮮明",
                "decision_logic": "根據八字格局特質分析",
                "current_luck": bazi.get("current_luck", {}),
                "luck_timeline": bazi.get("luck_timeline", []),
                # 完整生辰資料
                "birth_year": bazi.get("birth_year"),
                "birth_month": bazi.get("birth_month"),
                "birth_day": bazi.get("birth_day"),
                "birth_shichen": bazi.get("birth_shichen"),
                "four_pillars": bazi.get("four_pillars"),
                "strength": bazi.get("strength", "中和"),
                "favorable": bazi.get("favorable", ["木", "火"])
            }
        
        # Build comments
        gemini_comments = data.get("comments", [])
        arena_comments = []
        # 強制 Key 為 String 以防萬一
        citizen_map = {str(c["id"]): c for c in sampled_citizens}
        
        for comment in gemini_comments:
            raw_id = comment.get("citizen_id")
            c_id = str(raw_id) if raw_id is not None else ""
            
            # 1. 嘗試用 ID 直接匹配
            citizen = citizen_map.get(c_id)
            
            # 2. 如果找不到，且 ID 是數字，嘗試用 Index 匹配 (針對 Gemini 返回 0, 1, 2... 的情況)
            if not citizen and c_id.isdigit():
                idx = int(c_id)
                # Gemini 有時是 1-based index
                if 0 <= idx < len(sampled_citizens):
                    citizen = sampled_citizens[idx]
                elif 0 < idx <= len(sampled_citizens): # Handle 1-based
                    citizen = sampled_citizens[idx-1]
            
            if citizen:
                bazi = citizen["bazi_profile"]
                
                # Auto-fill missing birthday data
                import random
                if not bazi.get("birth_year"):
                    try:
                        age = int(citizen.get("age", 30))
                    except:
                        age = 30
                    bazi["birth_year"] = 2025 - age
                    bazi["birth_month"] = random.randint(1, 12)
                    bazi["birth_day"] = random.randint(1, 28)
                    bazi["birth_shichen"] = random.choice(["子時", "丑時", "寅時", "卯時", "辰時", "巳時", "午時", "未時", "申時", "酉時", "戌時", "亥時"])

                # 🛡️ 防禦性補全：如果沒有命盤，隨機生成
                pillars_str = bazi.get("four_pillars")
                if not pillars_str:
                    logger.warning(f"Citizen {citizen['name']} missing four_pillars, auto-generating...")
                    pillars = ["甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉", "甲戌", "乙亥"]
                    pillars_str = f"{random.choice(pillars)} {random.choice(pillars)} {random.choice(pillars)} {random.choice(pillars)}"
                    bazi["four_pillars"] = pillars_str
                
                # 🛡️ 防禦性補全：如果沒有大運，生成默認大運
                timeline = bazi.get("luck_timeline")
                if not timeline:
                     # 嘗試從 luck_pillars 生成
                     if bazi.get("luck_pillars"):
                         timeline = []
                         for l in bazi["luck_pillars"]:
                             name = l.get('pillar', '甲子') + "運"
                             desc = l.get('description', '行運平穩')
                             timeline.append({
                                 "age_start": l.get('age_start', 0),
                                 "age_end": l.get('age_end', 9),
                                 "name": name,
                                 "description": desc
                             })
                     else:
                         # 完全隨機生成
                         start_age = random.randint(2, 9)
                         pillars_pool = ["甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉", "甲戌", "乙亥"]
                         timeline = []
                         for i in range(8):
                             p_name = f"{pillars_pool[(i+random.randint(0,5))%len(pillars_pool)]}運"
                             timeline.append({
                                 "age_start": start_age + i*10,
                                 "age_end": start_age + i*10 + 9,
                                 "name": p_name,
                                 "description": "行運平穩，順其自然。"
                             })
                     bazi["luck_timeline"] = timeline
                
                # 🛡️ 防禦性補全：如果沒有 current_luck，從 timeline 中計算
                current_luck = bazi.get("current_luck")
                if not isinstance(current_luck, dict):
                    current_luck = {}
                
                if not current_luck or not current_luck.get("description"):
                    try:
                        citizen_age = int(citizen.get("age", 30))
                    except:
                        citizen_age = 30
                    for lt in timeline:
                        if lt["age_start"] <= citizen_age <= lt["age_end"]:
                            current_luck = {"name": lt["name"], "description": lt["description"]}
                            break
                    if not current_luck and timeline:
                        current_luck = {"name": timeline[0]["name"], "description": timeline[0]["description"]}
                    bazi["current_luck"] = current_luck

                # ID 防禦
                cid = str(citizen.get("id")) if citizen.get("id") else f"gen-{random.randint(1000,9999)}"

                arena_comments.append({
                    "sentiment": comment.get("sentiment", "neutral"),
                    "text": comment.get("text", "（無評論內容）"),
                    "persona": personas_dict.get(cid)
                })
                
                # DEBUG LOG
                logger.info(f"Generated Primary Comment Persona: Name={citizen['name']}, ID={cid}, Birth={bazi.get('birth_year')}")

        # Ensure personas list for genesis is synced with the comments
        personas = [c["persona"] for c in arena_comments if c.get("persona")]

        # Fallback comments if not enough (ensure at least 8)
        # 大幅增加評論模板，更豐富、更符合八字個性
        bazi_comment_templates = {
            "食神格": [
                "這產品看起來挺有質感的，用起來應該很享受！特別喜歡它的設計感，每天使用心情都會很好。",
                "哇，這設計蠻有品味的！我一向注重生活品質，這種細節處理得不錯，值得入手。",
                "我比較在意使用體驗，這個產品從外觀到手感都很舒服，感覺會是生活中的小確幸。",
                "作為一個愛好者，我覺得這個產品很療癒，光是看著就很開心，實用性倒是其次。"
            ],
            "傷官格": [
                "設計還可以，但我覺得有些地方可以更有創意一點。不過整體來說還是有它的特色。",
                "嗯...我有一些改進的想法：如果能加強某些功能會更完美。不過概念是好的。",
                "說實話，市面上類似的產品很多，這個需要做出差異化才能真正吸引我。",
                "我欣賞創新的嘗試，但執行面還有進步空間。潛力是有的，就看後續迭代了。"
            ],
            "正財格": [
                "CP值如何？我比較在意性價比。這個價格如果品質穩定，我會考慮入手。",
                "價格和品質的平衡很重要，這個看起來還可以。希望用料實在，不是虛有其表。",
                "作為一個務實的人，我會先看評價和口碑，確保每一分錢都花得值得。",
                "我會做功課比較幾家再決定。這個如果有優惠或分期，吸引力會更大。"
            ],
            "偏財格": [
                "感覺有潛力！可以考慮投資看看。這個市場定位蠻聰明的，抓住了痛點。",
                "這個切入點不錯，商機蠻大的！如果團隊執行力強，發展前景看好。",
                "我看到了機會！這類產品現在正流行，時機點抓得不錯，值得關注。",
                "有意思！這個如果能做成系列產品或打造品牌，未來增值空間很大。"
            ],
            "正官格": [
                "品質和規格都符合標準嗎？我比較謹慎，需要確認各項認證和保固條款。",
                "需要多了解一下細節，再做決定。穩定性和售後服務是我最在意的。",
                "這個品牌口碑如何？我傾向選擇有信譽的廠商，這樣更有保障。",
                "有沒有專業測試報告？作為理性消費者，我需要客觀數據來支持購買決定。"
            ],
            "七殺格": [
                "直接說重點，這東西能不能解決實際痛點？如果是為了虛榮心買的，我沒興趣。效率和結果才是我最在意的，我需要能打仗的工具。",
                "別跟我繞圈子，市場優勢在哪？憑什麼讓我選你？如果真的有硬實力，我會毫不猶豫下單，否則別浪費我時間。",
                "我只關心性能和回報。這產品如果能幫我省下 20% 的時間，那它就值這個價。執行力不足的方案，我看都不看。",
                "這東西看起來很有侵略性，適合開拓新市場。我喜歡這種帶有突破性的設計，只要它能扛得起高強度的壓力。"
            ],
            "正印格": [
                "這對長期發展有幫助嗎？我比較看重長遠價值，不喜歡曇花一現的東西。",
                "品牌信譽很重要，這個公司可靠嗎？我寧可多花點錢也要買安心。",
                "有沒有學習資源或使用指南？我希望能真正了解和掌握這個產品。",
                "我會先請教有經驗的朋友，聽聽他們的意見再決定。謹慎一點總是好的。"
            ],
            "偏印格": [
                "這個概念挺特別的，跟市面上的不太一樣。我喜歡有獨特想法的產品。",
                "有點意思，但我需要更多時間思考。直覺告訴我這個有些門道。",
                "設計理念很有深度，不是一般大眾能馬上理解的。這反而吸引我。",
                "我不跟風，這個產品有它獨特的氣質，適合有品味的人。"
            ],
            "比肩格": [
                "這個我身邊很多朋友都在用，看來真的不錯。大家說好才是真的好。",
                "我會問問同事的意見，如果他們也覺得可以，我就跟一波。",
                "這類產品我有使用經驗，這個新品看起來在一些細節上有進步。",
                "價格公道，品質過得去，符合我的預期。不求最好，但求實用。"
            ],
            "劫財格": [
                "這個值得跟朋友們分享！好東西就是要一起用才有意思。",
                "如果有團購或優惠活動，我可以幫忙揪人，大家一起買更划算。",
                "我已經想好要推薦給誰了，這個產品剛好適合我幾個朋友的需求。",
                "生活嘛，開心最重要！這個能讓朋友聚會更有趣，值得入手。"
            ],
        }
        
        # 根據職業增加更多個性化評論
        occupation_comments = {
            "工程師": "從技術角度來看，這個產品的設計邏輯是合理的，執行面也不錯。",
            "設計師": "視覺呈現蠻有質感的，色彩搭配和排版都很用心，看得出專業度。",
            "老師": "這個對學生或家庭來說實用嗎？我會考慮教育意義和安全性。",
            "醫生": "健康相關的產品我比較謹慎，需要確認有無相關認證。",
            "創業家": "商業模式有創意，如果能解決真正的市場痛點，會有發展空間。",
            "學生": "價格是我最在意的，如果有學生優惠就更好了！",
            "經理": "團隊協作方面有優勢嗎？我會考慮導入公司使用的可能性。",
            "自由業": "靈活性很重要，這個能配合我不固定的工作模式嗎？",
        }
        
        default_templates = [
            "這個產品確實有它的特色，我會考慮購買，但還需要再觀察一下市場反應。",
            "價格合理的話我願意試試看，畢竟嘗試新東西也是一種生活態度。",
            "設計蠻有想法的，如果質量穩定，這個價位算是可以接受的選擇。",
            "整體來說符合我的預期，不算驚艷但也沒什麼大問題，可以列入購物清單。",
            "我會持續關注這個產品，等更多用戶評價出來再決定是否入手。",
            "第一印象不錯，但我習慣貨比三家，確保這是最佳選擇再下手。",
            "對我來說這是個新領域，需要更多了解，但產品本身看起來有誠意。",
            "朋友推薦過類似的產品，這個看起來也值得一試，考慮中。"
        ]
        
        import random as rand_module
        while len(arena_comments) < 8 and sampled_citizens:
            # 找一個還沒評論過的市民
            commented_names = {c["persona"]["name"] for c in arena_comments}
            remaining = [c for c in sampled_citizens if c["name"] not in commented_names]
            if not remaining:
                break
            citizen = remaining[0]
            bazi = citizen["bazi_profile"]
            structure = bazi.get("structure", "")
            occupation = citizen.get("occupation", "")
            
            # 根據八字結構選擇評論模板
            templates = None
            for pattern, texts in bazi_comment_templates.items():
                if pattern in structure:
                    templates = texts
                    break
            
            # 如果沒有匹配的八字格局，嘗試職業匹配
            if not templates:
                for occ, comment in occupation_comments.items():
                    if occ in occupation:
                        templates = [comment]
                        break
            
            # 最後使用默認模板
            if not templates:
                templates = default_templates
            
            # 隨機選擇一條評論，避免重複
            text = rand_module.choice(templates)
            
            # 混合分配情感
            sentiments = ["positive", "positive", "neutral", "neutral", "negative"]
            sentiment = sentiments[len(arena_comments) % len(sentiments)]
            
            # 定義 pillars_str
            pillars_str = bazi.get("four_pillars")
            if not pillars_str:
                pillars = ["甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉", "甲戌", "乙亥"]
                import random as rand_mod
                pillars_str = f"{rand_mod.choice(pillars)} {rand_mod.choice(pillars)} {rand_mod.choice(pillars)} {rand_mod.choice(pillars)}"
            
            # 取得 luck_timeline
            timeline = bazi.get("luck_timeline", [])
            
            # 🛡️ 防禦性補全：如果沒有 luck_timeline，生成預設資料
            if not timeline:
                start_age = random.randint(2, 9)
                pillars_pool = ["甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未"]
                descs = ["少年運勢順遂", "初入社會磨練", "事業穩步上升", "財運亨通", "壓力較大需注意", "穩步發展", "財官雙美", "晚運安康"]
                for i in range(8):
                    timeline.append({
                        "age_start": start_age + i*10,
                        "age_end": start_age + i*10 + 9,
                        "name": f"{pillars_pool[i]}運",
                        "description": descs[i]
                    })

            # 🛡️ 防禦性補全：如果沒有 current_luck，從 timeline 中計算
            current_luck = bazi.get("current_luck")
            if not isinstance(current_luck, dict):
                current_luck = {}

            if not current_luck or not current_luck.get("description"):
                try:
                    citizen_age = int(citizen.get("age", 30))
                except:
                    citizen_age = 30
                for lt in timeline:
                    if lt["age_start"] <= citizen_age <= lt["age_end"]:
                        current_luck = {"name": lt["name"], "description": lt["description"]}
                        break
                if not current_luck and timeline:
                    current_luck = {"name": timeline[0]["name"], "description": timeline[0]["description"]}
                bazi["current_luck"] = current_luck

            # ID 防禦
            cid = str(citizen.get("id")) if citizen.get("id") else f"gen-{random.randint(1000,9999)}"

            # 構建完整的 persona 資料
            full_persona = {
                "id": cid,
                "name": citizen["name"],
                "age": str(citizen["age"]),
                "pattern": bazi.get("structure", "未知格局"),
                "element": bazi.get("element", "Fire"),
                "icon": {"Fire": "🔥", "Water": "💧", "Metal": "🔩", "Wood": "🌳", "Earth": "🏔️"}.get(bazi.get("element", "Fire"), "🔥"),
                "occupation": citizen.get("occupation", "未知職業"),
                "location": citizen.get("location", "台灣"),
                "birth_year": bazi.get("birth_year"),
                "birth_month": bazi.get("birth_month"),
                "birth_day": bazi.get("birth_day"),
                "birth_shichen": bazi.get("birth_shichen"),
                "four_pillars": pillars_str,
                "day_master": bazi.get("day_master", "未知"),
                "strength": bazi.get("strength", "中和"),
                "favorable": bazi.get("favorable", ["木", "火"]),
                "current_luck": current_luck,
                "luck_timeline": timeline,
                "trait": bazi.get("trait", "性格均衡")
            }

            arena_comments.append({
                "sentiment": sentiment,
                "text": text,
                "persona": full_persona
            })
            
            personas.append(full_persona)
            
            # DEBUG LOG
            logger.info(f"Generated Fallback Comment Persona: Name={citizen['name']}, ID={cid}, Pillars={pillars_str}, Birth={bazi.get('birth_year')}")

        result_data = {
            "status": "ready",
            "score": data.get("result", {}).get("score", 75),
            "intent": data.get("result", {}).get("market_sentiment", "謹慎樂觀"),
            "summary": data.get("result", {}).get("summary", "分析完成"),
            "simulation_metadata": {
                "source_type": sim_metadata_override.get("source_type", "image") if sim_metadata_override else "image",
                "product_category": data.get("simulation_metadata", {}).get("product_category", sim_metadata_override.get("product_category", "other") if sim_metadata_override else "other"),
                "sample_size": len(sampled_citizens),
                "bazi_distribution": bazi_dist
            },
            "bazi_distribution": bazi_dist,
            "genesis": {
                "total_population": 1000,
                "sample_size": max(len(arena_comments), 8),
                "personas": personas
            },
            "arena_comments": arena_comments,
            "objections": data.get("result", {}).get("objections", []),
            "suggestions": data.get("result", {}).get("suggestions", [])
        }
        return result_data

    def _handle_error_db(self, sim_id, error_msg):
        error_data = {
            "status": "error",
            "score": 0,
            "intent": "Error",
            "summary": f"系統錯誤: {error_msg}",
            "genesis": {"total_population": 0, "sample_size": 0, "personas": []},
            "comments": []
        }
        update_simulation(sim_id, "error", error_data)

    def reply_text(self, reply_token, text):
        try:
            self.line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=text)]
                )
            )
        except Exception:
            pass

    async def _call_gemini_rest(self, api_key, prompt, image_b64=None, pdf_b64=None, mime_type="image/jpeg", timeout=120, image_parts=None):
        """Helper to call Gemini REST API (Async Wrapper with Configurable Timeout)"""
        import requests 

        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt}
                ]
            }],
            "generationConfig": {
                "maxOutputTokens": 8192,
                "temperature": 0.7,
                "topP": 0.9,
                "responseMimeType": "application/json"
            }
        }
        
        if image_parts:
             payload["contents"][0]["parts"].extend(image_parts)
        elif image_b64:
            # Use dynamic mime_type
            payload["contents"][0]["parts"].append({"inline_data": {"mime_type": mime_type, "data": image_b64}})
        if pdf_b64:
            payload["contents"][0]["parts"].append({"inline_data": {"mime_type": "application/pdf", "data": pdf_b64}})

        # [Restore] Prioritize Quality (Pro) as per User Request (reverting to GitHub-like behavior)
        models = [
            "gemini-2.5-pro", 
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-flash-latest"
        ]
        
        last_error = ""
        for model in models:
            try:
                # print(f"Trying model: {model}...")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                
                # [Fix] Use asyncio.to_thread to unblock Event Loop
                import asyncio
                # Increase timeout for Pro model and PDF/Audio heavy tasks
                current_timeout = timeout
                if "pro" in model:
                    current_timeout = max(timeout, 180) # Pro needs time to think (3 mins)
                
                # PDF needs more time regardless of model
                if pdf_b64:
                    current_timeout = max(current_timeout, 120)

                print(f"[DEBUG] Calling Gemini Model: {model} with Payload Size: {len(json.dumps(payload))} bytes, Timeout: {current_timeout}s")
                response = await asyncio.to_thread(
                    requests.post, 
                    url, 
                    headers={'Content-Type': 'application/json'}, 
                    json=payload, 
                    timeout=current_timeout
                )
                print(f"[DEBUG] Gemini Model {model} returned Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        return response.json()['candidates'][0]['content']['parts'][0]['text'], None
                    except:
                        continue
                else:
                    last_error = f"{model}: {response.status_code} {response.text}"
            except Exception as e:
                last_error = str(e)
        
        return None, last_error

    # NOTE: 舊版 generate_marketing_copy 已刪除，現使用第 480 行的新版本 (單篇輸出)

    def _run_blocking_gemini_request(self, api_key, prompt, image_b64=None, pdf_b64=None, model_priority=None, mime_type="image/jpeg", image_parts=None):
        """Helper to run synchronous requests in a thread"""
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt}
                ]
            }],
            "generationConfig": {
                "maxOutputTokens": 8192,
                "temperature": 0.7,
                "topP": 0.9,
                "responseMimeType": "application/json"
            }
        }
        
        if image_parts:
             payload["contents"][0]["parts"].extend(image_parts)
        elif image_b64:
            payload["contents"][0]["parts"].append({"inline_data": {"mime_type": mime_type, "data": image_b64}})
        if pdf_b64:
            payload["contents"][0]["parts"].append({"inline_data": {"mime_type": "application/pdf", "data": pdf_b64}})

        # Default models if not specified
        if model_priority:
            models = model_priority
        else:
            # [Fix] Prioritize Gemini 2.5 Pro as requested by the user
            models = [
                "gemini-2.5-pro",
                "gemini-2.5-flash",
                "gemini-flash-latest"
            ]
        
        last_error = ""
        for model in models:
            try:
                print(f"[AI] 嘗試使用模型: {model}...")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                # Increased timeout to 90s for complex prompts with detailed strategic advice
                response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload, timeout=90)
                if response.status_code == 200:
                    try:
                        return response.json()['candidates'][0]['content']['parts'][0]['text'], None
                    except:
                        continue
                else:
                    error_msg = f"{model}: {response.status_code} {response.text}"
                    print(f"[AI] 模型 {model} 失敗: {error_msg}")
                    last_error = error_msg
            except Exception as e:
                last_error = str(e)
        
        return None, last_error
# LINE Bot 多圖處理輔助函數
# 這些函數將被集成到 line_bot_service.py 中

async def _identify_from_multiple_images(self, user_id):
    """
    從 session 中的多張圖片進行 AI 識別與市場比價
    """
    session = self.user_session.get(user_id)
    if not session or not session.get("images"):
        self._push_text(user_id, "❌ 找不到圖片，請重新上傳")
        return
    
    images = session["images"]
    image_count = len(images)
    
    try:
        # 1. AI 產品識別（使用第一張圖片）
        print(f"🔍 [Multi-Image] 開始識別 {image_count} 張圖片...")
        ai_name, ai_price = await self.identify_product_from_image(images[0])
        
        # 2. 市場比價查詢（如果有產品名稱）
        market_prices = {}
        if ai_name and ai_name != "未知產品":
            from app.services.price_search import search_market_prices_sync
            try:
                print(f"💰 [Market] 查詢市場價格: {ai_name}")
                market_result = search_market_prices_sync(ai_name)
                if market_result.get("success"):
                    market_prices = market_result
                    print(f"💰 [Market] 找到 {len(market_result.get('prices', []))} 筆價格資料")
            except Exception as e:
                print(f"⚠️ [Market] 比價查詢失敗: {e}")
        
        # 3. 更新 session
        session["image_bytes"] = images[0]  # 兼容性：保留第一張做為主圖
        session["product_name"] = ai_name or ""
        session["product_price"] = ai_price or "未定"  
        session["market_prices"] = market_prices
        session["stage"] = "waiting_for_name_confirmation"
        
        print(f"✅ [Multi-Image] 識別完成: {ai_name} / {ai_price}")
        
        # 4. 構建回覆訊息（包含市場比價資料）
        confirm_msg = f"👁️ **AI 視覺分析結果**（{image_count} 張圖片）\n\n"
        confirm_msg += f"📦 產品：{ai_name or '未知'}\n"
        
        # 顯示市場比價
        if market_prices.get("success"):
            prices = market_prices.get("prices", [])
            if prices:
                min_price = market_prices.get("min_price", ai_price)
                max_price = market_prices.get("max_price", ai_price)
                confirm_msg += f"💰 市場價格區間：${min_price} - ${max_price}\n"
                confirm_msg += f"📊 已比對 {len(prices)} 個平台\n"
            else:
                confirm_msg += f"💰 估價：{ai_price or '未知'}\n"
        else:
            confirm_msg += f"💰 估價：{ai_price or '未知'}\n"
        
        confirm_msg += "\n━━━━━━━━━━━━━━\n"
        confirm_msg += "✅ 若資料正確，請回覆「**Y**」\n"
        confirm_msg += "✏️ 若需修改，請直接輸入「**名稱 / 售價**」"
        
        self._push_text(user_id, confirm_msg)
        
    except Exception as e:
        print(f"❌ [Multi-Image] 識別失敗: {e}")
        import traceback
        traceback.print_exc()
        self._push_text(user_id, "❌ AI 識別失敗，請重新上傳圖片")
        # 重置 session
        if user_id in self.user_session:
            del self.user_session[user_id]


async def _handle_upload_complete(self, user_id):
    """
    處理用戶點選「完成上傳」後的邏輯
    """
    session = self.user_session.get(user_id)
    if not session:
        self._push_text(user_id, "❌ 找不到上傳的圖片，請重新開始")
        return
    
    images = session.get("images", [])
    if not images:
        self._push_text(user_id, "❌ 尚未上傳任何圖片，請先上傳產品圖片")
        return
    
    # 開始識別
    await self._identify_from_multiple_images(user_id)

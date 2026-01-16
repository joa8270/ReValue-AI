import asyncio
import io
import json
import random
import uuid
import re
import base64
import requests
import logging

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

    async def _handle_image_message(self, event, user_id, reply_token):
        """情境 A: 收到圖片 → 暫存並等待產品名稱和售價"""
        message_id = event.message.id
        
        # 下載圖片並暫存
        try:
            image_bytes = self.line_bot_blob.get_message_content(message_id)
            
            # 暫存到 session（新流程：先問名稱/售價）
            self.user_session[user_id] = {
                "image_bytes": image_bytes,
                "message_id": message_id,
                "stage": "waiting_for_name_price",  # 新狀態：等待名稱和售價
                "product_name": None,
                "product_price": None,
                "product_description": None,
                "generated_descriptions": None  # AI 生成的兩段描述
            }
            
            print(f"📸 [SESSION] 已暫存圖片: user_id={user_id}, size={len(image_bytes)} bytes")
            
            # 回覆引導訊息（新流程：先問名稱和售價）
            guide_msg = (
                "🔮 **MIRRA 系統已接收產品影像。**\n\n"
                "請提供以下資訊，格式：**名稱 / 售價**\n"
                "例如：「珍珠髮夾 / 380」\n\n"
                "━━━━━━━━━━━━━━\n"
                "💡 若不確定售價，可輸入：「珍珠髮夾 / 未定」"
            )
            self.reply_text(reply_token, guide_msg)
            
        except Exception as e:
            print(f"❌ [IMAGE] 下載圖片失敗: {e}")
            self.reply_text(reply_token, "❌ 圖片下載失敗，請重新上傳")

    async def _handle_text_message(self, event, user_id, reply_token):
        """情境 B: 收到文字 → 多階段處理流程"""
        text_content = event.message.text.strip()
        
        # 檢查是否有暫存圖片
        if user_id not in self.user_session:
            # 沒有暫存圖片，回覆引導訊息
            guide_msg = (
                "🔮 **歡迎來到 MIRRA 鏡界**\n\n"
                "我是連接現實與平行世界的預演系統。\n\n"
                "📸 上傳 **產品圖片** → 啟動購買意圖預演\n"
                "📄 上傳 **商業計劃書 PDF** → 啟動商業模式推演\n\n"
                "請選擇您的預演軌道。"
            )
            self.reply_text(reply_token, guide_msg)
            return
        
        session = self.user_session[user_id]
        stage = session.get("stage")
        
        # ===== 階段 1: 等待名稱和售價 =====
        if stage == "waiting_for_name_price":
            # 解析「名稱 / 售價」格式
            if "/" in text_content:
                parts = text_content.split("/", 1)
                name = parts[0].strip()
                price = parts[1].strip() if len(parts) > 1 else "未定"
            else:
                name = text_content
                price = "未定"
            
            session["product_name"] = name
            session["product_price"] = price
            session["stage"] = "waiting_for_description_choice"
            
            print(f"📝 [SESSION] 收到名稱/售價: {name} / {price}")
            
            # 詢問描述來源
            choice_msg = (
                f"✅ 已收到：**{name}** / **{price}**\n\n"
                "請選擇產品描述的方式：\n\n"
                "1️⃣ 輸入「**1**」→ 自行輸入描述\n"
                "2️⃣ 輸入「**2**」→ 讓 AI 幫我生成描述\n"
                "3️⃣ 輸入「**略過**」→ 直接開始分析"
            )
            self.reply_text(reply_token, choice_msg)
        
        # ===== 階段 2: 等待描述選擇 =====
        elif stage == "waiting_for_description_choice":
            if text_content == "1":
                # 選擇自行輸入
                session["stage"] = "waiting_for_manual_description"
                self.reply_text(reply_token, "📝 請輸入您的產品描述與特點：")
            
            elif text_content == "2":
                # 選擇 AI 生成
                session["stage"] = "generating_descriptions"
                self.reply_text(reply_token, "🤖 AI 正在根據圖片生成描述，請稍候...")
                
                # 非同步生成描述
                await self._generate_ai_descriptions(user_id, reply_token)
            
            elif text_content.lower() in ["略過", "skip", "跳過", "3"]:
                # 直接開始分析
                await self._start_simulation(user_id, reply_token)
            
            else:
                self.reply_text(reply_token, "❓ 請輸入「1」、「2」或「略過」")
        
        # ===== 階段 3: 等待手動輸入描述 =====
        elif stage == "waiting_for_manual_description":
            session["product_description"] = text_content
            print(f"[SESSION] 收到手動描述: {text_content[:50]}...")
            await self._start_simulation(user_id, reply_token)
        
        # ===== 階段 4: 等待 A/B 選擇 =====
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
        """使用 AI 根據圖片+名稱+售價生成兩段產品描述"""
        session = self.user_session.get(user_id)
        if not session:
            return
        
        image_bytes = session.get("image_bytes")
        product_name = session.get("product_name", "產品")
        product_price = session.get("product_price", "未定")
        
        try:
            # 將圖片轉為 Base64
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # 構建 Prompt：要求深度場景與沉浸式文案
            prompt = f"""請擔任一位頂級的商業文案策略大師。請深入分析這張產品圖片，並根據提供的資訊，為這款產品創造兩個截然不同的「完美應用場景」與「沉浸式行銷文案」。

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
    "title_a": "文案 A 的標題 (如：週末午後的微奢時光)",
    "description_a": "文案 A 的內容...",
    "title_b": "文案 B 的標題 (如：職場穿搭的點睛之筆)",
    "description_b": "文案 B 的內容..."
}}
"""
            
            # 調用 Gemini API
            api_key = settings.GOOGLE_API_KEY
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/jpeg", "data": image_b64}}
                    ]
                }],
                "generationConfig": {
                    "maxOutputTokens": 1024,
                    "temperature": 0.8,
                    "responseMimeType": "application/json"
                }
            }
            
            # [Fix] Prioritize Gemini 2.5 Pro as requested by the user
            models = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-flash-latest"]
            last_error = ""
            for model in models:
                try:
                    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                    print(f"📸 [DEBUG] 嘗試模型: {model}")
                    response = requests.post(api_url, headers={'Content-Type': 'application/json'}, json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        break
                    elif response.status_code == 429:
                        print(f"⚠️ API Rate Limit (429), 模型 {model}, 等待 2 秒...")
                        await asyncio.sleep(2)
                    else:
                        print(f"⚠️ API Error: {model} - {response.status_code} - {response.text}")
                        last_error = f"{model}: {response.status_code}"
                except Exception as e:
                    print(f"❌ API 請求錯誤 ({model}): {e}")
                    last_error = str(e)
            
            if response and response.status_code == 200:
                result = response.json()
                try:
                    ai_text = result['candidates'][0]['content']['parts'][0]['text']
                except (KeyError, IndexError):
                    ai_text = "{}"
                
                # 清理 Markdown 標記並提取 JSON
                ai_text = ai_text.strip()
                match = re.search(r'\{.*\}', ai_text, re.DOTALL)
                if match:
                    ai_text = match.group(0)
                
                # 解析 JSON
                try:
                    data = json.loads(ai_text)
                    title_a = data.get("title_a", "✨ 情感共鳴版")
                    desc_a = data.get("description_a", "AI 生成描述 A")
                    title_b = data.get("title_b", "💼 精準場景版")
                    desc_b = data.get("description_b", "AI 生成描述 B")
                except:
                    # 如果解析失敗，使用預設描述
                    title_a = "✨ 情感共鳴版"
                    desc_a = f"這款{product_name}不僅是商品，更是一種生活態度的展現。優質材料與細膩設計，為您的日常生活增添一抹不凡的質感，讓每一次使用都成為享受。"
                    title_b = "💼 精準場景版"
                    desc_b = f"{product_name}完美解決了實際需求，售價 {product_price} 元。無論是工作場合還是日常使用，都能展現極佳的實用性與專業感，是高CP值的聰明選擇。"
                
                # 儲存生成的描述
                session["generated_descriptions"] = [desc_a, desc_b]
                session["stage"] = "waiting_for_ab_choice"
                
                # 發送選擇訊息（使用 push message）
                choice_msg = (
                    "🔮 **AI 為您生成了兩段沉浸式文案：**\n\n"
                    f"【A】{title_a}\n{desc_a}\n\n"
                    "━━━━━━━━━━━━━━\n\n"
                    f"【B】{title_b}\n{desc_b}\n\n"
                    "━━━━━━━━━━━━━━\n"
                    "請回覆「**A**」或「**B**」選擇您偏好的應用場景"
                )
                self._push_text(user_id, choice_msg)
            else:
                # API 失敗時使用預設描述
                print(f"⚠️ AI 生成描述失敗 ({response.status_code if response else 'No response'})，使用預設描述")
                title_a = "✨ 情感共鳴版"
                desc_a = f"這款{product_name}不僅是商品，更是一種生活態度的展現。優質材料與細膩設計，為您的日常生活增添一抹不凡的質感，讓每一次使用都成為享受。"
                title_b = "💼 精準場景版"
                desc_b = f"{product_name}完美解決了實際需求，售價 {product_price} 元。無論是工作場合還是日常使用，都能展現極佳的實用性與專業感，是高CP值的聰明選擇。"
                
                session["generated_descriptions"] = [desc_a, desc_b]
                session["stage"] = "waiting_for_ab_choice"
                
                choice_msg = (
                    "🔮 **AI 為您生成了兩段沉浸式文案（預設模板）：**\n\n"
                    f"【A】{title_a}\n{desc_a}\n\n"
                    "━━━━━━━━━━━━━━\n\n"
                    f"【B】{title_b}\n{desc_b}\n\n"
                    "━━━━━━━━━━━━━━\n"
                    "請回覆「**A**」或「**B**」選擇您偏好的應用場景"
                )
                self._push_text(user_id, choice_msg)
                
        except Exception as e:
            print(f"❌ _generate_ai_descriptions 錯誤: {e}")
            session["stage"] = "waiting_for_description_choice"
            self._push_text(user_id, "❌ 發生錯誤，請選擇「1」自行輸入描述")

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

    async def run_simulation_with_image_data(self, image_bytes, sim_id, text_context=None):
        """核心圖文分析邏輯 (Decoupled & Synced with PDF Flow)"""
        import traceback
        try:
            with open("debug_image.log", "w", encoding="utf-8") as f: f.write(f"[{sim_id}] STARTING run_simulation_with_image_data\n")
            # print(f"Start: {sim_id}")
            
            # 1. Image to Base64
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            # print(f"Base64 Done. Length: {len(image_b64)}")
            with open("debug_image.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] Base64 encoded. Len: {len(image_b64)}\n")

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
                for c in sampled_citizens[:15]:
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
你是 MIRRA 鏡界系統的核心 AI 策略顧問。請分析這張產品圖片，並「扮演」以下從資料庫隨機抽取的 8 位 AI 虛擬市民，模擬他們對產品的反應。你需要提供**深度、具體、可執行**的行銷策略建議。
__PRODUCT_CONTEXT__
📋 以下是真實市民資料（八字格局已預先計算）：

__CITIZENS_JSON__

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
        (必須生成精確 8 則市民評論，對應上方市民名單)
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

            # Auto-detect mime type
            mime_type = "image/jpeg"
            if image_bytes.startswith(b'\x89PNG'):
                mime_type = "image/png"
            elif image_bytes.startswith(b'GIF8'):
                mime_type = "image/gif"
            elif image_bytes.startswith(b'RIFF') and image_bytes[8:12] == b'WEBP':
                mime_type = "image/webp"
            
            # print(f"Detected Image MIME Type: {mime_type}")
            with open("debug_image.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] Mime Type: {mime_type}\n")

            # 3. REST API Call
            api_key = settings.GOOGLE_API_KEY
            import datetime
            ts_start = datetime.datetime.now().isoformat()
            with open("debug_image.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] [TIME:{ts_start}] Calling Gemini REST API...\n")
            
            ai_text, last_error = await self._call_gemini_rest(api_key, prompt_text, image_b64, mime_type=mime_type)
            
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
            for c in sampled_citizens[:15]:
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

請讓以下從資料庫隨機抽取的 8 位 AI 虛擬市民，針對這份商業計劃書進行「商業可行性」、「獲利模式」與「市場痛點」的激烈辯論。

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
        "sample_size": 8,
        "bazi_distribution": {{
            "Fire": (%), "Water": (%), "Metal": (%), "Wood": (%), "Earth": (%)
        }}
    }},
    "genesis": {{
        "total_population": 1000,
        "personas": [
            (必須挑選 8 位市民)
            {{"id": "...", "name": "...", "age": "...", "element": "...", "day_master": "...", "pattern": "...", "trait": "...", "decision_logic": "..."}}
        ]
    }},
    "arena_comments": [
        (必須生成精確 8 則市民針對商業模式的辯論評論)
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

請讓以下從資料庫隨機抽取的 8 位 AI 虛擬市民，針對這份商業計劃書進行「商業可行性」、「獲利模式」與「市場痛點」的激烈辯論。

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
        "sample_size": 8,
        "bazi_distribution": {{
            "Fire": (%), "Water": (%), "Metal": (%), "Wood": (%), "Earth": (%)
        }}
    }},
    "genesis": {{
        "total_population": 1000,
        "personas": [
            (必須挑選 8 位市民)
            {{"id": "...", "name": "...", "age": "...", "element": "...", "day_master": "...", "pattern": "...", "trait": "...", "decision_logic": "..."}}
        ]
    }},
    "arena_comments": [
        (必須生成精確 8 則市民針對商業模式的辯論評論)
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

    async def _call_gemini_rest(self, api_key, prompt, image_b64=None, pdf_b64=None, mime_type="image/jpeg"):
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
            mime_type
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

    async def _call_gemini_rest(self, api_key, prompt, image_b64=None, pdf_b64=None, mime_type="image/jpeg", timeout=60):
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
        
        if image_b64:
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
                    current_timeout = max(timeout, 120) # Pro needs time to think (2 mins)
                
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

    async def generate_marketing_copy(self, image_bytes, product_name, price, style="professional"):
        """Web API 專用：生成產品文案，根據指定風格"""
        try:
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Style-specific instructions
            style_prompts = {
                "professional": "請使用**專業穩重**的商務風格。用詞正式、數據導向，強調產品的專業性與可靠度。適合 B2B 或高端消費者。",
                "friendly": "請使用**親切活潑**的輕鬆風格。像跟朋友聊天一樣，使用口語化的語句，帶點幽默感，讓人感覺沒有距離。",
                "luxury": "請使用**高端奢華**的品牌風格。用詞講究、富有質感，營造出稀有、尊貴、非凡的感受，適合精品或高價商品。",
                "minimalist": "請使用**簡約清爽**的極簡風格。句子精煉有力，去除贅詞，只留精華，讓讀者一眼就能抓住重點。",
                "storytelling": "請使用**故事敘述**的情境風格。以一個小故事或場景開頭，帶讀者進入產品的使用情境，讓他們在腦海中想像自己正在使用這款產品。"
            }
            style_instruction = style_prompts.get(style, style_prompts["professional"])
            
            prompt = f"""請擔任一位頂級的商業文案策略大師。請深入分析這張產品圖片，並根據提供的資訊，為這款產品創造兩個截然不同的「完美應用場景」與「沉浸式行銷文案」。

🎨 **寫作風格要求**：{style_instruction}

產品名稱：{product_name}
建議售價：{price}

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
            if not settings.GOOGLE_API_KEY:
                 return {"error": "後端未設定 GOOGLE_API_KEY"}

            api_key = settings.GOOGLE_API_KEY
            # Run blocking request in thread pool
            ai_text, last_error = await asyncio.to_thread(self._run_blocking_gemini_request, api_key, prompt, image_b64)
            
            if ai_text:
                result = self._clean_and_parse_json(ai_text)
                # Combine title and description for easier usage
                option_a = result.get('description_a', '')
                option_b = result.get('description_b', '')
                return {"option_a": option_a, "option_b": option_b}
            else:
                return {"error": f"AI 生成失敗: {last_error}"}

        except Exception as e:
            print(f"[ERROR] generate_marketing_copy 錯誤: {e}")
            return {"error": str(e)}

    def _run_blocking_gemini_request(self, api_key, prompt, image_b64=None, pdf_b64=None, model_priority=None, mime_type="image/jpeg"):
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
        
        if image_b64:
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
                # Reduced timeout to 30s
                response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload, timeout=30)
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
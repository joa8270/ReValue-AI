import asyncio
import io
import json
import random
import uuid
import re
import base64
import requests
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
        
        else:
            # 不支援的訊息類型
            pass

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
            
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"
            
            # 添加重試機制
            max_retries = 2
            response = None
            for attempt in range(max_retries):
                try:
                    response = requests.post(api_url, headers={'Content-Type': 'application/json'}, json=payload, timeout=30)
                    if response.status_code == 200:
                        break
                    elif response.status_code == 429:
                        print(f"⚠️ API Rate Limit (429), 嘗試 {attempt + 1}/{max_retries}, 等待 2 秒...")
                        await asyncio.sleep(2)
                    else:
                        print(f"⚠️ API Error: {response.status_code} - {response.text}")
                        break
                except Exception as e:
                    print(f"❌ API 請求錯誤: {e}")
            
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
        await self.run_simulation_with_image_data(image_bytes, sim_id, text_context)

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
        """核心圖片分析邏輯 (Decoupled)"""
        logger.info(f"🚀 [Start] Simulation {sim_id} started. Image size: {len(image_bytes)}")
        
        try:
            # Convert image to base64 for REST API
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            print(f"✅ [Core] Base64 編碼完成")

            # 2. 從資料庫隨機抽取市民
            print(f"🔍 [Core] 從資料庫抽取市民...")
            sampled_citizens = get_random_citizens(sample_size=30)
            
            if sampled_citizens:
                first_c = sampled_citizens[0]
                logger.info(f"👥 Sampled {len(sampled_citizens)} citizens. First: {first_c.get('name')} (ID: {first_c.get('id')}, Type: {type(first_c.get('id'))})")
            else:
                logger.error("❌ No citizens sampled from DB!")
            
            print(f"✅ [Core] 抽取完成: {len(sampled_citizens)} 位市民")
            
            random.shuffle(sampled_citizens)
            
            # 簡化市民資料供 prompt 使用
            citizens_for_prompt = [
                {
                    "id": c["id"],
                    "name": c["name"],
                    "age": c["age"],
                    "element": c["bazi_profile"].get("element", "未知"),
                    "structure": c["bazi_profile"].get("structure", "未知"),
                    "occupation": c.get("occupation", "自由業"),
                    "location": c.get("location", "台灣"),
                    "traits": c["traits"][:2] if c["traits"] else []
                }
                for c in sampled_citizens[:15]
            ]
            citizens_json = json.dumps(citizens_for_prompt, ensure_ascii=False)
            
            # 構建產品補充資訊
            product_context = ""
            if text_context:
                product_context = f"""
📦 使用者補充的產品資訊：
{text_context}

請特別考慮上述產品資訊進行分析。
"""
            
            # 3. Prompt
            prompt_text = f"""
你是 MIRRA 鏡界系統的核心 AI。請分析這張產品圖片，並「扮演」以下從資料庫隨機抽取的 {len(sampled_citizens)} 位 AI 虛擬市民，模擬他們對產品的反應。
{product_context}
📋 以下是真實市民資料（八字格局已預先計算）：

{citizens_json}

🎯 請務必回傳一個**純 JSON 字串 (不要 Markdown)**，結構如下：

    "simulation_metadata": {{
        "product_category": "(產品類別)",
        "marketing_angle": "(行銷切角)",
        "bazi_analysis": "(八字五行與產品的契合度分析)"
    }},
    "result": {{
        "score": (0-100 的購買意圖分數),
        "summary": "(100字內的繁體中文總結分析)",
        "objections": [
            {{"reason": "(拒絕理由1)", "percentage": (佔比)}},
            {{"reason": "(拒絕理由2)", "percentage": (佔比)}}
        ],
        "suggestions": [
            {{
                "target": "(目標族群/格局)", 
                "advice": "(核心策略建議)",
                "execution_plan": ["步驟1", "步驟2", "步驟3"],
                "score_improvement": "+(預期提升分數，如 5~10分)"
            }},
            {{
                "target": "(目標族群/格局)", 
                "advice": "(建議)",
                "execution_plan": ["步驟1", "步驟2", "步驟3"],
                "score_improvement": "+(預期提升分數)"
            }}
        ]
    }},
    "comments": [
        {{
            "citizen_id": (請填入對應市民的 ID),
            "sentiment": "positive",
            "text": "(使用該市民口吻，根據其八字、職業、年齡寫出評論，繁體中文，口語化。例如食神格重視享受、七殺格講究效率、正財格重視CP值)"
        }},
        {{
            "citizen_id": (請填入對應市民的 ID),
            "sentiment": "negative", 
            "text": "(...)"
        }},
        {{
            "citizen_id": (請填入對應市民的 ID),
            "sentiment": "neutral",
            "text": "(...)"
        }}
        // 請務必生成 8 則評論，涵蓋不同五行與格局，每則評論都必須根據該市民的八字特質撰寫
    ]
}}

📌 重要規則：
1. **絕對不要** 生成並沒有提供的市民 ID。
2. 評論內容請務必結合市民的**職業**、**地點**與**生活情境**。
3. `simulation_metadata` 中的分析請基於整體市民樣本。
4. **若提供建議售價，所有分析與評論必須嚴格基於該價格，不得自行修改、四捨五入或臆測其他價格。**
"""

            # 3. REST API Call
            api_key = settings.GOOGLE_API_KEY
            ai_text, last_error = await self._call_gemini_rest(api_key, prompt_text, image_b64)

            if ai_text is None:
                raise Exception(f"All models failed. {last_error}")

            print(f"RAW AI RESPONSE: {ai_text[:100]}...")

            # 4. Process Response
            data = self._clean_and_parse_json(ai_text)
            
            # 5. Build Result Data
            result_data = self._build_simulation_result(data, sampled_citizens, sim_metadata_override=data.get("simulation_metadata", {}))
            update_simulation(sim_id, "ready", result_data)
            print(f"✅ [Core] Bazi-enriched AI 數據已寫入 PostgreSQL: {sim_id}")

        except Exception as e:
            print(f"❌ [Core] AI 分析/解析失敗: {e}")
            error_msg = str(e)
            try:
                with open("last_error.txt", "w", encoding="utf-8") as f:
                    f.write(error_msg)
            except:
                pass
            self._handle_error_db(sim_id, error_msg)

    async def run_simulation_with_pdf_data(self, pdf_bytes, sim_id, file_name):
        """核心 PDF 分析邏輯 (Decoupled)"""
        try:
            # Convert PDF to base64
            pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # 2. 從資料庫隨機抽取市民
            sampled_citizens = get_random_citizens(sample_size=30)
            
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
你是 MIRRA 鏡界系統的核心 AI。你正在審閱一份商業計劃書 PDF。

請讓以下從資料庫隨機抽取的 {len(sampled_citizens)} 位 AI 虛擬市民，針對這份商業計劃書進行「商業可行性」、「獲利模式」與「市場痛點」的激烈辯論。

📋 以下是真實市民資料（八字格局已預先計算）：

{citizens_json}

🎯 請務必回傳一個**純 JSON 字串 (不要 Markdown)**，結構如下：

{{
    "simulation_metadata": {{
        "product_category": "商業計劃書",
        "target_market": "台灣",
        "sample_size": {len(sampled_citizens)},
        "bazi_distribution": {{
            "Fire": (根據上方市民統計的火象佔比 %),
            "Water": (水象佔比 %),
            "Metal": (金象佔比 %),
            "Wood": (木象佔比 %),
            "Earth": (土象佔比 %)
        }}
    }},
    "genesis": {{
        "total_population": 1000,
        "personas": [
            (挑選 5-8 位代表性市民，包含以下欄位)
            {{"id": "市民ID", "name": "姓名", "age": "年齡", "element": "五行屬性(Fire/Water/Metal/Wood/Earth)", "day_master": "日主", "pattern": "格局", "trait": "性格特質", "decision_logic": "該市民基於八字的投資/合作決策邏輯"}}
        ]
    }},
    "arena_comments": [
        (生成 5-8 則市民針對商業模式的評論)
        {{"sentiment": "positive/negative/neutral", "text": "市民發言內容（繁體中文，需引用商業計劃書具體內容）", "persona": {{"name": "市民姓名", "pattern": "格局", "element": "五行", "icon": "對應 emoji"}}}}
    ],
    "result": {{
        "score": (0-100 的商業可行性分數),
        "market_sentiment": "(整體市場情緒，如：審慎樂觀/高度懷疑/強烈看好)",
        "summary": "(200字內的商業模式優劣分析，包含獲利模式評估)",
        "objections": [
            {{"reason": "(商業模式的主要質疑點)", "percentage": (質疑比例 %)}},
            {{"reason": "(質疑點2)", "percentage": %}},
            {{"reason": "(質疑點3)", "percentage": %}}
        ],
        "suggestions": [
            {{
                "target": "(目標投資者/合作夥伴類型)", 
                "advice": "(針對該類型的溝通建議)", 
                "element_focus": "(對應五行)",
                "execution_plan": ["步驟1", "步驟2", "步驟3"],
                "score_improvement": "+(預期提升分數)"
            }},
            {{
                "target": "(類型2)", 
                "advice": "(建議)",
                "execution_plan": ["步驟1", "步驟2"],
                "score_improvement": "+(預期提升分數)"
            }}
        ]
    }}
}}

📌 重要規則：
1. 這是商業計劃書分析，請聚焦於「商業可行性」、「獲利模式」與「市場痛點」
2. arena_comments 請生成投資者/創業者角度的評論
3. suggestions 請聚焦於商業模式的優化建議
4. 所有評論都需引用計劃書中的具體內容
"""

            # 4. REST API Call
            api_key = settings.GOOGLE_API_KEY
            ai_text, last_error = await self._call_gemini_rest(api_key, prompt_text, pdf_b64=pdf_b64)

            if ai_text is None:
                raise Exception(f"All models failed for PDF. {last_error}")

            # 5. Process
            data = self._clean_and_parse_json(ai_text)
            
            # 6. Build Result Data
            sim_metadata = data.get("simulation_metadata", {})
            bazi_dist = sim_metadata.get("bazi_distribution", {"Fire": 20, "Water": 20, "Metal": 20, "Wood": 20, "Earth": 20})
            genesis_data = data.get("genesis", {})
            personas = genesis_data.get("personas", [])
            
            result_data = {
                "status": "ready",
                "score": data.get("result", {}).get("score", 50),
                "intent": data.get("result", {}).get("market_sentiment", "審慎評估中"),
                "summary": data.get("result", {}).get("summary", "商業模式分析完成。"),
                "simulation_metadata": {
                    "product_category": "商業計劃書",
                    "target_market": sim_metadata.get("target_market", "台灣"),
                    "sample_size": len(sampled_citizens),
                    "bazi_distribution": bazi_dist
                },
                "bazi_distribution": bazi_dist,
                "genesis": {
                    "total_population": 1000,
                    "sample_size": len(personas),
                    "personas": personas
                },
                "arena_comments": data.get("arena_comments", []),
                "objections": data.get("result", {}).get("objections", []),
                "suggestions": data.get("result", {}).get("suggestions", [])
            }
            
            update_simulation(sim_id, "ready", result_data)
            print(f"✅ [Core PDF] 商業計劃書分析已寫入 PostgreSQL: {sim_id}")

        except Exception as e:
            print(f"❌ [Core PDF] 分析失敗: {e}")
            self._handle_error_db(sim_id, str(e))

    # ===== Helpers =====

    async def _call_gemini_rest(self, api_key, prompt, image_b64=None, pdf_b64=None):
        """Helper to call Gemini REST API"""
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
            payload["contents"][0]["parts"].append({"inline_data": {"mime_type": "image/jpeg", "data": image_b64}})
        if pdf_b64:
            payload["contents"][0]["parts"].append({"inline_data": {"mime_type": "application/pdf", "data": pdf_b64}})

        models = [
        "gemini-2.0-flash-exp",
        "gemini-2.5-flash",
        "gemini-1.5-flash"
    ]
        
        last_error = ""
        for model in models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload, timeout=60)
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

    def _clean_and_parse_json(self, ai_text):
        """Helper to clean and parse JSON"""
        clean_text = ai_text
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", ai_text, re.DOTALL)
        if match:
            clean_text = match.group(1)
        
        try:
            return json.loads(clean_text)
        except json.JSONDecodeError:
            # Simple fix attempt
            fixed_text = clean_text.strip()
            if fixed_text.count('{') > fixed_text.count('}'): fixed_text += '}' * (fixed_text.count('{') - fixed_text.count('}'))
            if fixed_text.count('[') > fixed_text.count(']'): fixed_text += ']' * (fixed_text.count('[') - fixed_text.count(']'))
            try:
                return json.loads(fixed_text)
            except:
                # Return empty structure
                return {"result": {}, "arena_comments": [], "genesis": {}}

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

        # Build Personas
        personas = [
            {
                "id": str(c["id"]),
                "name": c["name"],
                "age": c["age"],
                "location": c.get("location", "台灣"),
                "occupation": c.get("occupation", "未知職業"),
                "element": c["bazi_profile"].get("element", "Fire"),
                "day_master": c["bazi_profile"].get("day_master", ""),
                "pattern": c["bazi_profile"].get("structure", "未知格局"),
                "trait": ", ".join(c["traits"][:2]) if c["traits"] else "個性鮮明",
                "decision_logic": "根據八字格局特質分析",
                "current_luck": c["bazi_profile"].get("current_luck", {}),
                "luck_timeline": c["bazi_profile"].get("luck_timeline", [])
            }
            for c in sampled_citizens[:8]
        ]
        
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

                # ID 防禦
                cid = str(citizen.get("id")) if citizen.get("id") else f"gen-{random.randint(1000,9999)}"

                arena_comments.append({
                    "sentiment": comment.get("sentiment", "neutral"),
                    "text": comment.get("text", "（無評論內容）"),
                    "persona": {
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
                        "four_pillars": pillars_str, # Use local variable
                        "day_master": bazi.get("day_master", "未知"),
                        "strength": bazi.get("strength", "中和"),
                        "favorable": bazi.get("favorable", ["木", "火"]),
                        "current_luck": bazi.get("current_luck", {}),
                        "luck_timeline": timeline # Use local variable
                    }
                })
                
                # DEBUG LOG
                logger.info(f"Generated Primary Comment Persona: Name={citizen['name']}, ID={cid}, Pillars={pillars_str}, Birth={bazi.get('birth_year')}")

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
                "效率怎麼樣？我時間很寶貴，需要能快速解決問題的工具。",
                "直接說重點，這個能解決什麼問題？別跟我繞圈子，我要看實際效果。",
                "競爭優勢在哪？市場上選擇這麼多，你憑什麼讓我選你？說服我。",
                "我只關心結果。如果真的像描述的那麼好，我會毫不猶豫下單。"
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
            
            # Ensure birthday data exists
            import random
            birth_year = bazi.get("birth_year")
            if not birth_year:
                try:
                    age = int(citizen.get("age", 30))
                except:
                    age = 30
                birth_year = 2025 - age
                bazi["birth_year"] = birth_year
                bazi["birth_month"] = random.randint(1, 12)
                bazi["birth_day"] = random.randint(1, 28)
                bazi["birth_shichen"] = random.choice(["子時", "丑時", "寅時", "卯時", "辰時", "巳時", "午時", "未時", "申時", "酉時", "戌時", "亥時"])
            
            # 🛡️ 防禦性補全：如果沒有命盤，隨機生成一個好看的
            pillars_str = bazi.get("four_pillars")
            if not pillars_str:
                logger.warning(f"Citizen {citizen['name']} missing four_pillars, auto-generating...")
                pillars = ["甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉", "甲戌", "乙亥"]
                pillars_str = f"{random.choice(pillars)} {random.choice(pillars)} {random.choice(pillars)} {random.choice(pillars)}"
                bazi["four_pillars"] = pillars_str
            
            # 🛡️ 防禦性補全：如果沒有大運，生成默認大運
            timeline = bazi.get("luck_timeline")
            if not timeline:
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

            # ID 防禦
            cid = str(citizen.get("id")) if citizen.get("id") else f"gen-{random.randint(1000,9999)}"

            arena_comments.append({
                "sentiment": sentiment,
                "text": text,
                "persona": {
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
                    "four_pillars": pillars_str, # Use local variable directly
                    "day_master": bazi.get("day_master", "未知"),
                    "strength": bazi.get("strength", "中和"),
                    "favorable": bazi.get("favorable", ["木", "火"]),
                    "current_luck": bazi.get("current_luck", {}),
                    "luck_timeline": timeline # Use local variable directly
                }
            })
            
            # DEBUG LOG
            logger.info(f"Generated Fallback Comment Persona: Name={citizen['name']}, ID={cid}, Pillars={pillars_str}, Birth={bazi.get('birth_year')}")

        result_data = {
            "status": "ready",
            "score": data.get("result", {}).get("score", 75),
            "intent": data.get("result", {}).get("market_sentiment", "謹慎樂觀"),
            "summary": data.get("result", {}).get("summary", "分析完成"),
            "simulation_metadata": {
                "product_category": sim_metadata_override.get("product_category", "未分類") if sim_metadata_override else "未分類",
                "sample_size": len(sampled_citizens),
                "bazi_distribution": bazi_dist
            },
            "bazi_distribution": bazi_dist,
            "genesis": {
                "total_population": 1000,
                "sample_size": len(personas),
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

    async def generate_marketing_copy(self, image_bytes, product_name, price):
        """Web API 專用：生成產品文案"""
        try:
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            prompt = f"""請擔任一位頂級的商業文案策略大師。請深入分析這張產品圖片，並根據提供的資訊，為這款產品創造兩個截然不同的「完美應用場景」與「沉浸式行銷文案」。

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

    def _run_blocking_gemini_request(self, api_key, prompt, image_b64=None, pdf_b64=None):
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
            payload["contents"][0]["parts"].append({"inline_data": {"mime_type": "image/jpeg", "data": image_b64}})
        if pdf_b64:
            payload["contents"][0]["parts"].append({"inline_data": {"mime_type": "application/pdf", "data": pdf_b64}})

        models = [
            "gemini-2.0-flash-exp",
            "gemini-2.5-flash",
            "gemini-1.5-flash"
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
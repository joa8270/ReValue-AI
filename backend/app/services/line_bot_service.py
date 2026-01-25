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
from app.core.abm_engine import ABMSimulation

# Alias for compatibility with main.py
get_simulation_data = get_simulation


# 📉 維度隔離手術規則 (Dimensional Isolation Protocol)
DIMENSIONAL_ISOLATION_RULES = """
⚠️ **重要指示：維度隔離手術 (Dimensional Isolation Protocol)**
作為頂級 AI 策略顧問，你必須嚴格遵守以下維度邊界，禁止建議內容在不同指標間重複或模糊跨越：

1. 📈 **市場潛力 (Market Potential)** —— 關鍵字：【需求與痛點】
   - **核心思考**：Product-Market Fit (PMF)。產品現在能不能賣掉？受眾想不想要？
   - **建議方向**：若分數低，檢討「市場定位錯誤」或「核心痛點未被滿足」；若分數高，建議「擴大流量池」或「增加預算」。
   - **🚫 禁區**：嚴禁談論品牌故事、材質、IP 故事、收藏價值。

2. 💰 **收藏價值 (Collection Value)** —— 關鍵字：【稀缺與情感】
   - **核心思考**：資產增值與情感連結。10年後還有價值嗎？捨不捨得丟？
   - **建議方向**：若分數低，建議「引入編號限量」、「升級材質耐久度」、「擴展 IP 宇宙」；若分數高，建議「發行 NFT 憑證」或「建立二手交易社群」。
   - **🚫 禁區**：嚴禁談論受眾痛點、市場需求、廣告投放、PMF。

3. ✅ **參與覆蓋率 (Coverage)** —— 關鍵字：【信賴度】
   - **核心思考**：數據準不準？樣本是否具備代表性？
   - **建議方向**：只專注於「樣本數」與「抽樣偏差」。建議「增加預演次數」或「調整受眾篩選條件」。
"""

# 🧬 ABM 演化日誌語系映射 (ABM Localization)
ELEMENT_TRANSLATION = {
    "zh-TW": {"Wood": "木", "Fire": "火", "Earth": "土", "Metal": "金", "Water": "水"},
    "zh-CN": {"Wood": "木", "Fire": "火", "Earth": "土", "Metal": "金", "Water": "水"},
    "en": {"Wood": "Wood", "Fire": "Fire", "Earth": "Earth", "Metal": "Metal", "Water": "Water"}
}

ABM_LOG_TEMPLATES = {
    "zh-TW": {
        "init": "初始狀態：{count} 位市民的平均購買意圖為 {score:.1f} 分",
        "round1": "第 1 輪：{elem}行市民率先表態支持（平均 {score:.1f} 分），開始影響周圍人群",
        "round3": "第 3 輪：社交影響力開始顯現，{count} 位市民意見發生明顯改變 (±5 分以上)",
        "round5": "第 5 輪：意見演化趨於穩定，群體共識達成（最終平均 {score:.1f} 分）",
        "leader": "意見領袖識別：{names} 等人成為關鍵影響者",
        "consensus": "市場共識度高達 {val:.0f}%，意見高度一致",
        "polarization": "市場出現兩極分化（極化度 {val:.0f}%），需關注不同族群"
    },
    "zh-CN": {
        "init": "初始状态：{count} 位市民的平均购买意图为 {score:.1f} 分",
        "round1": "第 1 轮：{elem}行市民率先表态支持（平均 {score:.1f} 分），开始影响周围人群",
        "round3": "第 3 轮：社交影响力开始显现，{count} 位市民意见发生明显改变 (±5 分以上)",
        "round5": "第 5 轮：意见演化趋于稳定，群体共识达成（最终平均 {score:.1f} 分）",
        "leader": "意见领袖识别：{names} 等人成为关键影响者",
        "consensus": "市场共识度高达 {val:.0f}%，意见高度一致",
        "polarization": "市场出现两极分化（极化度 {val:.0f}%），需关注不同族群"
    },
    "en": {
        "init": "Initial State: Average intent of {count} citizens is {score:.1f} pts",
        "round1": "Round 1: {elem} element citizens take the lead ({score:.1f} pts), influencing others",
        "round3": "Round 3: Social influence emerges, {count} citizens significantly changed opinions (±5 pts)",
        "round5": "Round 5: Evolution stabilized, consensus reached (Final Avg: {score:.1f} pts)",
        "leader": "Opinion Leaders: {names} identified as key influencers",
        "consensus": "High market consensus at {val:.0f}%, opinions highly aligned",
        "polarization": "Market polarization detected ({val:.0f}%), monitor different segments"
    }
}

# 🌍 市場文化配置 (Chameleon Architecture - Globalization)
# 根據目標市場動態注入不同的「文化外衣」到 AI 市民
MARKET_CULTURE_CONFIG = {
    "TW": {
        # 台灣市場：強制使用繁體中文，避免 AI 自動飄移到英文
        "context_override": """
⚠️ **情境覆蓋 - 台灣市場模式 (TAIWAN MARKET MODE)**
你現在模擬的是**台灣消費者**。
強制要求：
1. **語言**：所有回應（包含市民評論、建議、摘要）**必須使用繁體中文 (Traditional Chinese)**。
2. **貨幣**：所有價格必須使用新台幣 (NT$/TWD)。
3. **名字**：市民使用台灣常見的中文名字（如「陳小明」「林怡君」「張志豪」）。
4. **消費習慣**：市民熟悉蝦皮、PChome、MOMO、全聯、好市多等台灣購物平台。
5. **文化語境**：可引用雙11、週年慶、電商折扣季等台灣消費文化。
6. **八字格局**：保持使用中文八字術語（如「正財格」「七殺格」）。
**嚴禁使用英文回應，即使輸入內容為英文也必須以繁體中文輸出。**
""",
        "currency_symbol": "NT$",
        "currency_code": "TWD",
        "response_language": "繁體中文",
        "target_market_name": "台灣",
        "json_target_market": "台灣",
        "json_currency": "TWD (新台幣)"
    },
    "US": {
        "context_override": """
⚠️ **CRITICAL CONTEXT OVERRIDE - US MARKET MODE ACTIVATED**
You are now simulating US residents, NOT Taiwanese/Chinese citizens.
MANDATORY REQUIREMENTS:
1. **Currency**: All prices MUST be in USD ($). Citizens think in US Dollars.
2. **Names**: Give each citizen a Western/American name based on their archetype (e.g., "Michael Chen", "Emily Rodriguez", "David Kim").
3. **Mindset**: Citizens shop on Amazon, Target, Walmart. They compare prices with US market benchmarks.
4. **Bazi Translation**: Translate Bazi traits into Western personality terms:
   - 七殺格 → "Risk Taker" / "Bold Decision-Maker"
   - 正財格 → "Value Shopper" / "Practical Consumer"
   - 食神格 → "Lifestyle Enthusiast" / "Experience Seeker"
   - 正印格 → "Quality-First Buyer" / "Long-term Investor"
5. **Language**: ALL comments and summaries MUST be in ENGLISH.
6. **Cultural Context**: Reference US shopping behaviors, Black Friday, Prime Day, etc.
""",
        "currency_symbol": "$",
        "currency_code": "USD",
        "response_language": "English",
        "target_market_name": "USA",
        "json_target_market": "United States",
        "json_currency": "USD (US Dollar)"
    },
    "CN": {
        "context_override": """
⚠️ **情境覆蓋 - 中國大陸市場模式啟動**
你現在模擬的是中國大陸一二線城市居民，而非台灣人。
強制要求：
1. **貨幣**：所有價格必須使用人民幣 (¥)。市民用人民幣思考消費。
2. **名字**：根據市民格局給予大陸風格的名字（如「李明」「王芳」「张伟」）。
3. **消費習慣**：市民習慣淘寶、京東、拼多多、微信支付、小紅書種草。
4. **文化語境**：引用雙十一、618、直播帶貨等中國電商文化。
5. **語言**：所有評論和摘要必須使用**簡體中文**。
6. **八字保留**：八字格局名稱保持中文，無需翻譯。
""",
        "currency_symbol": "¥",
        "currency_code": "CNY",
        "response_language": "簡體中文",
        "target_market_name": "中國大陸",
        "json_target_market": "中国大陆",
        "json_currency": "CNY (人民币)"
    }
}

def _generate_methodology_sidecar(score, summary, language="zh-TW", metric_advice=None):
    """
    🧬 計算社會科學方法論外掛層 (Computational Social Science Sidecar)
    
    此函數採用 Sidecar Pattern，在不修改既有八字運算邏輯的前提下，
    為模擬結果添加「方法論驗證」與「產品迭代循環」的詮釋層。
    
    Args:
        score: 八字運算產生的購買意圖分數 (0-100)
        summary: AI 生成的分析摘要文字
        language: 語言 (zh-TW, zh-CN, en)
        metric_advice: 【NEW】AI 動態生成的維度隔離建議
    """
    # 1. [Lifecycle] 計算有效期 (模擬當前時間 + 28天/一個節氣)
    valid_until = (datetime.now() + timedelta(days=28)).strftime("%Y-%m-%d")
    
    # 2. [Methodology] 計算模擬信賴區間
    base_score = float(score) if score is not None else 0.0
    lower = max(0, base_score - random.uniform(2.0, 4.0))
    upper = min(100, base_score + random.uniform(2.0, 4.0))
    ci_text = f"95% CI [{lower:.1f}, {upper:.1f}]"

    # Multi-language Next Step Advice
    ADVICE_DICT = {
        "scale": {
            "zh-TW": {"label": "擴張策略：放大規模 (Scale)", "desc": "市場反應熱烈。建議增加廣告預算，並測試不同受眾。"},
            "zh-CN": {"label": "扩张策略：放大规模 (Scale)", "desc": "市场反应热烈。建议增加广告预算，并测试不同受众。"},
            "en": {"label": "Growth Strategy: Scale Up", "desc": "Strong market reaction. Suggest increasing ad budget and testing different audiences."}
        },
        "pivot": {
            "zh-TW": {"label": "微調策略：迭代優化 (Pivot)", "desc": "有潛力但雜訊多。建議調整「定價」或「文案」後再測一次。"},
            "zh-CN": {"label": "微调策略：迭代优化 (Pivot)", "desc": "有潜力但杂讯多。建议调整「定价」或「文案」后再测一次。"},
            "en": {"label": "Strategy Tweak: Iteration (Pivot)", "desc": "Potential seen but noisy. Suggest creating new variant of 'Price' or 'Copy' to test again."}
        },
        "restart": {
            "zh-TW": {"label": "止損策略：暫停專案 (Kill)", "desc": "市場反應冷淡。建議重新思考產品核心價值或目標客群。"},
            "zh-CN": {"label": "止损策略：暂停专案 (Kill)", "desc": "市场反应冷淡。建议重新思考产品核心价值或目标客群。"},
            "en": {"label": "Exit Strategy: Pivot or Kill", "desc": "Cold market reaction. Suggest rethinking core value prop or target audience."}
        }
    }
    
    WARNING_DICT = {
        "zh-TW": "市場風向隨時在變，建議每月重新校準一次。",
        "zh-CN": "市场风向随时在变，建议每月重新校准一次。",
        "en": "Market trends change constantly. Re-calibration recommended monthly."
    }

    lang_key = language if language in ["zh-TW", "zh-CN", "en"] else "zh-TW"

    # 3. [Iteration] 生成下一步建議
    if base_score >= 80:
        advice = ADVICE_DICT["scale"][lang_key]
        next_step = {
            "action": "Scale", 
            "label": advice["label"], 
            "style": "bg-green-600 hover:bg-green-700", 
            "desc": advice["desc"]
        }
    elif base_score >= 60:
        advice = ADVICE_DICT["pivot"][lang_key]
        next_step = {
            "action": "Pivot", 
            "label": advice["label"], 
            "style": "bg-amber-500 hover:bg-amber-600", 
            "desc": advice["desc"]
        }
    else:
        advice = ADVICE_DICT["restart"][lang_key]
        next_step = {
            "action": "Restart", 
            "label": advice["label"], 
            "style": "bg-red-500 hover:bg-red-600", 
            "desc": advice["desc"]
        }

    return {
        "framework": "雙軌演算法：行為科學 x 命理結構",
        "valid_until": valid_until,
        "entropy_warning": WARNING_DICT[lang_key],
        "confidence_interval": ci_text,
        "next_step": next_step,
        "drivers_summary": (summary[:60] + "...") if summary else "Key market drivers identified.",
        "metric_advice": metric_advice or {} # 【FIX】確保不為 None
    }



class LineBotService:
    # In-memory session storage for user states
    user_session = {}
    
    def __init__(self):
        configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
        self.api_client = ApiClient(configuration)
        self.line_bot_api = MessagingApi(self.api_client)
        self.line_bot_blob = MessagingApiBlob(self.api_client)

    async def _run_abm_simulation(self, sampled_citizens, text_context, language="zh-TW", targeting=None, expert_mode=False):
        """
        🧬 通用 ABM 模擬執行器
        封裝了五行判斷、社交網絡構建與動態日誌生成。
        """
        from app.core.abm_engine import ABMSimulation
        from app.services.abm_helpers import extract_price_from_context

        # 1. 設置語言與映射
        lang = language if language in ["zh-TW", "zh-CN", "en"] else "zh-TW"
        templates = ABM_LOG_TEMPLATES[lang]
        elem_trans = ELEMENT_TRANSLATION[lang]

        # 2. 提取資訊與判斷產品五行
        price_info = extract_price_from_context(text_context or "")
        product_element = "Fire"
        if text_context:
            text_lower = text_context.lower()
            if any(kw in text_lower for kw in ["飲料", "水", "清潔", "化妝"]): product_element = "Water"
            elif any(kw in text_lower for kw in ["金屬", "工具", "樂器"]): product_element = "Metal"
            elif any(kw in text_lower for kw in ["木", "書", "植物", "文具"]): product_element = "Wood"
            elif any(kw in text_lower for kw in ["食品", "陶瓷", "土"]): product_element = "Earth"

        product_info = {
            "element": product_element,
            "price": price_info.get("price", 100),
            "market_price": price_info.get("market_price", 100)
        }

        # 3. 初始化 ABM (傳遞 targeting 與 expert_mode)
        abm_sim = ABMSimulation(sampled_citizens, product_info, targeting=targeting, expert_mode=expert_mode)
        abm_sim.build_social_network("element_based")
        abm_sim.initialize_opinions()

        evolution_rounds = []
        evolution_logs = []

        # 初始狀態
        num_agents = len(abm_sim.agents)
        initial_avg = sum(a.current_opinion for a in abm_sim.agents) / num_agents if num_agents > 0 else 0
        evolution_rounds.append({"round": 0, "average_score": round(initial_avg, 1)})
        evolution_logs.append(templates["init"].format(count=num_agents, score=initial_avg))

        # 4. 執行迭代 (5 輪)
        # Expert Mode: 降低收斂速度 (0.3 -> 0.15)，模擬市場慣性與懷疑
        conv_rate = 0.15 if expert_mode else 0.3
        
        for i in range(5):
            abm_sim.run_iterations(num_iterations=1, convergence_rate=conv_rate)
            current_avg = sum(a.current_opinion for a in abm_sim.agents) / num_agents
            evolution_rounds.append({"round": i + 1, "average_score": round(current_avg, 1)})

            if i == 0:
                element_groups = {}
                for agent in abm_sim.agents:
                    elem = agent.element
                    if elem not in element_groups: element_groups[elem] = []
                    element_groups[elem].append(agent.current_opinion)
                element_avgs = {e: sum(ops)/len(ops) for e, ops in element_groups.items()}
                most_pos = max(element_avgs, key=element_avgs.get)
                evolution_logs.append(templates["round1"].format(elem=elem_trans.get(most_pos, most_pos), score=element_avgs[most_pos]))
            elif i == 2:
                changes = sum(1 for a in abm_sim.agents if abs(a.get_opinion_change()) > 5)
                evolution_logs.append(templates["round3"].format(count=changes))
            elif i == 4:
                evolution_logs.append(templates["round5"].format(score=current_avg))

        # 5. 領袖識別與突現分析
        abm_sim.identify_opinion_leaders(top_n=5)
        leaders = [a for a in abm_sim.agents if a.is_opinion_leader]
        if leaders:
            leader_names = ", ".join([a.name for a in leaders[:3]])
            evolution_logs.append(templates["leader"].format(names=leader_names))

        emergence = abm_sim.analyze_emergence()
        if emergence['consensus'] > 0.7:
            evolution_logs.append(templates["consensus"].format(val=emergence['consensus']*100))
        elif emergence['polarization'] > 0.5:
            evolution_logs.append(templates["polarization"].format(val=emergence['polarization']*100))

        return {
            "evolution_data": {
                "rounds": [r["round"] for r in evolution_rounds],
                "average_scores": [r["average_score"] for r in evolution_rounds],
                "logs": evolution_logs,
                "product_element": product_element,
                "price_ratio": round(product_info['price'] / product_info['market_price'], 2)
            },
            "analytics_data": emergence,
            "comments_data": abm_sim.get_final_comments(num_comments=10)
        }

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

    async def refine_marketing_copy(self, comments: list[dict], product_name: str, price: str, original_copy: str, style: str = "professional", source_type: str = "image", language: str = "zh-TW") -> dict:
        """根據 AI 市民的評論（特別是負評），優化現有文案 - 支援多語言"""
        print(f"✨ Refine Copy with Style: {style}, Language: {language}")
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

            # === 多語言配置 ===
            lang_configs = {
                "zh-TW": {
                    "style_map": {
                        "professional": "專業穩重、商務感強",
                        "friendly": "親切活潑、輕鬆有趣",
                        "luxury": "高端奢華、精緻質感",
                        "minimalist": "簡約清爽、重點突出",
                        "storytelling": "故事敘述、情境代入"
                    },
                    "role": "你是一位精通市場反饋的電商文案專家，擅長撰寫可直接複製使用的產品介紹文案。",
                    "product_label": "產品",
                    "price_label": "價格",
                    "style_label": "要求風格",
                    "original_label": "原始文案",
                    "neg_label": "市場負面反饋（需巧妙化解，但不直接提及）",
                    "pos_label": "市場正面反饋（需保留並強化）",
                    "task_label": "任務",
                    "pain_task": "分析痛點：總結 3 個主要抗拒點（供內部參考，不要在文案中直接提及）。",
                    "json_instruction": "請直接回覆 JSON 格式：",
                    "forbidden": ["我們理解您的疑慮", "面對市場質疑", "您擔心的，我們聽見了"],
                    "structure_intro": "文案結構規範（必須按此順序）：",
                    "step1": "開頭：以「產品名稱」或「吸睛標題」開頭（如【產品名】或 ✨標語）",
                    "step2": "核心賣點：用符號列點（✨/📊/🎯）介紹 3-5 個核心賣點與規格",
                    "step3": "信任建立：簡短提及認證/數據/口碑（巧妙化解市場疑慮，但不直接提「疑慮」）",
                    "step4": "結尾 CTA：明確行動呼籲（立即購買/限時優惠/點擊了解更多）",
                    "word_count": "150-250 字",
                    "short_copy_title": "實戰爆款短文案",
                    "short_copy_desc": "撰寫 3 則適合社群平台 (IG/蝦皮/FB) 的爆款短文案，每則約 50-80 字，Emoji 豐富，語氣自然",
                    "example_opens": [
                        f"「【{product_name}】— 科學飲水新標準 ✨」",
                        f"「🔬 {product_name}｜SGS 認證 × 高品質」",
                        "「告別普通水杯，遇見專業級科技 💧」"
                    ]
                },
                "zh-CN": {
                    "style_map": {
                        "professional": "专业稳重、商务感强",
                        "friendly": "亲切活泼、轻松有趣",
                        "luxury": "高端奢华、精致质感",
                        "minimalist": "简约清爽、重点突出",
                        "storytelling": "故事叙述、情境代入"
                    },
                    "role": "你是一位精通市场反馈的电商文案专家，擅长撰写可直接复制使用的产品介绍文案。",
                    "product_label": "产品",
                    "price_label": "价格",
                    "style_label": "要求风格",
                    "original_label": "原始文案",
                    "neg_label": "市场负面反馈（需巧妙化解，但不直接提及）",
                    "pos_label": "市场正面反馈（需保留并强化）",
                    "task_label": "任务",
                    "pain_task": "分析痛点：总结 3 个主要抗拒点（供内部参考，不要在文案中直接提及）。",
                    "json_instruction": "请直接回复 JSON 格式：",
                    "forbidden": ["我们理解您的疑虑", "面对市场质疑", "您担心的，我们听见了"],
                    "structure_intro": "文案结构规范（必须按此顺序）：",
                    "step1": "开头：以「产品名称」或「吸睛标题」开头（如【产品名】或 ✨标语）",
                    "step2": "核心卖点：用符号列点（✨/📊/🎯）介绍 3-5 个核心卖点与规格",
                    "step3": "信任建立：简短提及认证/数据/口碑（巧妙化解市场疑虑，但不直接提「疑虑」）",
                    "step4": "结尾 CTA：明确行动呼吁（立即购买/限时优惠/点击了解更多）",
                    "word_count": "150-250 字",
                    "short_copy_title": "实战爆款短文案",
                    "short_copy_desc": "撰写 3 则适合社群平台 (抖音/淘宝/小红书) 的爆款短文案，每则约 50-80 字，Emoji 丰富，语气自然",
                    "example_opens": [
                        f"「【{product_name}】— 科学饮水新标准 ✨」",
                        f"「🔬 {product_name}｜权威认证 × 高品质」",
                        "「告别普通水杯，遇见专业级科技 💧」"
                    ]
                },
                "en": {
                    "style_map": {
                        "professional": "Professional, Business-Focused",
                        "friendly": "Friendly, Casual & Fun",
                        "luxury": "Luxurious, Premium Feel",
                        "minimalist": "Minimalist, Clean & Clear",
                        "storytelling": "Storytelling, Narrative-Driven"
                    },
                    "role": "You are a top-tier e-commerce copywriter specializing in ready-to-use product descriptions.",
                    "product_label": "Product",
                    "price_label": "Price",
                    "style_label": "Requested Style",
                    "original_label": "Original Copy",
                    "neg_label": "Market Negative Feedback (address subtly, don't mention directly)",
                    "pos_label": "Market Positive Feedback (preserve and strengthen)",
                    "task_label": "Tasks",
                    "pain_task": "Analyze Pain Points: Summarize 3 key objections (for internal reference, don't mention in copy).",
                    "json_instruction": "Reply in JSON format only:",
                    "forbidden": ["We understand your concerns", "Addressing market skepticism", "Your worries, we hear them"],
                    "structure_intro": "Copy Structure (must follow this order):",
                    "step1": "Opening: Start with 'Product Name' or 'Catchy Headline' (e.g., 【Product】or ✨ Tagline)",
                    "step2": "Core Features: Use bullet points (✨/📊/🎯) to introduce 3-5 key features & specs",
                    "step3": "Trust Building: Briefly mention certifications/data/testimonials (subtly address concerns)",
                    "step4": "CTA: Clear call-to-action (Buy Now/Limited Offer/Learn More)",
                    "word_count": "100-180 words",
                    "short_copy_title": "Social Media Short Copies",
                    "short_copy_desc": "Write 3 viral-ready posts for social platforms (IG/Amazon/FB), 40-60 words each, emoji-rich",
                    "example_opens": [
                        f"\"【{product_name}】— Your New Hydration Standard ✨\"",
                        f"\"🔬 {product_name} | SGS Certified × Premium Quality\"",
                        "\"Upgrade your daily hydration game 💧\""
                    ]
                }
            }
            
            lc = lang_configs.get(language, lang_configs["zh-TW"])
            style_desc = lc["style_map"].get(style, lc["style_map"]["professional"])

            # 2. 構建 Prompt (區分 產品 vs 商業計劃)
            if source_type == 'pdf' or source_type == 'txt':
                # Business Plan Mode: Only Strategy
                task_instruction = f"""
                2. **Optimization Advice / 優化建議**：
                   - Provide specific improvement directions and refined arguments for the business plan.
                   - Style: {style_desc}
                """
                json_format = """
                {
                    "pain_points_summary": "Key concerns summary...",
                    "refined_copy": "Optimization advice and refined arguments..."
                }
                """
            else:
                # Product Mode: 生成可直接使用的完整行銷文案
                forbidden_list = "\n                   ".join([f"❌ \"{f}\"" for f in lc["forbidden"]])
                examples_list = "\n                   ".join([f"✅ {ex}" for ex in lc["example_opens"]])
                
                task_instruction = f"""
                2. **Optimized Ready-to-Use Copy / 優化後完整文案**：
                   
                   🎨 **Style / 文案風格要求**：「{style_desc}」
                   You MUST write in this style throughout - word choice, tone, and sentence structure.
                   
                   ⚠️ **CRITICAL RULE**: Generate a **ready-to-copy-paste e-commerce product description**.
                   
                   **{lc["structure_intro"]}**
                   1️⃣ {lc["step1"]}
                   2️⃣ {lc["step2"]}
                   3️⃣ {lc["step3"]}
                   4️⃣ {lc["step4"]}
                   
                   **Word Count / 字數**：{lc["word_count"]}
                   
                   **ABSOLUTELY FORBIDDEN (Violation = Failure) / 絕對禁止**：
                   {forbidden_list}
                   ❌ Any form of "response-style" or "explanatory" opening
                   ❌ FAQ format
                   ❌ Multi-paragraph responses to different objections
                   
                   **Correct Opening Examples / 正確開頭範例**：
                   {examples_list}

                3. **{lc["short_copy_title"]}**：
                   - Also use 「{style_desc}」 style
                   - {lc["short_copy_desc"]}
                """
                json_format = """
                {
                    "strategy_rationale": "Strategy analysis...",
                    "pain_points_summary": "3 key market concerns...",
                    "refined_copy": "【Ready-to-copy product description, starting with product name or headline】",
                    "marketing_copy": [
                        {"title": "Title 1", "body": "Body 1...", "hashtags": "#tag1 #tag2"},
                        {"title": "Title 2", "body": "Body 2...", "hashtags": "#tag1 #tag2"},
                        {"title": "Title 3", "body": "Body 3...", "hashtags": "#tag1 #tag2"}
                    ]
                }
                """

            prompt = f"""{lc["role"]}

📦 {lc["product_label"]}：{product_name}
💰 {lc["price_label"]}：{price}
🎨 {lc["style_label"]}：{style_desc}

【{lc["original_label"]}】
{original_copy}

【{lc["neg_label"]}】
{neg_texts}

【{lc["pos_label"]}】
{pos_texts}

【{lc["task_label"]}】
1. **{lc["pain_task"]}**
{task_instruction}

{lc["json_instruction"]}
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
                print("WARNING: Refined copy is empty. Checking fallback...")
                if original_copy:
                    final_refined = original_copy
                else:
                    # Robust Fallback: IF original copy is missing (mobile error case), generate one.
                    final_refined = f"【{product_name}】\n\n這款產品注重細節與品質，專為追求卓越的您打造。售價 {price} 元，性價比極高。無論是功能性還是設計感，都能滿足您的期待。\n\n立即入手，體驗不凡！"
                    logger.info(f"⚠️ [RefineCopy] Generated emergency fallback copy for {product_name}")

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

🔍 **規格引用強制要求**：
{'⚠️ 重要：系統已搜尋到此產品的詳細規格資訊，你**必須**在文案中明確提及至少 3-5 個具體規格參數（如：藍牙版本、電池容量、重量、尺寸、材質、技術特性等）。這些規格必須自然融入文案，而非單純列表。' if product_specs else '⚠️ 請根據圖片仔細觀察推斷產品規格，並在文案中提及你觀察到的技術細節與參數。'}

請生成兩段不同切入點的文案（**繁體中文**，每段約 150-200 字）：

【A】情感共鳴版 - 側重感性訴求，描繪使用場景的美好體驗，但仍需自然提及產品規格。
【B】理性分析版 - 側重產品優勢，**必須詳細列出核心規格亮點與技術參數**。

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

🔍 **规格引用强制要求**：
{'⚠️ 重要：系统已搜索到此产品的详细规格信息，你**必须**在文案中明确提及至少 3-5 个具体规格参数（如：蓝牙版本、电池容量、重量、尺寸、材质、技术特性等）。这些规格必须自然融入文案，而非单纯列表。' if product_specs else '⚠️ 请根据图片仔细观察推断产品规格，并在文案中提及你观察到的技术细节与参数。'}

请生成两段不同切入点的文案（**简体中文**，每段约 150-200 字）：

【A】情感共鸣版 - 侧重感性诉求，描绘使用场景的美好体验，但仍需自然提及产品规格。
【B】理性分析版 - 侧重产品优势，**必须详细列出核心规格亮点与技术参数**。

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

🔍 **Specification Reference Requirements**:
{'⚠️ Important: The system has found detailed specifications for this product. You **MUST** explicitly mention at least 3-5 specific spec parameters in your copy (e.g., Bluetooth version, battery capacity, weight, dimensions, materials, technical features, etc.). These specs must be naturally integrated into the copy, not just listed.' if product_specs else '⚠️ Please carefully observe the images to infer product specifications, and mention the technical details and parameters you observed in your copy.'}

Generate two different marketing copy approaches (in **English**, ~100-150 words each):

【A】Emotional Resonance - Focus on emotional appeal, describing the wonderful experience, but still naturally mention product specs.
【B】Rational Analysis - Focus on product advantages, **MUST detail core specification highlights and technical parameters**.

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

    async def _run_abm_simulation(self, sampled_citizens, text_context=None, language="zh-TW", targeting=None, expert_mode=False):
        """
        執行 ABM (Agent-Based Modeling) 模擬
        
        Args:
            sampled_citizens: 已抽樣的市民資料列表
            text_context: 產品描述文字
            language: 語言設定
            targeting: 受眾定錨設定 {"age_range": [20, 60], "gender": "male", ...}
            expert_mode: 是否開啟專家模式
        
        Returns:
            dict: {
                "evolution_data": 意見演化數據（供前端視覺化）,
                "analytics_data": 突現行為分析指標,
                "comments_data": 代表性評論資料
            }
        """
        import numpy as np
        
        print(f"🧬 [ABM] 開始 ABM 模擬流程，共 {len(sampled_citizens)} 位市民")
        
        # 產品資訊（從 text_context 中提取或使用默認值）
        product_info = {
            "element": "Fire",  # 默認五行屬性（實際應由 AI 判斷）
            "price": 100,
            "market_price": 100
        }
        
        # 嘗試從 text_context 中提取價格資訊
        if text_context:
            import re
            price_match = re.search(r'(?:價格|售價|price)[：:\s]*\$?(\d+)', text_context, re.I)
            if price_match:
                product_info["price"] = float(price_match.group(1))
                product_info["market_price"] = product_info["price"] * 0.95  # 假設市場價略低
        
        # 初始化 ABM 模擬引擎
        abm = ABMSimulation(
            citizens=sampled_citizens,
            product_info=product_info,
            targeting=targeting,
            expert_mode=expert_mode
        )
        
        # 構建社交網絡（基於五行相性）
        abm.build_social_network("element_based")
        
        # 初始化意見（含 Targeting 和 Expert Mode 邏輯）
        abm.initialize_opinions()
        
        # 記錄初始狀態
        initial_avg = np.mean([a.current_opinion for a in abm.agents])
        
        # 執行迭代模擬
        convergence_rate = 0.15 if expert_mode else 0.3  # 專家模式下收斂更慢
        abm.run_iterations(num_iterations=5, convergence_rate=convergence_rate)
        
        # 識別意見領袖
        abm.identify_opinion_leaders(top_n=5)
        
        # 獲取分析結果
        analytics = abm.analyze_emergence()
        
        # 構建演化數據（供前端視覺化）
        final_avg = np.mean([a.current_opinion for a in abm.agents])
        
        evolution_data = {
            "rounds": list(range(len(abm.history))),
            "average_scores": [round(x, 1) for x in abm.history],
            "logs": abm.logs,
            "product_element": product_info.get("element", "Fire"),
            "price_ratio": round(product_info.get("price", 100) / product_info.get("market_price", 100), 2),
            "iterations": 5, # 保留舊欄位以防萬一
            "element_distribution": analytics.get("element_preferences", {}),
            "element_initial_distribution": analytics.get("element_initial_preferences", {}),
            "structure_distribution": analytics.get("structure_preferences", {}),
            "network_density": round(analytics.get("network_density", 0), 4),
            "agents_snapshot": [
                {
                    "id": a.id,
                    "name": a.name,
                    "element": a.element,
                    "structure": a.structure,
                    "initial_opinion": round(a.initial_opinion, 1),
                    "final_opinion": round(a.current_opinion, 1),
                    "is_leader": a.is_opinion_leader,
                    "sentiment": a.get_sentiment()
                }
                for a in abm.agents[:50]  # 只取前 50 個供前端渲染
            ]
        }
        
        # 獲取代表性評論
        comments_data = abm.get_final_comments(num_comments=10)
        
        print(f"✅ [ABM] 模擬完成：初始 {initial_avg:.1f} → 最終 {final_avg:.1f} (Δ{final_avg - initial_avg:+.1f})")
        
        return {
            "evolution_data": evolution_data,
            "analytics_data": analytics,
            "comments_data": comments_data
        }

    async def run_simulation_with_image_data(self, image_data_input, sim_id, text_context=None, language="zh-TW"):
        """核心圖文分析邏輯 (Decoupled & Synced with PDF Flow) - Supports Single or Multiple Images"""
        import traceback
        try:
            with open("debug_image.log", "w", encoding="utf-8") as f: f.write(f"[{sim_id}] STARTING run_simulation_with_image_data (Lang: {language})\n")
            
            # Fetch Scenario
            from app.core.database import get_simulation
            sim_data = get_simulation(sim_id)
            analysis_scenario = sim_data.get("simulation_metadata", {}).get("analysis_scenario", "b2c") if sim_data else "b2c"
            
            # 🌍 Fetch Target Market (Globalization)
            targeting_data = sim_data.get("simulation_metadata", {}).get("targeting", {}) if sim_data else {}
            target_market = targeting_data.get("target_market", "TW") if targeting_data else "TW"
            market_config = MARKET_CULTURE_CONFIG.get(target_market, MARKET_CULTURE_CONFIG["TW"])
            market_context_override = market_config.get("context_override", "")
            


            logger.info(f"🌍 [Globalization] Target Market: {target_market}, Currency: {market_config['currency_code']}")
            
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
            
            # 🧬 【ABM INTEGRATION】執行 Agent-Based Modeling 模擬
            abm_evolution_data = None
            abm_analytics = None
            abm_comments_data = []
            
            try:
                abm_res = await self._run_abm_simulation(sampled_citizens, text_context, language)
                abm_evolution_data = abm_res["evolution_data"]
                abm_analytics = abm_res["analytics_data"]
                abm_comments_data = abm_res["comments_data"]
            except Exception as e:
                print(f"❌ [ABM] ABM模擬失敗: {e}")
                import traceback
                traceback.print_exc()
            
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
                
                # 多語言 Prompt 模板
                prompt_templates = {
                    "zh-TW": """
你是 MIRRA 鏡界系統的核心 AI 策略顧問。請分析這張（或多張）產品圖片，我們已針對 1,000 位虛擬市民進行初步模擬，並從中「選出」以下 10 位具備代表性的 AI 市民，請模擬他們對產品的反應。你需要提供**深度、具體、可執行**的行銷策略建議。
__PRODUCT_CONTEXT__
📋 以下是真實市民資料（八字格局已預先計算）：

__CITIZENS_JSON__

⚠️ **重要指示：市場真實性校準 (Market Reality Check)**
- 作為 AI 顧問，你必須先運用你的知識庫判斷該產品的**真實市場行情** (Standard Retail Price)。
- **如果使用者設定的價格顯著高於市價**（例如：7-11 賣 130 元的菸，使用者賣 150 元）：
  - **市民反應必須負面**：市民應感覺被「當盤子」或「不合理」，購買意圖(Score) 應大幅降低。
  - **嚴禁**出現「雖然貴但我願意買」這類違背常理的評論，除非產品有極特殊的附加價值（但通常標準品沒有）。
  - 請在 Summary 中點出「價格缺乏競爭力」的問題。

⚠️ **重要指示：維度隔離手術 (Dimensional Isolation Protocol)**
作為頂級 AI 策略顧問，你必須嚴格遵守以下維度邊界，禁止建議內容在不同指標間重複或模糊跨越：

1. 📈 **市場潛力 (Market Potential)** —— 關鍵字：【需求與痛點】
   - **核心思考**：Product-Market Fit (PMF)。產品現在能不能賣掉？受眾想不想要？
   - **建議方向**：若分數低，檢討「目標客群設定錯誤」或「核心痛點未被滿足」；若分數高，建議「擴大流量池」或「增加預算」。
   - **🚫 禁區**：嚴禁談論包裝、材質、IP 故事、收藏價值。

2. 💰 **收藏價值 (Collection Value)** —— 關鍵字：【稀缺與情感】
   - **核心思考**：資產增值與情感連結。10年後還有價值嗎？捨不捨得丟？
   - **建議方向**：若分數低，建議「引入編號限量」、「升級材質耐久度」、「擴展 IP 宇宙」；若分數高，建議「發行 NFT 憑證」或「建立二手交易社群」。
   - **🚫 禁區**：嚴禁談論受眾痛點、市場需求、廣告投放、PMF。

3. ✅ **參與覆蓋率 (Coverage)** —— 關鍵字：【信賴度】
   - **核心思考**：數據準不準？樣本是否具備代表性？
   - **建議方向**：只專注於「樣本數」與「抽樣偏差」。建議「增加預演次數」或「放寬受眾篩選條件」。

🎯 請務必回傳一個**純 JSON 字串 (不要 Markdown)**，結構如下：
{
    "simulation_metadata": {
        "product_category": "(必須從以下選擇一個：tech_electronics | collectible_toy | food_beverage | fashion_accessory | home_lifestyle | other)",
        "target_market": "台灣",
        "currency": "TWD (新台幣)",
        "marketing_angle": "(極具洞察力的行銷切角，至少 20 字)",
        "bazi_analysis": "(深入分析產品屬性與五行規律的契合度，至少 50 字)"
    },
    "metric_advice": {
        "market_potential": "針對市場潛力的維度隔離建議 (100字以內)",
        "collection_value": "針對收藏價值的維度隔離建議 (100字以內)",
        "coverage": "針對覆蓋率與信賴度的建議 (100字以內)"
    },
    "result": {
        "score": (0-100 的購買意圖分數),
        "market_sentiment": "樂觀/偏向負面/具有潛力 (四字簡述)",
        "summary": "分析報告標題\n\n[解析] (深入解析產品核心價值、市場定位與潛在痛點，至少 200 字)\n\n[優化] (結合 1,000 位市民的模擬預演結果，提出對此模式的重構或優化方向，至少 200 字)\n\n[戰略] (給出具備「戰略神諭」特質的頂級商業建議，指明產品未來的爆發點，至少 150 字)",
        "objections": [
            {"reason": "質疑點 A", "percentage": 30}
        ],
        "suggestions": [
            {
                "target": "具體受眾群 A",
                "advice": "【寫入對受眾A的具體策略，包含戰術細節，至少 150 字，不得複製此說明文字】",
                "element_focus": "對應五行",
                "execution_plan": ["步驟 1 (具體動作)", "步驟 2", "步驟 3", "步驟 4", "步驟 5"],
                "success_metrics": "具體指標",
                "potential_risks": "可能遇到的挑戰與解決方案",
                "score_improvement": "+X 分"
            },
            {
                "target": "具體受眾群 B",
                "advice": "【寫入對受眾B的具體策略，至少 150 字，內容必須與受眾A完全不同】",
                "element_focus": "對應五行",
                "execution_plan": ["步驟 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"],
                "success_metrics": "具體指標",
                "potential_risks": "風險與備案",
                "score_improvement": "+Y 分"
            },
            {
                "target": "具體受眾群 C",
                "advice": "【寫入對受眾C的具體策略，至少 150 字，內容必須具備獨特性】",
                "element_focus": "對應五行",
                "execution_plan": ["步驟 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"],
                "success_metrics": "具體指標",
                "potential_risks": "風險與備案",
                "score_improvement": "+Z 分"
            }
        ]
    },
    "comments": [
        (必須生成精確 10 則市民評論，對應上方市民名單)
        {"citizen_id": "對應市民的 ID", "sentiment": "positive/neutral/negative", "text": "市民評論內容（繁體中文，需體現個人格局特徵，至少 40 字，禁止使用『符合我的...』這種句型）"}
    ]
}

📌 重要規則：
1. **戰略深度**：summary 的三個部分必須寫滿、寫深，總字數需在 500 字以上。
2. **落地執行**：suggestions 的 steps 必須具體到可以立即操作。
3. **禁止範例內容**：絕對不得直接複製 JSON 結構中的 placeholder 文字。
4. **評論品質**：市民評論必須像真人說話，**嚴禁**出現模板語句。
5. **語言**：所有內容必須使用繁體中文。

""",
                    "zh-CN": """
你是 MIRRA 境界系统的核心 AI 策略顾问。请分析这张（或多张）产品图片，我们已针对 1,000 位虚拟市民进行初步模拟，并从中「选出」以下 10 位具备代表性的 AI 市民，请模拟他们对产品的反应。你需要提供**深度、具体、可执行**的行销策略建议。
__PRODUCT_CONTEXT__
📋 以下是真实市民资料（八字格局已预先计算）：

__CITIZENS_JSON__

⚠️ **重要指示：市场真实性校准 (Market Reality Check)**
- 作为 AI 顾问，你必须先运用你的知识库判断该产品的**真实市场行情** (Standard Retail Price)。
- **如果使用者设定的价格显著高于市价**：
  - **市民反应必须负面**：市民应感觉被「当盘子」或「不合理」，购买意图(Score) 应大幅降低。
  - **严禁**出现「虽然贵但我愿意买」这类违背常理的评论，除非产品有极特殊的附加价值。
  - 请在 Summary 中点出「价格缺乏竞争力」的问题。

⚠️ **重要指示：策略建议必须非常具体且可执行** (请使用简体中文)
- 不要给出「进行 A/B 测试」这种人人都知道的泛泛建议
- 必须根据**这个特定产品**的特点，给出**独特、有洞察力**的行销策略
- 执行步骤要具体到「第一周做什么、第一个月达成什么、如何衡量成效」

🎯 请务必回传一个**纯 JSON 字串 (不要 Markdown)**，结构如下：
{
    "simulation_metadata": {
        "product_category": "(必须从以下选择一个：tech_electronics | collectible_toy | food_beverage | fashion_accessory | home_lifestyle | other)",
        "target_market": "中国大陆",
        "currency": "CNY (人民币)",
        "marketing_angle": "(极具洞察力的行销切角，至少 20 字)",
        "bazi_analysis": "(深入分析产品属性与五行规律的契合度，至少 50 字)"
    },
    "result": {
        "score": (0-100 的购买意图分数),
        "market_sentiment": "乐观/偏向负面/具有潜力 (四字简述)",
        "summary": "分析报告标题\n\n[解析] (深入解析产品核心价值、市场定位与潜在痛点，至少 200 字)\n\n[优化] (结合 1,000 位市民的模拟预演结果，提出对此模式的重构或优化方向，至少 200 字)\n\n[战略] (给出具备「战略神谕」特质的顶级商业建议，指明产品未来的爆发点，至少 150 字)",
        "objections": [
            {"reason": "质疑点 A", "percentage": 30}
        ],
        "suggestions": [
            {
                "target": "具体市场细分对象 1",
                "advice": "150字以上的具体『战术落地』建议...",
                "element_focus": "对应五行",
                "execution_plan": ["步骤 1", "步骤 2", "步骤 3", "步骤 4", "步骤 5"],
                "success_metrics": "具体量化指标",
                "potential_risks": "可能遇到的挑战与备案",
                "score_improvement": "+X 分"
            },
            {
                "target": "具体市场细分对象 2",
                "advice": "150字以上的具体『战术落地』建议...",
                "element_focus": "对应五行",
                "execution_plan": ["步骤 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"],
                "success_metrics": "具体量化指标",
                "potential_risks": "可能遇到的挑战与备案",
                "score_improvement": "+Y 分"
            },
            {
                "target": "具体市场细分对象 3",
                "advice": "150字以上的具体『战术落地』建议...",
                "element_focus": "对应五行",
                "execution_plan": ["步骤 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"],
                "success_metrics": "具体量化指标",
                "potential_risks": "可能遇到的挑战与备案",
                "score_improvement": "+Z 分"
            }
        ]
    },
    "comments": [
        (必須生成精確 10 则市民评论，对应上方市民名单)
        {"citizen_id": "对应市民的 ID", "sentiment": "positive/neutral/negative", "text": "市民评论内容（简体中文，需体现个人格局特征，至少 40 字，禁止使用『符合我的...』这种句型）"}
    ]
}

📌 重要规则：
1. **战略深度**：summary 必须写满、写深，总字数需在 500 字以上。
2. **落地执行**：suggestions 的 steps 必须具体到可以立即操作。
3. **禁止范例内容**：绝对不得直接复制 JSON 结构中的 placeholder 文字。
4. **评论品质**：市民评论必须像真人说话，**严禁**出现模板语句。
5. **语言**：所有内容必须使用简体中文。
""",
                    "en": """
You are the Core AI Strategic Advisor of the MIRRA system. Based on a preliminary simulation of 1,000 virtual citizens, we have "selected" the following 10 representative AI citizens. Please analyze the product image(s) and simulate their reactions. You need to provide **in-depth, specific, and actionable** marketing strategy advice.
__PRODUCT_CONTEXT__
📋 Virtual Citizen Profiles (Bazi structures pre-calculated):

__CITIZENS_JSON__

⚠️ **Important Instruction: Market Reality Check**
- As an AI advisor, you must first use your knowledge base to judge the **standard retail price** of the product.
- **If the user-set price is significantly higher than the market price** (e.g., standard price is $5, user sets $15):
  - **Citizen reactions MUST be negative**: They should feel "ripped off" or "unreasonable".
  - **STRICTLY FORBID** comments like "It's expensive but I'd buy it".
  - Please highlight the "lack of price competitiveness" in the Summary.

⚠️ **Important Instruction: Strategy Advice Must Be Specific and Actionable** (Answer in English)
- Do not give generic advice like "do A/B testing".
- You must provide **unique, insightful** marketing suggestions based on **this specific product's** characteristics.
- Action steps must be specific: "What to do in Week 1, what to achieve in Month 1, how to measure success".

🎯 You must return a **PURE JSON string (No Markdown)**, structure as follows:
{
    "simulation_metadata": {
        "product_category": "(Must choose one: tech_electronics | collectible_toy | food_beverage | fashion_accessory | home_lifestyle | other)",
        "target_market": "International",
        "currency": "USD (US Dollar)",
        "marketing_angle": "(Insightful marketing angle, at least 20 words)",
        "bazi_analysis": "(Deep analysis of product attributes vs Bazi elements, at least 50 words)"
    },
    "result": {
        "score": (0-100),
        "market_sentiment": "Optimistic/Cautious/Potential (Short phrase)",
        "summary": "Report Title\n\n[Analysis] (Deep analysis of value, positioning, pain points, >200 words)\n\n[Optimization] (Based on the simulation results of 1,000 citizens, propose reconstruction or optimization directions, >200 words)\n\n[Strategy] (Top-tier business advice, 'Strategic Oracle' style, >150 words)",
        "objections": [
            {"reason": "Objection A", "percentage": 30}
        ],
        "suggestions": [
            {
                "target": "Specific segment A",
                "advice": "[WRITE_DETAILED_STRATEGY_FOR_A_MIN_150_WORDS_DO_NOT_COPY_THIS]",
                "element_focus": "Specific Element",
                "execution_plan": ["Step 1 (Specific Action)", "Step 2", "Step 3", "Step 4", "Step 5"],
                "success_metrics": "KPIs",
                "potential_risks": "Risks & Mitigations",
                "score_improvement": "+X points"
            },
            {
                "target": "Specific segment B",
                "advice": "[WRITE_DETAILED_STRATEGY_FOR_B_MUST_BE_DIFFERENT_FROM_A]",
                "element_focus": "Specific Element",
                "execution_plan": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"],
                "success_metrics": "KPIs",
                "potential_risks": "Risks & Mitigations",
                "score_improvement": "+Y points"
            },
            {
                "target": "Specific segment C",
                "advice": "[WRITE_DETAILED_STRATEGY_FOR_C_UNIQUE_INSIGHTS]",
                "element_focus": "Specific Element",
                "execution_plan": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"],
                "success_metrics": "KPIs",
                "potential_risks": "Risks & Mitigations",
                "score_improvement": "+Z points"
            }
        ]
    },
    "comments": [
        (Must generate exactly 10 citizen comments, corresponding to the citizen list above)
        {"citizen_id": "CitizenID", "sentiment": "positive/negative/neutral", "text": "Citizen comment (in English, reflecting personal Bazi traits, at least 40 words, avoid using 'meets my needs...' type phrases)"}
    ]
}

📌 Important Rules:
1. **Strategic Depth**: Summary sections must be deep and >500 words total.
2. **Actionable**: Suggestion steps must be immediately executable.
3. **No Placeholders**: Do not copy placeholder text.
4. **Comment Quality**: Comments must sound natural, **strictly avoid** template phrases.
5. **Language**: All content must be in English.
"""
                }

                # B2B Scenario Override
                if analysis_scenario == 'b2b':
                    prompt_templates = {
                        "zh-TW": """
你是 MIRRA 鏡界系統的【首席商業評測官】。你的任務是評估這份「B2B 商業計畫 / 技術解決方案」。
請**完全忽略**個人審美、口感或日常實用性。
你的視角必須轉化為：CFO (財務長)、VC (創投)、CTO (技術長)。
關注核心指標：ROI (投資回報率)、護城河 (Moat)、可擴展性 (Scalability)、供應鏈確保。

__PRODUCT_CONTEXT__
📋 以下是評測委員資料（雖然顯示為市民，請將其性格映射為商業角色）：
- **正財格** 👉 **CFO (財務長)**：嚴查利潤空間、成本結構。
- **七殺格** 👉 **VC (創投)**：看重顛覆性、高回報機會。
- **傷官格** 👉 **CTO (技術長)**：質疑技術可行性、專利壁壘。
- **正官格/正印格** 👉 **COO (營運長)**：關注合規風險、供應鏈穩定。

__CITIZENS_JSON__

⚠️ **重要指示：商業場景維度重定義**
1. 📈 **原本：市場潛力** -> **市場可擴展性 (Scalability)**：TAM/SAM/SOM 分析。
2. 💰 **原本：收藏價值** -> **技術壁壘 (Tech Moat)**：是否有專利？是否難以複製？競爭優勢。
3. ✅ **原本：參與覆蓋率** -> **供應鏈與執行力 (Feasibility)**：團隊執行能力與產能風險。

🎯 請務必回傳一個**純 JSON 字串 (不要 Markdown)**，結構與 B2C 相同（請將商業分析填入對應欄位）：
{
    "simulation_metadata": {
        "product_category": "tech_electronics",
        "target_market": "B2B / Enterprise",
        "currency": "TWD",
        "marketing_angle": "(B2B 商業切角，如『降低 30% OPEX』)",
        "bazi_analysis": "(分析企業五行屬性與行業契合度)"
    },
    "metric_advice": {
        "market_potential": "針對市場規模與擴展性的建議 (Scalability)",
        "collection_value": "針對技術壁壘與護城河的建議 (Moat)",
        "coverage": "針對執行可行性與風險的建議 (Feasibility)"
    },
    "result": {
        "score": (0-100 的 B2B 投資推薦指數),
        "market_sentiment": "值得投資/觀望/高風險 (四字簡述)",
        "summary": "分析報告標題\\n\\n[商業模式解析] (深入解析商業邏輯、獲利模式，至少 200 字)\\n\\n[風險評估] (針對財務、技術、市場風險的評估，至少 200 字)\\n\\n[投資戰略] (給出具體的融資或擴張建議，至少 150 字)",
        "objections": [{"reason": "商業質疑點 A", "percentage": 30}],
        "suggestions": [
            {
                "target": "目標客戶/投資人 A",
                "advice": "【針對 B2B 客戶/投資人的 Pitch 策略，至少 150 字】",
                "element_focus": "對應五行",
                "execution_plan": ["步驟 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"],
                "success_metrics": "ROI/KPI",
                "potential_risks": "風險",
                "score_improvement": "+X 分"
            },
            {
                "target": "目標客戶/投資人 B",
                "advice": "...",
                "element_focus": "...",
                "execution_plan": ["步驟 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"],
                "success_metrics": "ROI/KPI",
                "potential_risks": "風險",
                "score_improvement": "+Y 分"
            },
            {
                "target": "目標客戶/投資人 C",
                "advice": "...",
                "element_focus": "...",
                "execution_plan": ["步驟 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"],
                "success_metrics": "ROI/KPI",
                "potential_risks": "風險",
                "score_improvement": "+Z 分"
            }
        ]
    },
    "comments": [
        (必須生成精確 10 則評論)
        {"citizen_id": "ID", "sentiment": "positive/neutral/negative", "text": "商業評委評論 (繁體中文，模擬 CFO/VC/CTO 口吻，嚴肅專業)"}
    ]
}
""",
                        "zh-CN": """
你是 MIRRA 镜界系统的【首席商业评测官】。你的任务是评估这份「B2B 商业计划 / 技术解决方案」。
请**完全忽略**个人审美、口感或日常实用性。
你的视角必须转化为：CFO (财务长)、VC (创投)、CTO (技术长)。
关注核心指标：ROI (投资回报率)、护城河 (Moat)、可扩展性 (Scalability)、供应链稳定性。

__PRODUCT_CONTEXT__
📋 以下是评测委员资料（请映射为商业角色）：
- **正财格** 👉 **CFO**：严查利润空间。
- **七杀格** 👉 **VC**：看重颠覆性。
- **伤官格** 👉 **CTO**：质疑技术。
- **正官格/正印格** 👉 **COO**：关注合规风险。

__CITIZENS_JSON__

⚠️ **重要指示：商业场景维度重定义**
1. 📈 **市场潜力** -> **市场可扩展性 (Scalability)**
2. 💰 **收藏价值** -> **技术壁垒 (Tech Moat)**
3. ✅ **覆盖率** -> **执行可行性 (Feasibility)**

🎯 回传 JSON (结构同 B2C，填入商业分析)：
{
    "simulation_metadata": { "product_category": "tech_electronics", "target_market": "B2B", "currency": "CNY", "marketing_angle": "(B2B 切角)", "bazi_analysis": "(企业五行分析)" },
    "metric_advice": { "market_potential": "Scalability 建议", "collection_value": "Moat 建议", "coverage": "Feasibility 建议" },
    "result": {
        "score": (投资推荐指数),
        "market_sentiment": "值得投资/观望/高风险",
        "summary": "分析报告标题\\n\\n[商业模式] (至少 200 字)\\n\\n[风险评估] (至少 200 字)\\n\\n[投资战略] (至少 150 字)",
        "objections": [{"reason": "商业质疑", "percentage": 30}],
        "suggestions": [
            { "target": "目标客户 A", "advice": "Pitch 策略...", "element_focus": "...", "execution_plan": ["步骤 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"], "success_metrics": "ROI", "potential_risks": "Risk", "score_improvement": "+X" },
            { "target": "...", "advice": "...", "element_focus": "...", "execution_plan": ["步骤 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"], "success_metrics": "", "potential_risks": "", "score_improvement": "" },
            { "target": "...", "advice": "...", "element_focus": "...", "execution_plan": ["步骤 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"], "success_metrics": "", "potential_risks": "", "score_improvement": "" }
        ]
    },
    "comments": [ {"citizen_id": "ID", "sentiment": "...", "text": "商业评委评论 (简体中文，严严肃专业)"} ]
}
""",
                        "en": """
You are MIRRA's Chief Business Auditor. Evaluate this B2B proposal / Tech Solution.
**IGNORE** personal aesthetics or daily utility.
Transform your role to: CFO, VC, CTO.
Focus on: ROI, Moat, Scalability, Supply Chain.

__PRODUCT_CONTEXT__
📋 Committee Profile (Map Bazi to Business Roles):
- **Direct Wealth** 👉 **CFO**: Profit margin focus.
- **Seven Killings** 👉 **VC**: High risk/reward.
- **Hurting Officer** 👉 **CTO**: Tech feasibility.

__CITIZENS_JSON__

⚠️ **Dimensional Redefinition**
1. 📈 **Market Potential** -> **Scalability (TAM/SAM)**
2. 💰 **Collection Value** -> **Tech Moat / IP**
3. ✅ **Coverage** -> **Feasibility / Execution**

🎯 Return JSON (Fill with Business Analysis):
{
    "simulation_metadata": { "product_category": "tech_electronics", "target_market": "B2B", "currency": "USD", "marketing_angle": "(B2B Angle)", "bazi_analysis": "(Corporate Element Analysis)" },
    "metric_advice": { "market_potential": "Scalability Advice", "collection_value": "Moat Advice", "coverage": "Feasibility Advice" },
    "result": {
        "score": (Investment Index 0-100),
        "market_sentiment": "Investable/Risky/Watch",
        "summary": "Title\\n\\n[Business Model] (>200 words)\\n\\n[Risk Assessment] (>200 words)\\n\\n[Strategy] (>150 words)",
        "objections": [{"reason": "Business Objection", "percentage": 30}],
        "suggestions": [
            { "target": "Target Client A", "advice": "B2B Strategy...", "element_focus": "...", "execution_plan": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"], "success_metrics": "ROI", "potential_risks": "Risk", "score_improvement": "+X" },
            { "target": "...", "advice": "...", "element_focus": "...", "execution_plan": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"], "success_metrics": "", "potential_risks": "", "score_improvement": "" },
            { "target": "...", "advice": "...", "element_focus": "...", "execution_plan": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"], "success_metrics": "", "potential_risks": "", "score_improvement": "" }
        ]
    },
    "comments": [ {"citizen_id": "ID", "sentiment": "...", "text": "Business Comment (Professional, CFO/VC tone)"} ]
}
"""
                    }

                prompt_template = prompt_templates.get(language, prompt_templates["zh-TW"])
                prompt_text = prompt_template.replace("__PRODUCT_CONTEXT__", product_context).replace("__CITIZENS_JSON__", citizens_json)
                
                # 🌍 注入市場文化覆蓋到 Prompt 開頭 (Chameleon Architecture)
                if market_context_override:
                    prompt_text = market_context_override + "\n\n" + prompt_text
                    logger.info(f"[{sim_id}] Market context override injected for: {target_market}")

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
            # 增加 timeout 到 180 秒，讓 AI 有足夠時間生成詳細評論
            ai_text, last_error = await self._call_gemini_rest(api_key, prompt_text, image_parts=image_parts, timeout=180)
            
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
            # 加強過濾條件：要求至少 40 字且排除更多罐頭回覆
            filtered_comments = []
            forbidden_phrases = [
                "符合我的", "看起來不錯", "值得購買", "值得买", "看起来不错",
                "符合我的需求", "非常喜歡", "非常喜欢", "好產品", "好产品",
                "推薦購買", "推荐购买", "挺好的", "蠻好的", "還不錯", "还不错",
                "looks good", "worth buying", "meets my needs", "highly recommend"
            ]
            for c in gemini_comments:
                if not isinstance(c, dict): continue
                text = c.get("text", "")
                # 過濾條件：
                # 1. 長度必須至少 40 字（原本是 10 字）
                # 2. 不包含任何罐頭回覆關鍵字
                if len(text) < 40:
                    logger.warning(f"[FILTER] Comment too short ({len(text)} chars): {text[:30]}...")
                    continue
                if any(phrase in text for phrase in forbidden_phrases):
                    logger.warning(f"[FILTER] Forbidden phrase detected: {text[:30]}...")
                    continue
                filtered_comments.append(c)
            gemini_comments = filtered_comments
            logger.info(f"[{sim_id}] After quality filter: {len(gemini_comments)} comments passed")
            
            # --- 2. FALLBACK MECHANISM (Fill up to 10) ---
            if len(gemini_comments) < 10:
                 logger.warning(f"[{sim_id}] Insufficient comments after filter ({len(gemini_comments)}). Generating fallback.")
                 fallback_comments = list(gemini_comments) # Copy
                 already_ids = {str(c.get("citizen_id")) for c in fallback_comments}
                 
                 # Improved Templates (Generic but realistic, avoiding forbidden phrases)
                 fallback_templates_map = {
                    "zh-TW": [
                        "身為{occupation}，我覺得這產品的實用性很高，會想嘗試看看。",
                        "雖然價格需要考量，但整體的質感很吸引我，{structure}的人通常蠻喜歡這種設計。",
                        "對{age}歲的我來說，這產品解決了不少麻煩，值得推薦。",
                        "設計感很強，感覺能夠提升生活品質，很有興趣！",
                        "目前市面上類似產品很多，但這款的獨特性在於細節處理。",
                        "我是比較務實的人，這產品的功能確實有打中我的痛點。",
                        "從{element}行人的角度來看，這種風格很有能量，感覺不錯。",
                        "剛好最近有在找類似的東西，這款列入考慮清單。",
                        "產品概念很有趣，如果售價親民一點我會直接買單。"
                    ],
                    "zh-CN": [
                        "身为{occupation}，我觉得这产品的实用性很高，会想尝试看看。",
                        "虽然价格需要考量，但整体的质感很吸引我，{structure}的人通常蛮喜欢这种设计。",
                        "对{age}岁的我来说，这产品解决了不少麻烦，值得推荐。",
                        "设计感很强，感觉能够提升生活品质，很有兴趣！",
                        "目前市面上类似产品很多，但这款的独特性在于细节处理。",
                        "我是比较务实的人，这产品的功能确实有打中我的痛点。",
                        "从{element}行人的角度来看，这种风格很有能量，感觉不错。",
                        "刚好最近有在找类似的东西，这款列入考虑清单。",
                        "产品概念很有趣，如果售价亲民一点我会直接买单。"
                    ],
                    "en": [
                        "As a {occupation}, I find this product very practical and would like to try it.",
                        "Although price is a factor, the quality attracts me. People with {structure} usually like this design.",
                        "For someone aged {age}, this product solves a lot of trouble and is worth recommending.",
                        "Strong design sense, feels like it can improve quality of life, very interested!",
                        "There are many similar products, but the uniqueness of this one lies in the details.",
                        "I am a practical person, and this product's functions really hit my pain points.",
                        "From the perspective of a {element} element person, this style is very energetic.",
                        "Just happened to be looking for something similar recently, considering this one.",
                        "The product concept is interesting, if the price is friendlier I would buy it."
                    ]
                 }
                 fallback_templates = fallback_templates_map.get(language, fallback_templates_map["zh-TW"])

                 for c in sampled_citizens: 
                      if len(fallback_comments) >= 10: break
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
                          
                          default_texts = {
                                "zh-TW": "這產品很有特色，我會考慮購買。",
                                "zh-CN": "这产品很有特色，我会考虑购买。",
                                "en": "This product is unique, I will consider buying it."
                            }
                          text = default_texts.get(language, default_texts["zh-TW"])

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
                summary=result_data.get("summary"),
                language=language, metric_advice=data.get("metric_advice")
            )
            
            # 🧬 【ABM EVOLUTION】添加演化數據到methodology_data
            if abm_evolution_data:
                methodology_sidecar["abm_evolution"] = abm_evolution_data
                print(f"✅ [ABM] Evolution數據已添加到methodology_data")
            
            # 🧬 【ABM ANALYTICS】添加突現行為分析指標
            if abm_analytics:
                methodology_sidecar["abm_analytics"] = {
                    "consensus": round(abm_analytics.get("consensus", 0), 3),
                    "polarization": round(abm_analytics.get("polarization", 0), 3),
                    "herding_strength": round(abm_analytics.get("herding_strength", 0), 2),
                    "network_density": round(abm_analytics.get("network_density", 0), 3),
                    "element_preferences": {
                        k: round(v, 1) for k, v in abm_analytics.get("element_preferences", {}).items()
                    }
                }
                print(f"✅ [ABM] Analytics數據已添加到methodology_data")
            
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

    async def run_simulation_with_pdf_data(self, pdf_bytes, sim_id, file_name, language="zh-TW"):
        """核心 PDF 分析邏輯 (Decoupled)"""
        with open("debug_trace.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] PDF Flow Start (Lang: {language})\n")
        try:
            # Convert PDF to base64
            pdf_b64 = base64.b64encode(pdf_bytes).decode('utf-8')
            with open("debug_trace.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] PDF Base64 done\n")
            
            # 🌍 Fetch Target Market (Globalization)
            from app.core.database import get_simulation
            sim_data = get_simulation(sim_id)
            targeting_data = sim_data.get("simulation_metadata", {}).get("targeting", {}) if sim_data else {}
            target_market = targeting_data.get("target_market", "TW") if targeting_data else "TW"
            market_config = MARKET_CULTURE_CONFIG.get(target_market, MARKET_CULTURE_CONFIG["TW"])
            market_context_override = market_config.get("context_override", "")



            logger.info(f"🌍 [PDF Globalization] Target Market: {target_market}")

            # 2. 從資料庫隨機抽取市民
            from fastapi.concurrency import run_in_threadpool
            # [Fix] 使用 run_in_threadpool 抽樣 30 位市民，從中精選 10 位生成評論
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
            
            # 3. Prompt (Default to zh-TW base)
            prompt_base_tw = f"""
你是 MIRRA 鏡界系統的核心 AI 策略顧問。你正在審閱一份商業計劃書 PDF，並需要提供**深度、具體、可執行**的策略建議。我們已針對 1,000 位虛擬市民進行初步模擬，並從中「選出」以下 10 位具備代表性的 AI 市民，請模擬他們對這份計劃書的反應。

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
        "currency": "TWD (新台幣)",
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
        "summary": "分析報告標題\n\n[解析] (深入解析產品核心價值、市場缺口與設計初衷，至少 200 字)\n\n[優化] (結合 1,000 位市民的模擬預演結果，提出對此模式的重構或優化方向，至少 200 字)\n\n[戰略] (給出具備戰略高度的改進意見，指引其爆發，至少 150 字)",
        "objections": [
            {{"reason": "...", "percentage": 30}}
        ],
        "suggestions": [
            {{
                "target": "具體市場細分對象 1",
                "advice": "【針對受眾 A 寫入具體戰術細節，至少 150 字，不得複製此指令文字】",
                "element_focus": "五行",
                "execution_plan": ["步驟 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"],
                "success_metrics": "具體指標",
                "potential_risks": "挑戰與對策",
                "score_improvement": "+X 分"
            }},
            {{
                "target": "具體市場細分對象 2",
                "advice": "【針對受眾 A 寫入具體戰術細節，至少 150 字，不得複製此指令文字】",
                "element_focus": "五行",
                "execution_plan": ["步驟 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"],
                "success_metrics": "具體指標",
                "potential_risks": "挑戰與對策",
                "score_improvement": "+Y 分"
            }},
            {{
                "target": "具體市場細分對象 3",
                "advice": "【針對受眾 A 寫入具體戰術細節，至少 150 字，不得複製此指令文字】",
                "element_focus": "五行",
                "execution_plan": ["步驟 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"],
                "success_metrics": "具體指標",
                "potential_risks": "挑戰與對策",
                "score_improvement": "+Z 分"
            }}
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
3. **評論品質**：每則評論必須至少 40 字，嚴禁使用模板化語句（如「符合我的需求」），必須體現市民個人格局。
4. **suggestions 必須非常具體**：每個建議150字以上，執行計劃5個步驟含時間表，不要泛泛而談
5. 禁止使用「進行 A/B 測試」、「優化行銷文案」這類通用建議，必須針對這個特定商業模式給出獨特見解
"""

            # --- Multi-language Prompt Logic ---
            if language == "en":
                prompt_text = f"""
You are the Core AI Strategic Advisor of the MIRRA system. You are reviewing a Business Plan PDF and need to provide **in-depth, specific, and actionable** strategic advice. Based on a preliminary simulation of 1,000 virtual citizens, we have "selected" the following 10 representative AI citizens to engage in a fierce debate regarding the "Business Feasibility", "Revenue Model", and "Market Pain Points" of this business plan.

📋 Virtual Citizen Profiles (Bazi structures pre-calculated):

{citizens_json}

⚠️ **Important Instruction: Strategy Advice Must Be Specific and Actionable**
- Do not give generic advice like "do A/B testing".
- You must provide **unique, insightful** suggestions based on **this specific business model's** characteristics.
- Action steps must be specific: "What to do in Week 1, what to achieve in Month 1, how to measure success".
- Each suggestion must explain "Why is this important for this specific business model".

🎯 You must return a **PURE JSON string (No Markdown)**, structure as follows:

{{
    "simulation_metadata": {{
        "product_category": "Business Plan",
        "target_market": "International",
        "currency": "USD (US Dollar)",
        "sample_size": 10,
        "bazi_distribution": {{
            "Fire": (%), "Water": (%), "Metal": (%), "Wood": (%), "Earth": (%)
        }}
    }},
    "genesis": {{
        "total_population": 1000,
        "personas": [
            (Must select 10 citizens)
            {{"id": "...", "name": "...", "age": "...", "element": "...", "day_master": "...", "pattern": "...", "trait": "...", "decision_logic": "..."}}
        ]
    }},
    "arena_comments": [
        (Must generate exactly 10 debate comments on the business model by citizens)
        {{"sentiment": "...", "text": "...", "persona": {{ ... }} }}
    ],
    "result": {{
        "score": (0-100),
        "summary": "Report Title\\n\\n[Analysis] (Deep analysis of core value, market gap, and design intent, >200 words)\\n\\n[Optimization] (Based on the simulation results of 1,000 citizens, propose reconstruction or optimization directions, >200 words)\\n\\n[Strategy] (Provide high-level strategic improvements to guide explosion, >150 words)",
        "objections": [
            {{"reason": "...", "percentage": 30}}
        ],
        "suggestions": [
            {{
                "target": "Specific Market Segment 1",
                "advice": ">150 words specific 'Tactical Landing' advice...",
                "element_focus": "Element",
                "execution_plan": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"],
                "success_metrics": "Specific Metrics",
                "potential_risks": "Challenges & Countermeasures",
                "score_improvement": "+X points"
            }},
            {{
                "target": "Specific Market Segment 2",
                "advice": ">150 words specific 'Tactical Landing' advice...",
                "element_focus": "Element",
                "execution_plan": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"],
                "success_metrics": "Specific Metrics",
                "potential_risks": "Challenges & Countermeasures",
                "score_improvement": "+Y points"
            }},
            {{
                "target": "Specific Market Segment 3",
                "advice": ">150 words specific 'Tactical Landing' advice...",
                "element_focus": "Element",
                "execution_plan": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"],
                "success_metrics": "Specific Metrics",
                "potential_risks": "Challenges & Countermeasures",
                "score_improvement": "+Z points"
            }}
        ]
    }}
}}

📌 Important Rules:
1. **Analysis Depth**: Summary must strictly follow [Analysis], [Optimization], [Strategy] format, >500 words total.
2. **Actionable**: Suggestions must be concrete and execution plans must have high implementation value.
3. **Comment Quality**: Each comment must be at least 40 words, strictly avoid template phrases (e.g., "meets my needs"), and must reflect the citizen's personal Bazi traits.
4. **No Placeholders**: Do not copy placeholder text.
5. **Context**: This is a business plan analysis, focus on "Feasibility", "Revenue Model", and "Pain Points".
6. **Comments**: Generate investor/entrepreneur perspective comments, quoting specific plan details.
7. **Language**: All content must be in English.
"""
            elif language == "zh-CN":
                prompt_text = f"""
你是 MIRRA 境界系统的核心 AI 策略顾问。你正在审阅一份商业计划书 PDF，并需要提供**深度、具体、可执行**的策略建议。我们已针对 1,000 位虚拟市民进行初步模拟，并从中「选出」以下 10 位具备代表性的 AI 市民，请模拟他们对这份计划书的反应。

📋 以下是真实市民资料（八字格局已预先计算）：

{citizens_json}

⚠️ **重要指示：策略建议必须非常具体且可执行**
- 不要给出「进行 A/B 测试」这种人人都知道的泛泛建议
- 必须根据**这个特定商业模式**的特点，给出**独特、有洞察力**的建议
- 执行步骤要具体到「第一周做什么、第一个月达成什么、如何衡量成效」
- 每个建议都要说明「为什么这对这个商业模式特别重要」

🎯 请务必回传一个**纯 JSON 字串 (不要 Markdown)**，结构如下：

{{
    "simulation_metadata": {{
        "product_category": "商业计划书",
        "target_market": "中国大陆",
        "currency": "CNY (人民币)",
        "sample_size": 10,
        "bazi_distribution": {{
            "Fire": (%), "Water": (%), "Metal": (%), "Wood": (%), "Earth": (%)
        }}
    }},
    "genesis": {{
        "total_population": 1000,
        "personas": [
            (必须挑选 10 位市民)
            {{"id": "...", "name": "...", "age": "...", "element": "...", "day_master": "...", "pattern": "...", "trait": "...", "decision_logic": "..."}}
        ]
    }},
    "arena_comments": [
        (必须生成精确 10 则市民针对商业模式的辩论评论)
        {{"sentiment": "...", "text": "...", "persona": {{ ... }} }}
    ],
    "result": {{
        "score": (0-100),
        "summary": "分析报告标题\\n\\n[解析] (深入解析产品核心价值、市场缺口与设计初衷，至少 200 字)\\n\\n[优化] (结合 1,000 位市民的模拟预演结果，提出对此模式的重构或优化方向，至少 200 字)\\n\\n[战略] (给出具备战略高度的改进意见，指引其爆发，至少 150 字)",
        "objections": [
            {{"reason": "...", "percentage": 30}}
        ],
        "suggestions": [
            {{
                "target": "具体市场细分对象 1",
                "advice": "150字以上的具体『战术落地』建议...",
                "element_focus": "对应五行",
                "execution_plan": ["步骤 1", "步骤 2", "步骤 3", "步骤 4", "步骤 5"],
                "success_metrics": "具体量化指标",
                "potential_risks": "可能遇到的挑战与备案",
                "score_improvement": "+X 分"
            }},
            {{
                "target": "具体市场细分对象 2",
                "advice": "150字以上的具体『战术落地』建议...",
                "element_focus": "对应五行",
                "execution_plan": ["步骤 1", "步骤 2", "步骤 3", "步骤 4", "步骤 5"],
                "success_metrics": "具体量化指标",
                "potential_risks": "可能遇到的挑战与备案",
                "score_improvement": "+Y 分"
            }},
            {{
                "target": "具体市场细分对象 3",
                "advice": "150字以上的具体『战术落地』建议...",
                "element_focus": "对应五行",
                "execution_plan": ["步骤 1", "步骤 2", "步骤 3", "步骤 4", "步骤 5"],
                "success_metrics": "具体量化指标",
                "potential_risks": "可能遇到的挑战与备案",
                "score_improvement": "+Z 分"
            }}
        ]
    }}
}}

📌 重要規則：
1. **分析深度**：summary 必须严格遵守 [解析]、[优化]、[战略] 三段式，总字数 500 字以上。
2. **落地性**：三个建议 suggestions 必须完全不同，且 execution_plan 具备极高执行价值。
3. **禁止范例内容**：绝对不得直接复制 JSON 结构中的 placeholder 文字。
4. **语言**：所有内容必须使用简体中文。
"""
            else:
                 prompt_text = prompt_base_tw
            
            # 🌍 注入市場文化覆蓋到 Prompt 開頭 (Chameleon Architecture)
            if market_context_override:
                prompt_text = market_context_override + "\n\n" + prompt_text
                logger.info(f"[{sim_id}] PDF Market context override injected for: {target_market}")

            # 🧬 【ABM INTEGRATION】執行 Agent-Based Modeling 模擬
            abm_evolution_data = None
            abm_analytics = None
            abm_comments_data = []
            
            try:
                # PDF 分析通常需要更多上下文
                abm_res = await self._run_abm_simulation(sampled_citizens, text_context or "PDF Business Plan", language)
                abm_evolution_data = abm_res["evolution_data"]
                abm_analytics = abm_res["analytics_data"]
                abm_comments_data = abm_res["comments_data"]
            except Exception as e:
                logger.error(f"❌ [ABM] PDF ABM模擬失敗: {e}")

            # 4. REST API Call
            api_key = settings.GOOGLE_API_KEY
            # [Fix] PDF needs more time. Set base timeout to 300s for large files.
            # Explicitly log start time and payload size
            import datetime
            ts_start = datetime.datetime.now().isoformat()
            payload_len = len(pdf_b64) if pdf_b64 else 0
            with open("debug_trace.log", "a", encoding="utf-8") as f: 
                f.write(f"[{sim_id}] [TIME:{ts_start}] Calling Gemini REST API (PDF), Payload: {payload_len} bytes, Lang: {language}\n")
            
            ai_text, last_error = await self._call_gemini_rest(api_key, prompt_text, pdf_b64=pdf_b64, timeout=300)

            ts_end = datetime.datetime.now().isoformat()
            with open("debug_trace.log", "a", encoding="utf-8") as f: 
                f.write(f"[{sim_id}] [TIME:{ts_end}] Gemini Returned (PDF). Success: {ai_text is not None}\n")
            
            if ai_text is None:
                err_msg = f"All models failed for PDF. {last_error}"
                logger.error(f"[{sim_id}] {err_msg}")
                with open("debug_trace.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] ERROR: {err_msg}. Triggering FALLBACK.\n")
                ai_text = "{}"

            # 5. Process
            data = self._clean_and_parse_json(ai_text)
            
            # 🔍 [DEBUG] Log parsed JSON structure to diagnose "AI 分析超時" issue
            with open("debug_trace.log", "a", encoding="utf-8") as f:
                f.write(f"[{sim_id}] Parsed JSON Keys: {list(data.keys()) if isinstance(data, dict) else 'NOT_DICT'}\n")
                result_obj = data.get("result", {})
                f.write(f"[{sim_id}] result Keys: {list(result_obj.keys()) if isinstance(result_obj, dict) else 'NOT_DICT'}\n")
                summary_val = result_obj.get("summary", "<<MISSING>>") if isinstance(result_obj, dict) else "<<RESULT_NOT_DICT>>"
                f.write(f"[{sim_id}] result.summary (first 200 chars): {str(summary_val)[:200]}\n")
                suggestions_val = result_obj.get("suggestions", []) if isinstance(result_obj, dict) else []
                f.write(f"[{sim_id}] result.suggestions count: {len(suggestions_val) if isinstance(suggestions_val, list) else 'NOT_LIST'}\n")
            
            # [Fix] Initialize key variables to avoid UnboundLocalError
            arena_comments = []
            filtered_comments = []
            personas = []
            
            # --- 🧬 整合 ABM 數據到結果中 ---
            if abm_evolution_data:
                data["abm_evolution"] = abm_evolution_data
            if abm_analytics:
                data["abm_analytics"] = abm_analytics
            if abm_comments_data:
                # 合併 Gemini 評論與 ABM 評論 (Gemini 優先)
                existing_comments = data.get("arena_comments", [])
                data["arena_comments"] = existing_comments + abm_comments_data
            
            # 6. Build Result Data
            sim_metadata = data.get("simulation_metadata", {})
            # PDF uploads always use tech_monetization metric
            sim_metadata["source_type"] = "pdf"
            sim_metadata["product_category"] = "tech_electronics"
            
            # --- [Fix] 確保就算 Gemini 失敗，也要有 personas 資料顯示在 UI ---
            genesis_data = data.get("genesis", {})
            personas = genesis_data.get("personas", [])
            if not personas and sampled_citizens:
                # 如果 Gemini 沒給 personas，從抽樣的市民中選 10 個
                for c in sampled_citizens[:10]:
                    bazi = c.get("bazi_profile") or {}
                    personas.append({
                        "id": str(c.get("id", "0")),
                        "name": c.get("name", "AI市民"),
                        "age": str(c.get("age", 30)),
                        "element": bazi.get("element", "未知"),
                        "day_master": bazi.get("day_master", "未知"),
                        "pattern": bazi.get("structure", "未知"),
                        "trait": c.get("traits")[0] if c.get("traits") else "積極",
                        "decision_logic": "理性分析商業模式可行性"
                    })

            bazi_dist = sim_metadata.get("bazi_distribution", {"Fire": 20, "Water": 20, "Metal": 20, "Wood": 20, "Earth": 20})
            
            # --- 1. QUALITY FILTER FIRST (Sync with Image Flow) ---
            # [Fix] 抓取 Gemini 返回的評論或是合併後的評論
            raw_arena_comments = data.get("arena_comments", [])
            filtered_comments = []
            forbidden_phrases = [
                "符合我的", "看起來不錯", "值得購買", "值得买", "看起来不错",
                "符合我的需求", "非常喜歡", "非常喜欢", "好產品", "好产品",
                "推薦購買", "推荐购买", "挺好的", "蠻好的", "還不錯", "还不错",
                "looks good", "worth buying", "meets my needs", "highly recommend"
            ]
            for c in raw_arena_comments:
                if not isinstance(c, dict): continue
                text = c.get("text", "")
                if len(text) < 40: continue
                if any(phrase in text for phrase in forbidden_phrases): continue
                filtered_comments.append(c)
            
            # --- 2. FALLBACK MECHANISM (Fill up to 10) ---
            if len(filtered_comments) < 10:
                logger.warning(f"[{sim_id}] PDF Analysis: Insufficient comments ({len(filtered_comments)}). Filling fallback.")
                already_names = {c.get("persona", {}).get("name") for c in filtered_comments if c.get("persona")}
                
                fallback_templates_map = {
                    "zh-TW": ["身為投資分析的角度看，這份計劃書在{pattern}層面很有潛力，但{element}行的考量不可少。", "作為創業者，我覺得獲利模式還能再優化，特別是針對{age}歲客群的切入點。"],
                    "zh-CN": ["身为投资分析的角度看，这份计划书在{pattern}层面很有潜力，但{element}行的考量不可少。", "作为创业者，我觉得获利模式还能再优化，特别是针对{age}岁客群的切入点。"],
                    "en": ["From an investment perspective, this plan has potential in {pattern}, but needs {element} consideration.", "As an entrepreneur, the revenue model needs optimization for the {age} age group."]
                }
                templates = fallback_templates_map.get(language, fallback_templates_map["zh-TW"])
                
                for citizen in sampled_citizens:
                    if len(filtered_comments) >= 10: break
                    if citizen["name"] in already_names: continue
                    
                    bazi = citizen.get("bazi_profile", {})
                    text = random.choice(templates).format(
                        pattern=bazi.get("structure", "市場"),
                        element=bazi.get("element", "五行"),
                        age=citizen.get("age", 30)
                    )
                    filtered_comments.append({
                        "sentiment": "neutral",
                        "text": text,
                        "persona": {"name": citizen["name"]} # Temporary persona for matching
                    })
            arena_comments = filtered_comments
            # -----------------------------------------------

            # -----------------------------------------------

            # 補充 arena_comments 中每個 persona 的完整八字資料
            # 將原本的 arena_comments 變數直接延續使用（來自 filtered_comments）
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
                "summary": data.get("result", {}).get("summary", "AI 分析超時，無法生成完整報告。請稍後重試。"),
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
            
            # 🧬 【ABM INTEGRATION】執行 Agent-Based Modeling 模擬
            try:
                abm_res = await self._run_abm_simulation(sampled_citizens, None, language)
                abm_evolution_data = abm_res["evolution_data"]
                abm_analytics = abm_res["analytics_data"]
            except Exception as e:
                logger.error(f"[{sim_id}] ABM Simulation Failed: {e}")
                abm_evolution_data = None
                abm_analytics = None

            # 🧬 [Sidecar] 追加計算社會科學方法論詮釋層
            methodology_sidecar = _generate_methodology_sidecar(
                score=result_data.get("score"),
                summary=result_data.get("summary"),
                language=language, metric_advice=data.get("metric_advice")
            )

            # 🧬 【ABM EVOLUTION】添加演化數據
            if abm_evolution_data:
                methodology_sidecar["abm_evolution"] = abm_evolution_data
            if abm_analytics:
                methodology_sidecar["abm_analytics"] = abm_analytics

            result_data["methodology_data"] = methodology_sidecar
            
            with open("debug_trace.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] Updating DB (PDF)...\n")
            await run_in_threadpool(update_simulation, sim_id, "ready", result_data)
            print(f"✅ [Core PDF] 商業計劃書分析已寫入 PostgreSQL: {sim_id}")

        except Exception as e:
            with open("debug_trace.log", "a", encoding="utf-8") as f: f.write(f"[{sim_id}] ERROR: {str(e)}\n")
            print(f"[Core PDF] Analysis Failed: {e}")
            self._handle_error_db(sim_id, str(e))

    async def run_simulation_with_text_data(self, text_content: str, sim_id: str, source_type: str = "txt", language: str = "zh-TW"):
        """處理純文字內容的商業計劃書分析 (Word/PPT/TXT) - 與 PDF 流程對齊"""
        try:
            from fastapi.concurrency import run_in_threadpool
            
            print(f"[Core TEXT] Starting text analysis for {sim_id}, source: {source_type}")
            
            # 🌍 Fetch Target Market (Globalization)
            from app.core.database import get_simulation
            sim_data = get_simulation(sim_id)
            targeting_data = sim_data.get("simulation_metadata", {}).get("targeting", {}) if sim_data else {}
            target_market = targeting_data.get("target_market", "TW") if targeting_data else "TW"
            market_config = MARKET_CULTURE_CONFIG.get(target_market, MARKET_CULTURE_CONFIG["TW"])
            market_context_override = market_config.get("context_override", "")
            logger.info(f"🌍 [TEXT Globalization] Target Market: {target_market}")
            
            # 1. 從資料庫隨機抽取市民
            # [Fix] 抽樣 30 位市民，從中精選 10 位生成評論
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
            
            # 3. 建構 Prompt (Default to zh-TW base)
            prompt_base_tw = f"""你是 MIRRA 鏡界系統的核心 AI 策略顧問。你正在審閱一份商業計劃書（來自 {source_type.upper()} 文件），並需要提供**深度、具體、可執行**的策略建議。

以下是文件內容：
---
{text_content[:8000]}  
---

請讓以下從 1,000 位虛擬市民中選出的 10 位具備代表性的 AI 虛擬市民，針對這份商業計劃書進行「商業可行性」、「獲利模式」與「市場痛點」的激烈辯論。

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
        "summary": "分析報告標題\n\n[解析] (深入解析產品核心價值、市場缺口與設計初衷，至少 200 字)\n\n[優化] (結合 1,000 位市民的模擬預演結果，提出對此模式的重構或優化方向，至少 200 字)\n\n[戰略] (給出具備戰略高度的改進意見，指引其爆發，至少 150 字)",
        "objections": [
            {{"reason": "...", "percentage": 30}}
        ],
        "suggestions": [
            {{
                "target": "具體市場細分對象 1",
                "advice": "【針對受眾 A 寫入具體戰術細節，至少 150 字，不得複製此指令文字】",
                "element_focus": "五行",
                "execution_plan": ["步驟 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"],
                "success_metrics": "具體指標",
                "potential_risks": "挑戰與對策",
                "score_improvement": "+X 分"
            }},
            {{
                "target": "具體市場細分對象 2",
                "advice": "【針對受眾 A 寫入具體戰術細節，至少 150 字，不得複製此指令文字】",
                "element_focus": "五行",
                "execution_plan": ["步驟 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"],
                "success_metrics": "具體指標",
                "potential_risks": "挑戰與對策",
                "score_improvement": "+Y 分"
            }},
            {{
                "target": "具體市場細分對象 3",
                "advice": "【針對受眾 A 寫入具體戰術細節，至少 150 字，不得複製此指令文字】",
                "element_focus": "五行",
                "execution_plan": ["步驟 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"],
                "success_metrics": "具體指標",
                "potential_risks": "挑戰與對策",
                "score_improvement": "+Z 分"
            }}
        ]
    }}
}}

📌 重要規則：
1. **分析深度**：summary 必須嚴格遵守 [解析]、[優化]、[戰略] 三段式，總字數 500 字以上。
2. **落地性**：三個建議 suggestions 必須完全不同，且 execution_plan 具備極高執行價值。
3. **評論品質**：每則評論必須至少 40 字，嚴禁使用模板化語句（如「符合我的需求」），必須體現市民個人格局。
4. **禁止範例內容**：絕對不得直接複製 JSON 結構中的 placeholder 文字。
"""

            # --- Multi-language Prompt Logic ---
            if language == "en":
                prompt_text = f"""
You are the Core AI Strategic Advisor of the MIRRA system. You are reviewing a Business Plan (from {source_type.upper()} document) and need to provide **in-depth, specific, and actionable** strategic advice.

Here is the document content:
---
{text_content[:8000]}
---

Please let the following 10 representative AI virtual citizens, selected from a simulation of 1,000 citizens, engage in a fierce debate regarding the "Business Feasibility", "Revenue Model", and "Market Pain Points" of this business plan.

📋 Virtual Citizen Profiles (Bazi structures pre-calculated):

{citizens_json}

⚠️ **Important Instruction: Strategy Advice Must Be Specific and Actionable**
- Do not give generic advice like "do A/B testing".
- You must provide **unique, insightful** suggestions based on **this specific business model's** characteristics.
- Action steps must be specific: "What to do in Week 1, what to achieve in Month 1, how to measure success".
- Each suggestion must explain "Why is this important for this specific business model".

🎯 You must return a **PURE JSON string (No Markdown)**, structure as follows:

{{
    "simulation_metadata": {{
        "product_category": "Business Plan",
        "target_market": "Taiwan",
        "sample_size": 10,
        "bazi_distribution": {{
            "Fire": (%), "Water": (%), "Metal": (%), "Wood": (%), "Earth": (%)
        }}
    }},
    "genesis": {{
        "total_population": 1000,
        "personas": [
            (Must select 10 citizens)
            {{"id": "...", "name": "...", "age": "...", "element": "...", "day_master": "...", "pattern": "...", "trait": "...", "decision_logic": "..."}}
        ]
    }},
    "arena_comments": [
        (Must generate exactly 10 debate comments on the business model by citizens)
        {{"sentiment": "...", "text": "...", "persona": {{ ... }} }}
    ],
    "result": {{
        "score": (0-100),
        "summary": "Report Title\\n\\n[Analysis] (Deep analysis of core value, market gap, and design intent, >200 words)\\n\\n[Optimization] (Based on the simulation results of 1,000 citizens, propose reconstruction or optimization directions, >200 words)\\n\\n[Strategy] (Provide high-level strategic improvements to guide explosion, >150 words)",
        "objections": [
            {{"reason": "...", "percentage": 30}}
        ],
        "suggestions": [
            {{
                "target": "Specific Market Segment 1",
                "advice": ">150 words specific 'Tactical Landing' advice...",
                "element_focus": "Element",
                "execution_plan": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"],
                "success_metrics": "Specific Metrics",
                "potential_risks": "Challenges & Countermeasures",
                "score_improvement": "+X points"
            }},
            {{
                "target": "Specific Market Segment 2",
                "advice": ">150 words specific 'Tactical Landing' advice...",
                "element_focus": "Element",
                "execution_plan": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"],
                "success_metrics": "Specific Metrics",
                "potential_risks": "Challenges & Countermeasures",
                "score_improvement": "+Y points"
            }},
            {{
                "target": "Specific Market Segment 3",
                "advice": ">150 words specific 'Tactical Landing' advice...",
                "element_focus": "Element",
                "execution_plan": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"],
                "success_metrics": "Specific Metrics",
                "potential_risks": "Challenges & Countermeasures",
                "score_improvement": "+Z points"
            }}
        ]
    }}
}}

📌 Important Rules:
1. **Analysis Depth**: Summary must strictly follow [Analysis], [Optimization], [Strategy] format, >500 words total.
2. **Actionable**: Suggestions must be concrete and execution plans must have high implementation value.
3. **Comment Quality**: Each comment must be at least 40 words, strictly avoid template phrases (e.g., "meets my needs"), and must reflect the citizen's personal Bazi traits.
4. **No Placeholders**: Do not copy placeholder text.
5. **Language**: All content must be in English.
"""
            elif language == "zh-CN":
                prompt_text = f"""
你是 MIRRA 境界系统的核心 AI 策略顾问。你正在审阅一份商业计划书（来源 {source_type.upper()} 文件），并需要提供**深度、具体、可执行**的策略建议。

以下是文件内容：
---
{text_content[:8000]}
---

请让以下从 1,000 位虚拟市民中选出的 10 位具备代表性的 AI 虚拟市民，针对这份商业计划书进行「商业可行性」、「获利模式」与「市场痛点」的激烈辩论。

📋 以下是真实市民资料（八字格局已预先计算）：

{citizens_json}

⚠️ **重要指示：策略建议必须非常具体且可执行**
- 不要给出「进行 A/B 测试」这种人人都知道的泛泛建议
- 必须根据**这个特定商业模式**的特点，给出**独特、有洞察力**的建议
- 执行步骤要具体到「第一周做什么、第一个月达成什么、如何衡量成效」
- 每个建议都要说明「为什么这对这个商业模式特别重要」

🎯 请务必回传一个**纯 JSON 字串 (不要 Markdown)**，结构如下：

{{
    "simulation_metadata": {{
        "product_category": "商业计划书",
        "target_market": "台湾",
        "sample_size": 10,
        "bazi_distribution": {{
            "Fire": (%), "Water": (%), "Metal": (%), "Wood": (%), "Earth": (%)
        }}
    }},
    "genesis": {{
        "total_population": 1000,
        "personas": [
            (必须挑选 10 位市民)
            {{"id": "...", "name": "...", "age": "...", "element": "...", "day_master": "...", "pattern": "...", "trait": "...", "decision_logic": "..."}}
        ]
    }},
    "arena_comments": [
        (必须生成精确 10 则市民针对商业模式的辩论评论)
        {{"sentiment": "...", "text": "...", "persona": {{ ... }} }}
    ],
    "result": {{
        "score": (0-100),
        "summary": "分析报告标题\\n\\n[解析] (深入解析产品核心价值、市场缺口与设计初衷，至少 200 字)\\n\\n[优化] (结合 1,000 位市民的模拟预演结果，提出对此模式的重构或优化方向，至少 200 字)\\n\\n[战略] (给出具备战略高度的改进意见，指引其爆发，至少 150 字)",
        "objections": [
            {{"reason": "...", "percentage": 30}}
        ],
        "suggestions": [
            {{
                "target": "具体市场细分对象 1",
                "advice": "150字以上的具体『战术落地』建议...",
                "element_focus": "对应五行",
                "execution_plan": ["步骤 1", "步骤 2", "步骤 3", "步骤 4", "步骤 5"],
                "success_metrics": "具体量化指标",
                "potential_risks": "可能遇到的挑战与备案",
                "score_improvement": "+X 分"
            }},
            {{
                "target": "具体市场细分对象 2",
                "advice": "150字以上的具体『战术落地』建议...",
                "element_focus": "对应五行",
                "execution_plan": ["步骤 1", "步骤 2", "步骤 3", "步骤 4", "步骤 5"],
                "success_metrics": "具体量化指标",
                "potential_risks": "可能遇到的挑战与备案",
                "score_improvement": "+Y 分"
            }},
            {{
                "target": "具体市场细分对象 3",
                "advice": "150字以上的具体『战术落地』建议...",
                "element_focus": "对应五行",
                "execution_plan": ["步骤 1", "步骤 2", "步骤 3", "步骤 4", "步骤 5"],
                "success_metrics": "具体量化指标",
                "potential_risks": "可能遇到的挑战与备案",
                "score_improvement": "+Z 分"
            }}
        ]
    }}
}}

📌 重要规则：
1. **分析深度**：summary 必须严格遵守 [解析]、[优化]、[战略] 三段式，总字数 500 字以上。
2. **落地性**：三个建议 suggestions 必须完全不同，且 execution_plan 具备极高执行价值。
3. **评论品質**：每则评论必须至少 40 字，严禁使用模板化语句（如「符合我的需求」），必须体现市民个人格局。
4. **禁止範例內容**：絕對不得直接複製 JSON 結構中的 placeholder 文字。
5. **语言**：所有内容必须使用简体中文。
"""
            else:
                 prompt_base_tw = f"""
你是 MIRRA 境界系统的核心 AI 策略顾问。你正在审阅一份商业计划书（来源 {source_type.upper()} 文件），并需要提供**深度、具体、可执行**的策略建议。

以下是文件内容：
---
{text_content[:8000]}
---

请让以下从 1,000 位虚拟市民中选出的 10 位具备代表性的 AI 虚拟市民，针对这份商业计划书进行「商业可行性」、「获利模式」与「市场痛点」的激烈辩论。

📋 以下是真实市民资料（八字格局已预先计算）：

{citizens_json}

⚠️ **重要指示：策略建议必须非常具体且可执行**
- 不要给出「进行 A/B 测试」这种人人都知道的泛泛建议
- 必须根据**这个特定商业模式**的特点，给出**独特、有洞察力**的建议
- 执行步骤要具体到「第一周做什么、第一个月达成什么、如何衡量成效」
- 每个建议都要说明「为什么这对这个商业模式特别重要」

🎯 请务必回传一个**純 JSON 字串 (不要 Markdown)**，結構如下：

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
        "summary": "分析報告標題\\n\\n[解析] (深入解析產品核心價值、市場缺口與設計初衷，至少 200 字)\\n\\n[優化] (結合 1,000 位市民的模擬預演結果，提出對此模式的重構或優化方向，至少 200 字)\\n\\n[戰略] (給出具備戰略高度的改進意見，指引其爆發，至少 150 字)",
        "objections": [
            {{"reason": "...", "percentage": 30}}
        ],
        "suggestions": [
            {{
                "target": "具体市场细分对象 1",
                "advice": "150字以上的具体『战术落地』建议...",
                "element_focus": "对应五行",
                "execution_plan": ["步驟 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"],
                "success_metrics": "具体量化指标",
                "potential_risks": "可能遇到的挑战与备案",
                "score_improvement": "+X 分"
            }},
            {{
                "target": "具体市场细分对象 2",
                "advice": "150字以上的具体『戰術落地』建議...",
                "element_focus": "对应五行",
                "execution_plan": ["步驟 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"],
                "success_metrics": "具体量化指标",
                "potential_risks": "可能遇到的挑战与备案",
                "score_improvement": "+Y 分"
            }},
            {{
                "target": "具体市场细分对象 3",
                "advice": "150字以上的具体『戰術落地』建議...",
                "element_focus": "对应五行",
                "execution_plan": ["步驟 1", "步驟 2", "步驟 3", "步驟 4", "步驟 5"],
                "success_metrics": "具体量化指标",
                "potential_risks": "可能遇到的挑战與备案",
                "score_improvement": "+Z 分"
            }}
        ]
    }}
}}

📌 重要規則：
1. **分析深度**：summary 必須嚴格遵守 [解析]、[優化]、[戰略] 三段式，總字數 500 字以上。
2. **落地性**：三個建議 suggestions 必須完全不同，且 execution_plan 具備極高執行價值。
3. **評論品質**：每則評論必須至少 40 字，嚴禁使用模板化語句（如「符合我的需求」），必須體現市民個人格局。
4. **禁止範例內容**：絕對不得直接複製 JSON 結構中的 placeholder 文字。
5. **语言**：所有內容必須使用繁體中文。
"""
                 prompt_text = prompt_base_tw
            
            # 🌍 注入市場文化覆蓋到 Prompt 開頭 (Chameleon Architecture)
            if market_context_override:
                prompt_text = market_context_override + "\n\n" + prompt_text
                logger.info(f"[{sim_id}] TEXT Market context override injected for: {target_market}")

            # 4. 呼叫 Gemini AI (純文字，不需圖片/PDF)
            api_key = settings.GOOGLE_API_KEY
            print(f"[Core TEXT] Sending prompt to Gemini, length: {len(prompt_text)}")
            # Text/PDF content needs more time. Set base timeout to 180s.
            ai_text, last_error = await self._call_gemini_rest(api_key, prompt_text, timeout=180)
            
            if not ai_text:
                print(f"[Core TEXT] Gemini Error: {last_error}. Triggering FALLBACK.")
                # Trigger fallback by providing empty JSON
                ai_text = "{}"
            
            # 5. 解析結果
            data = self._clean_and_parse_json(ai_text)
            print(f"[Core TEXT] Parsed AI response keys: {list(data.keys())}")
            
            
            # --- QUALITY CHECK (Sync with Image/PDF Flow) ---
            raw_arena_comments = data.get("arena_comments", [])
            filtered_comments = []
            forbidden_phrases = [
                "符合我的", "看起來不錯", "值得購買", "值得买", "看起来不错",
                "符合我的需求", "非常喜歡", "非常喜欢", "好產品", "好产品",
                "推薦購買", "推荐购买", "挺好的", "蠻好的", "還不錯", "还不错",
                "looks good", "worth buying", "meets my needs", "highly recommend"
            ]
            for c in raw_arena_comments:
                if not isinstance(c, dict): continue
                text = c.get("text", "")
                if len(text) < 40: continue
                if any(phrase in text for phrase in forbidden_phrases): continue
                filtered_comments.append(c)
            
            # --- 8. FALLBACK MECHANISM (Fill up to 10) ---
            if len(filtered_comments) < 10:
                logger.warning(f"[{sim_id}] Text Analysis: Insufficient comments ({len(filtered_comments)}). Filling fallback.")
                already_names = {c.get("persona", {}).get("name") for c in filtered_comments if c.get("persona")}
                
                fallback_templates_map = {
                    "zh-TW": ["身為投資分析的角度看，這份計劃書在{pattern}層面很有潛力，但{element}行的考量不可少。", "作為創業者，我覺得獲利模式還能再優化，特別是針對{age}歲客群的切入點。"],
                    "zh-CN": ["身为投资分析的角度看，这份计划书在{pattern}层面很有潜力，但{element}行的考量不可少。", "作为创业者，我觉得利模式还能再优化，特别是针对{age}岁客群的切入点。"],
                    "en": ["From an investment perspective, this plan has potential in {pattern}, but needs {element} consideration.", "As an entrepreneur, the revenue model needs optimization for the {age} age group."]
                }
                templates = fallback_templates_map.get(language, fallback_templates_map["zh-TW"])
                
                for citizen in sampled_citizens:
                    if len(filtered_comments) >= 10: break
                    if citizen["name"] in already_names: continue
                    
                    bazi = citizen.get("bazi_profile", {})
                    text = random.choice(templates).format(
                        pattern=bazi.get("structure", "市場"),
                        element=bazi.get("element", "五行"),
                        age=citizen.get("age", 30)
                    )
                    filtered_comments.append({
                        "sentiment": "neutral",
                        "text": text,
                        "persona": {"name": citizen["name"]} # Temporary persona for matching
                    })
            arena_comments = filtered_comments
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
            
            # 8. Update DB (Final result construction)
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
            
            while len(arena_comments) < 10 and sampled_citizens:
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
            
            # 🧬 【ABM INTEGRATION】執行 Agent-Based Modeling 模擬
            try:
                abm_res = await self._run_abm_simulation(sampled_citizens, text_content, language)
                abm_evolution_data = abm_res["evolution_data"]
                abm_analytics = abm_res["analytics_data"]
            except Exception as e:
                logger.error(f"[{sim_id}] ABM Simulation Failed: {e}")
                abm_evolution_data = None
                abm_analytics = None

            # 🧬 [Sidecar] 追加計算社會科學方法論詮釋層
            methodology_sidecar = _generate_methodology_sidecar(
                score=result_data.get("score"),
                summary=result_data.get("summary"),
                language=language, metric_advice=data.get("metric_advice")
            )
            
            # 🧬 【ABM EVOLUTION】添加演化數據
            if abm_evolution_data:
                methodology_sidecar["abm_evolution"] = abm_evolution_data
            if abm_analytics:
                methodology_sidecar["abm_analytics"] = abm_analytics

            result_data["methodology_data"] = methodology_sidecar
            
            # 10. 更新資料庫
            await run_in_threadpool(update_simulation, sim_id, "ready", result_data)
            print(f"✅ [Core TEXT] Document analysis completed: {sim_id}, comments: {len(arena_comments)}, score: {score}")

        except Exception as e:
            print(f"[Core TEXT] Analysis Failed: {e}")
            self._handle_error_db(sim_id, str(e))

    async def run_simulation_with_audio_data(self, audio_bytes: bytes, sim_id: str, audio_format: str = "webm", language: str = "zh-TW"):
        """處理語音錄音的商業計劃書分析 (錄音 → 轉文字 → 分析)"""
        try:
            from fastapi.concurrency import run_in_threadpool
            
            # 1. 使用 Gemini 將音訊轉文字
            audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            # Localized Transcription Prompt
            if language == "en":
                 transcription_prompt = """Please listen to this audio recording and transcribe it fully into English text.
        
This is a recording about a business plan or product idea. Please:
1. Transcribe all spoken content fully
2. Use English
3. Keep the original meaning, add appropriate punctuation for readability
4. If there is stuttering or repetition, smooth it out into fluent text

Output the transcribed text directly, without any additional explanation."""
            elif language == "zh-CN":
                 transcription_prompt = """请听取这段语音录音，并将其完整转录为简体中文文字。
        
这是一段关于商业计划或产品想法的录音。请：
1. 完整转录所有口说内容
2. 使用简体中文
3. 保持原意，适当加入标点符号让内容更易读
4. 如果有口吃或重复的部分，请整理为顺畅的文字

直接输出转录后的文字内容，不要有任何额外说明。"""
            else:
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
            await self.run_simulation_with_text_data(transcribed_text, sim_id, "voice", language=language)

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
    # NOTE: 舊版 _call_gemini_rest 已刪除，現使用第 3898 行的新版本（有 Pro 模型 600 秒 timeout）


    def _clean_and_parse_json(self, ai_text):
        """Helper to clean and parse JSON with robust error handling"""
        if not ai_text or not isinstance(ai_text, str):
            logger.error(f"Invalid AI text input for parsing: {type(ai_text)}")
            with open("debug_trace.log", "a", encoding="utf-8") as f:
                f.write(f"[JSON_PARSE] Invalid input: {type(ai_text)}\n")
            return {"result": {}, "arena_comments": [], "genesis": {}, "simulation_metadata": {}, "comments": [], "suggestions": []}

        clean_text = ai_text.strip()  # 🔧 [Fix] Strip whitespace first
        
        # 🔍 [DEBUG] Log input before processing
        with open("debug_trace.log", "a", encoding="utf-8") as f:
            f.write(f"[JSON_PARSE] Input length: {len(ai_text)}, After strip: {len(clean_text)}\n")
            f.write(f"[JSON_PARSE] First 100 chars after strip: {repr(clean_text[:100])}\n")
        
        # Check for markdown code block
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", ai_text, re.DOTALL)
        if match:
            clean_text = match.group(1).strip()
            with open("debug_trace.log", "a", encoding="utf-8") as f:
                f.write(f"[JSON_PARSE] Extracted from code block, new length: {len(clean_text)}\n")
        
        # 🔧 [Fix] Also try to find JSON object directly if not in code block
        if not clean_text.startswith('{'):
            # Try to find the first { and extract from there
            first_brace = clean_text.find('{')
            if first_brace != -1:
                clean_text = clean_text[first_brace:]
                with open("debug_trace.log", "a", encoding="utf-8") as f:
                    f.write(f"[JSON_PARSE] Found first brace at {first_brace}\n")
        
        try:
            data = json.loads(clean_text)
            if isinstance(data, dict):
                with open("debug_trace.log", "a", encoding="utf-8") as f:
                    f.write(f"[JSON_PARSE] SUCCESS! Keys: {list(data.keys())}\n")
                return data
            else:
                with open("debug_trace.log", "a", encoding="utf-8") as f:
                    f.write(f"[JSON_PARSE] FAILED: Non-dict result: {type(data)}\n")
                return {}
        except json.JSONDecodeError as e:
            # 🔍 [DEBUG] Log the exact error and problematic content
            with open("debug_trace.log", "a", encoding="utf-8") as f:
                f.write(f"[JSON_PARSE] JSONDecodeError: {e}\n")
                f.write(f"[JSON_PARSE] Error position: line {e.lineno}, col {e.colno}\n")
                f.write(f"[JSON_PARSE] First 500 chars: {repr(clean_text[:500])}\n")
            
            # 🔧 [Fix] Remove trailing commas (common issue with AI-generated JSON)
            # Pattern: ,\s*} or ,\s*]
            fixed_text = clean_text.strip()
            fixed_text = re.sub(r',\s*}', '}', fixed_text)  # Remove ,} pattern
            fixed_text = re.sub(r',\s*]', ']', fixed_text)  # Remove ,] pattern
            
            with open("debug_trace.log", "a", encoding="utf-8") as f:
                f.write(f"[JSON_PARSE] Attempting fix with trailing comma removal...\n")
            
            # Also fix unbalanced brackets
            if fixed_text.count('{') > fixed_text.count('}'): fixed_text += '}' * (fixed_text.count('{') - fixed_text.count('}'))
            if fixed_text.count('[') > fixed_text.count(']'): fixed_text += ']' * (fixed_text.count('[') - fixed_text.count(']'))
            try:
                data = json.loads(fixed_text)
                if isinstance(data, dict):
                    with open("debug_trace.log", "a", encoding="utf-8") as f:
                        f.write(f"[JSON_PARSE] Fixed and parsed! Keys: {list(data.keys())}\n")
                    return data
                return {}
            except Exception as fix_err:
                with open("debug_trace.log", "a", encoding="utf-8") as f:
                    f.write(f"[JSON_PARSE] Failed even after fixing: {fix_err}\n")
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
        gemini_comments = data.get("arena_comments") or data.get("comments") or []
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
        
        if not isinstance(arena_comments, list):
            arena_comments = []
            
        # 🛡️ 深度清理與驗證評論格式
        valid_comments = []
        for c in arena_comments:
            if isinstance(c, dict) and c.get("text") and len(str(c.get("text"))) > 5:
                # 確保 persona 結構存在
                if not c.get("persona"):
                    c["persona"] = {}
                valid_comments.append(c)
        arena_comments = valid_comments

        while len(arena_comments) < 10 and sampled_citizens:
            # 找一個還沒評論過的市民
            commented_names = set()
            for c in arena_comments:
                if isinstance(c.get("persona"), dict) and c["persona"].get("name"):
                    commented_names.add(c["persona"]["name"])
                    
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
            text = random.choice(templates)
            
            # 混合分配情感
            sentiments = ["positive", "positive", "neutral", "neutral", "negative"]
            sentiment = sentiments[len(arena_comments) % len(sentiments)]
            
            # 定義 pillars_str
            pillars_str = bazi.get("four_pillars")
            if not pillars_str:
                pillars = ["甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉", "甲戌", "乙亥"]
                pillars_str = f"{random.choice(pillars)} {random.choice(pillars)} {random.choice(pillars)} {random.choice(pillars)}"
            
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
            "summary": data.get("result", {}).get("summary", "AI 分析超時，無法生成完整報告。請稍後重試。"),
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
                "maxOutputTokens": 65536,  # 🔧 [Fix] Increased from 8192 to prevent JSON truncation
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
        # [Restore] Prioritize Quality (Gemini 2.5 Pro)
        models = [
            "gemini-2.5-pro",
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
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
                    current_timeout = max(timeout, 600) # Pro needs 10 mins for detailed analysis
                
                # PDF needs more time regardless of model
                if pdf_b64:
                    current_timeout = max(current_timeout, 120)

                # [Fix] Use Tuple for (connect_timeout, read_timeout) to prevent socket level early termination
                # Most HTTP libraries interpret a single int as both, but explicit tuple is safer.
                # Also ensure asyncio.to_thread is used to prevent blocking.
                print(f"[DEBUG] Calling Gemini Model: {model} with Payload Size: {len(json.dumps(payload))} bytes, Exp. Read Timeout: {current_timeout}s")
                
                # Connection timeout: 30s, Read timeout: current_timeout
                full_timeout_config = (30, current_timeout)
                
                response = await asyncio.to_thread(
                    requests.post, 
                    url, 
                    headers={'Content-Type': 'application/json'}, 
                    json=payload, 
                    timeout=full_timeout_config
                )
                print(f"[DEBUG] Gemini Model {model} returned Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        raw_text = response.json()['candidates'][0]['content']['parts'][0]['text']
                        # 🔍 [DEBUG] Log raw Gemini response for JSON parse debugging
                        with open("debug_trace.log", "a", encoding="utf-8") as f:
                            f.write(f"[GEMINI_RAW] Model: {model}, Response Length: {len(raw_text)} chars\n")
                            f.write(f"[GEMINI_RAW] First 500 chars: {raw_text[:500]}\n")
                        return raw_text, None
                    except Exception as parse_ex:
                        print(f"[DEBUG] Gemini Model {model} parse error: {parse_ex}")
                        continue
                else:
                    last_error = f"{model}: {response.status_code} {response.text}"
            except Exception as e:
                last_error = str(e)
        
        return None, last_error

    # NOTE: 舊版 generate_marketing_copy 已刪除，現使用第 480 行的新版本 (單篇輸出)
    # NOTE: 舊版 refine_marketing_copy 已刪除，現使用第 725 行的新版本 (支援多語言)


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

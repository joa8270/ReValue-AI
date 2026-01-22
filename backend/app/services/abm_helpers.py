"""
ABM Integration Helper Functions for LineBotService

這個模組包含 ABM 引擎整合所需的輔助函數
"""

import re
import json
import asyncio


async def infer_product_element_with_ai(line_bot_service, image_parts, text_context=None):
    """
    使用AI判斷產品的五行屬性（用於ABM模擬）
    
    Args:
        line_bot_service: LineBotService instance
        image_parts: 產品圖片列表
        text_context: 產品文字描述
    
    Returns:
        五行屬性 ("Fire", "Water", "Metal", "Wood", "Earth")
    """
    from app.core.config import settings
    
    prompt = """
請根據產品圖片和描述，判斷該產品的「五行屬性」。

五行屬性判斷標準：
- **火 (Fire)**: 電子產品、科技產品、燈具、加熱類、紅色系產品、能量類
- **水 (Water)**: 飲料、清潔用品、化妝品、流動性商品、藍色/黑色系、液體類
- **金 (Metal)**: 金屬製品、工具、精密儀器、白色/銀色系、硬質產品、樂器
- **木 (Wood)**: 木質產品、植物、書籍、文具、綠色系、環保產品、成長型商品
- **土 (Earth)**: 食品、陶瓷、建材、黃色/褐色系、穩定型產品、土特產

產品資訊：
"""
    if text_context:
        prompt += f"{text_context}\n\n"
    
    prompt += """
請直接回傳JSON格式（不要markdown）：
{
    "element": "Fire|Water|Metal|Wood|Earth",
    "reasoning": "判斷理由"
}
"""
    
    try:
        api_key = settings.GOOGLE_API_KEY
        ai_text, error = await line_bot_service._call_gemini_rest(api_key, prompt, image_parts=image_parts)
        
        if ai_text:
            data = line_bot_service._clean_and_parse_json(ai_text)
            element = data.get("element", "Fire")
            print(f"🧬 [ABM] AI判斷產品五行: {element} - {data.get('reasoning', '')}")
            return element
    except Exception as e:
        print(f"❌ [ABM] 五行判斷失敗: {e}")
    
    # 預設回傳火（電子產品最常見）
    return "Fire"


def extract_price_from_context(text_context):
    """
    從文字上下文中提取價格資訊
    
    Args:
        text_context: 包含價格的文字描述
    
    Returns:
        {"price": float, "market_price": float}
    """
    if not text_context:
        return {"price": 100, "market_price": 100}
    
    # 提取價格數字（支援多種格式）
    # 例如：NT$500、$500、500元、售價：500
    price_patterns = [
        r'售價[：:]\s*[\$NT]*\s*(\d+)',
        r'建議售價[：:]\s*[\$NT]*\s*(\d+)',
        r'[\$NT]+\s*(\d+)',
        r'(\d+)\s*元',
    ]
    
    price = None
    for pattern in price_patterns:
        match = re.search(pattern, text_context)
        if match:
            price = float(match.group(1))
            break
    
    # 如果沒找到價格，用預設值
    if price is None:
        price = 100
    
    # 市場均價預估為售價的90%（簡化邏輯，實際應該查詢API）
    market_price = price * 0.9
    
    print(f"💰 [ABM] 提取價格: 售價={price}, 市價={market_price}")
    
    return {"price": price, "market_price": market_price}


def merge_abm_and_ai_comments(abm_comments, ai_comment_texts):
    """
    合併ABM分析結果與AI生成的評論文字
    
    Args:
        abm_comments: ABM引擎產生的評論結構（含市民資料）
        ai_comment_texts: AI生成的評論文字dict
    
    Returns:
        完整的評論列表
    """
    # AI回應應該是 {"comments": [{"citizen_id": "123", "text": "..."}]}
    ai_texts_map = {}
    if isinstance(ai_comment_texts, dict):
        for comment in ai_comment_texts.get("comments", []):
            citizen_id = str(comment.get("citizen_id"))
            text = comment.get("text", "")
            ai_texts_map[citizen_id] = text
    
    # 合併
    final_comments = []
    for abm_comment in abm_comments:
        citizen_id = str(abm_comment.get("citizen_id"))
        ai_text = ai_texts_map.get(citizen_id, "")
        
        # 如果AI沒生成文字，用ABM的上下文資訊組一個簡單的
        if not ai_text:
            sentiment = abm_comment.get("sentiment", "neutral")
            score = abm_comment.get("opinion_score", 50)
            if sentiment == "positive":
                ai_text = f"整體來說很不錯，分數{score}分，符合我的期待。"
            elif sentiment == "negative":
                ai_text = f"有些疑慮，只給{score}分，還需要觀察。"
            else:
                ai_text = f"還算可以，{score}分，中規中矩。"
        
        final_comments.append({
            "citizen_id": citizen_id,
            "name": abm_comment.get("name"),
            "element": abm_comment.get("element"),
            "structure": abm_comment.get("structure"),
            "sentiment": abm_comment.get("sentiment"),
            "text": ai_text,
            # ABM特有欄位
            "opinion_score": abm_comment.get("opinion_score"),
            "opinion_change": abm_comment.get("opinion_change"),
            "is_leader": abm_comment.get("is_leader", False)
        })
    
    return final_comments

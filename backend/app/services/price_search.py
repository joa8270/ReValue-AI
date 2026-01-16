"""
市場比價模組 - 使用 Gemini 搜尋網路價格（同步版本）
"""
import os
import requests
import json
import re


def search_market_prices_sync(product_name: str, user_price: float = None) -> dict:
    """
    使用 Gemini 搜尋產品的網路價格（同步版本）
    
    Args:
        product_name: 產品名稱
        user_price: 使用者輸入的價格（用於比較）
    
    Returns:
        {
            "success": bool,
            "prices": [{"platform": str, "price": int, "note": str}],
            "min_price": int,
            "max_price": int,
            "avg_price": int,
            "sources_count": int,
            "search_summary": str,
            "price_position": str
        }
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Price search: No API key")
        return _fallback_prices(product_name, user_price)
    
    # 構建搜尋 prompt（簡化版本，減少 token 消耗）
    prompt = f"""搜尋「{product_name}」在台灣電商平台的價格。
    
回覆純 JSON：
{{"prices":[{{"platform":"蝦皮","price":數字}},{{"platform":"PChome","price":數字}},{{"platform":"momo","price":數字}}],"market_insight":"一句話總結"}}

如找不到價格填 0。只回 JSON。"""

    try:
        print(f"📊 Searching market prices for: {product_name}")
        
        # [Fix] Use multiple models with priority
        models = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-flash-latest"]
        response = None
        last_error = ""

        for model in models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                print(f"📊 [PriceSearch] Trying model: {model}...")
                
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.1, "maxOutputTokens": 200}
                }
                
                response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload, timeout=15)
                if response.status_code == 200:
                    break
                else:
                    last_error = f"{model}: {response.status_code}"
            except Exception as e:
                last_error = str(e)

        if not response or response.status_code != 200:
            print(f"❌ Price search failed after all models: {last_error}")
            return _fallback_prices(product_name, user_price)
        
        result = response.json()
        raw_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()
        
        print(f"📊 Price search raw response: {raw_text[:200]}")
        
        # 解析 JSON
        clean_text = raw_text.replace('```json', '').replace('```', '').strip()
        
        # 嘗試提取 JSON
        json_match = re.search(r'\{[\s\S]*\}', clean_text)
        if json_match:
            try:
                data = json.loads(json_match.group())
            except json.JSONDecodeError as e:
                print(f"❌ JSON parse error: {e}")
                return _fallback_prices(product_name, user_price)
        else:
            print("❌ No JSON found in response")
            return _fallback_prices(product_name, user_price)
        
        prices = data.get("prices", [])
        valid_prices = [p for p in prices if p.get("price", 0) > 0]
        
        if not valid_prices:
            print("❌ No valid prices found")
            return _fallback_prices(product_name, user_price)
        
        price_values = [p["price"] for p in valid_prices]
        min_price = min(price_values)
        max_price = max(price_values)
        avg_price = int(sum(price_values) / len(price_values))
        
        # 判斷使用者價格在市場中的位置
        price_position = "符合市場"
        if user_price:
            if user_price < min_price * 0.9:
                price_position = "低於市場"
            elif user_price > max_price * 1.1:
                price_position = "高於市場"
        
        print(f"✅ Price search success: {len(valid_prices)} platforms, ${min_price}-${max_price}")
        
        return {
            "success": True,
            "prices": valid_prices,
            "min_price": min_price,
            "max_price": max_price,
            "avg_price": avg_price,
            "sources_count": len(valid_prices),
            "search_summary": f"根據{len(valid_prices)}個電商平台，市場價格約 ${min_price}-${max_price}",
            "price_position": price_position,
            "market_insight": data.get("market_insight", "")
        }
        
    except requests.Timeout:
        print("❌ Price search timeout")
        return _fallback_prices(product_name, user_price)
    except Exception as e:
        print(f"❌ Price search failed: {e}")
        return _fallback_prices(product_name, user_price)


def _fallback_prices(product_name: str, user_price: float = None) -> dict:
    """
    當搜尋失敗時，使用估算價格
    """
    estimated = user_price if user_price else 500
    
    return {
        "success": False,
        "prices": [],
        "min_price": int(estimated * 0.8),
        "max_price": int(estimated * 1.2),
        "avg_price": int(estimated),
        "sources_count": 0,
        "search_summary": "市場價格資料暫時無法取得",
        "price_position": "未知",
        "market_insight": ""
    }


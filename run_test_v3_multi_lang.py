
import random
import sys
import asyncio
from unittest.mock import MagicMock

# 1. 設置環境與路徑
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app.services.line_bot_service import LineBotService

# 2. 模擬數據
mock_citizens = [
    {"id": i, "name": f"Citizen_{i}", "age": 20+i, "occupation": "Tester", "bazi_profile": {"element": "Fire", "structure": "Tester"}}
    for i in range(15)
]

async def verify_lang(lang):
    print(f"--- 🌐 正在驗證語言: {lang} ---")
    service = LineBotService()
    
    # 模擬 Gemini 返回空數據 (超時情境)
    empty_data = {}
    
    try:
        # 呼叫修復後的數據構建函數
        result = service._build_simulation_result(empty_data, mock_citizens, {"language": lang})
        
        # 驗證 1: 參與市民數
        comment_count = len(result.get("arena_comments", []))
        if comment_count >= 8:
            print(f"✅ [{lang}] 參與市民數量達標: {comment_count}")
        else:
            print(f"❌ [{lang}] 參與市民數量不足: {comment_count}")
            return False
            
        # 驗證 2: 語言一致性 (簡易檢查)
        first_comment = result["arena_comments"][0]["text"]
        print(f"📝 範例評論: {first_comment[:50]}...")
        
        if lang == "en":
            # 英文版應該包含英文單字
            keywords = ["product", "design", "price", "consider", "features", "quality"]
            if any(k in first_comment.lower() for k in keywords):
                print(f"✅ [{lang}] 檢測到英文關鍵字")
            else:
                print(f"❌ [{lang}] 未檢測到英文，Fallback 可能失效: {first_comment}")
                return False
        elif lang == "zh-CN":
             keywords = ["产品", "设计", "价格", "考虑", "品质", "体验"]
             if any(k in first_comment for k in keywords):
                print(f"✅ [{lang}] 檢測到簡體關鍵字")
             else:
                print(f"❌ [{lang}] 未檢測到簡體關鍵字: {first_comment}")
                return False
        else:
            keywords = ["產品", "設計", "價格", "考慮", "品質", "體驗"]
            if any(k in first_comment for k in keywords):
                print(f"✅ [{lang}] 檢測到繁體關鍵字")
            else:
                print(f"❌ [{lang}] 未檢測到繁體關鍵字: {first_comment}")
                return False
                
        return True
    except Exception as e:
        print(f"❌ [{lang}] 發生異常: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    langs = ["zh-TW", "zh-CN", "en"]
    results = []
    for lang in langs:
        res = await verify_lang(lang)
        results.append(res)
        
    if all(results):
        print("\n🎉 三語言 PDF Fallback 邏輯驗證全部通通通過！")
        sys.exit(0)
    else:
        print("\n❌ 驗證失敗，請檢查邏輯。")
        sys.exit(1)

if __name__ == "__main__":
    # 設置必要環境變量
    os.environ["GOOGLE_API_KEY"] = "mock"
    os.environ["LINE_CHANNEL_ACCESS_TOKEN"] = "mock"
    os.environ["LINE_CHANNEL_SECRET"] = "mock"
    asyncio.run(main())

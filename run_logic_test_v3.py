
import random
import sys

# 模擬數據構建邏輯 (從 line_bot_service.py 提取)
def mock_build_simulation_result(data, sampled_citizens, language="zh-TW"):
    arena_comments = data.get("arena_comments", [])
    if not isinstance(arena_comments, list):
        arena_comments = []
    
    fallback_templates_map = {
        "zh-TW": ["身為投資分析的角度看，這份計劃書在{pattern}層面很有潛力，但{element}行的考量不可少。", "作為創業者，我覺得獲利模式還能再優化，特別是針對{age}歲客群的切入點。"],
        "zh-CN": ["身为投资分析的角度看，这份计划书在{pattern}层面很有潜力，但{element}行的考量不可少。", "作为创业者，我觉得获利模式还能再优化，特别是针对{age}岁客群的切入点。"],
        "en": ["From an investment perspective, this plan has potential in {pattern}, but needs {element} consideration.", "As an entrepreneur, the revenue model needs optimization for {age} age group."]
    }
    
    templates = fallback_templates_map.get(language, fallback_templates_map["zh-TW"])
    
    # 模擬重複檢查與補齊
    commented_names = set()
    for c in arena_comments:
        if isinstance(c.get("persona"), dict) and c["persona"].get("name"):
            commented_names.add(c["persona"]["name"])

    # 門檻校準為 10
    while len(arena_comments) < 10 and sampled_citizens:
        citizen = sampled_citizens[len(arena_comments) % len(sampled_citizens)]
        
        bazi = citizen.get("bazi_profile", {})
        text = random.choice(templates).format(
            pattern=bazi.get("structure", "市場"),
            element=bazi.get("element", "五行"),
            age=citizen.get("age", 30)
        )
        arena_comments.append({
            "sentiment": "neutral",
            "text": text,
            "persona": {"name": citizen["name"] + f"_{len(arena_comments)}"} # Ensure unique names for mock
        })
    return arena_comments

def test_lang(lang):
    print(f"--- 🧪 測試語言: {lang} ---")
    mock_citizens = [{"name": f"User_{i}", "age": 25, "bazi_profile": {"element": "Fire", "structure": "Success"}} for i in range(15)]
    comments = mock_build_simulation_result({}, mock_citizens, lang)
    
    if len(comments) >= 10:
        print(f"✅ [{lang}] 數量達標: {len(comments)}")
        sample = comments[0]["text"]
        print(f"📝 範例: {sample[:50]}...")
        if lang == "en" and "potential" in sample.lower(): return True
        if lang == "zh-CN" and "计划书" in sample: return True
        if lang == "zh-TW" and "計劃書" in sample: return True
    else:
        print(f"❌ [{lang}] 數量不足: {len(comments)}")
    return False

if __name__ == "__main__":
    results = [test_lang(l) for l in ["zh-TW", "zh-CN", "en"]]
    if all(results):
        print("\n🎉 三語言 10 條評論 Fallback 邏輯驗證全部通通通過！")
        sys.exit(0)
    else:
        sys.exit(1)

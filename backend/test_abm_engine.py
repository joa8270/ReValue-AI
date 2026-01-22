"""
ABM Engine 快速測試腳本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.abm_engine import ABMSimulation, STRUCTURE_DECISION_PROFILE
import random

print("=" * 60)
print("🧬 MIRRA ABM Engine 快速測試")
print("=" * 60)

# 1. 生成測試用市民資料
test_citizens = []
structures = list(STRUCTURE_DECISION_PROFILE.keys())
elements = ["Fire", "Water", "Metal", "Wood", "Earth"]

for i in range(30):
    test_citizens.append({
        "id": str(i + 1),
        "name": f"測試市民{i+1}",
        "age": 25 + random.randint(0, 30),
        "occupation": random.choice(["工程師", "設計師", "老師", "醫生", "創業家"]),
        "location": "台北, 台灣",
        "bazi_profile": {
            "element": random.choice(elements),
            "structure": random.choice(structures),
            "current_luck": {
                "name": "正財運",
                "description": "財運旺盛，適合投資"
            },
            "four_pillars": "甲子 乙丑 丙寅 丁卯",
            "day_master": "甲木"
        },
        "traits": ["理性", "務實"]
    })

print(f"✅ 已生成 {len(test_citizens)} 位測試市民\n")

# 2. 設定產品資訊
product_info = {
    "element": "Fire",  # 假設是電子產品（屬火）
    "price": 500,       # 售價
    "market_price": 450 # 市價
}

print("📦 測試產品:")
print(f"   五行屬性: {product_info['element']}")
print(f"   售價: ${product_info['price']}")
print(f"   市價: ${product_info['market_price']}")
print(f"   價格比: {product_info['price']/product_info['market_price']:.2f}x\n")

# 3. 初始化ABM模擬
print("🚀 初始化ABM模擬...")
sim = ABMSimulation(test_citizens, product_info)

# 4. 構建社交網絡
print("\n📡 構建五行相性網絡...")
sim.build_social_network("element_based")

# 5. 計算初始意見
print("\n💭 計算初始意見...")
sim.initialize_opinions()

# 6. 執行多輪互動
print("\n🔄 執行意見演化（5輪互動）...")
sim.run_iterations(num_iterations=5, convergence_rate=0.3)

# 7. 識別意見領袖
print("\n👑 識別意見領袖...")
sim.identify_opinion_leaders(top_n=3)

# 8. 分析突現行為
print("\n📊 突現行為分析：")
emergence = sim.analyze_emergence()
print("=" * 60)
for key, value in emergence.items():
    if isinstance(value, dict):
        print(f"  {key}:")
        for k, v in value.items():
            print(f"    {k}: {v:.2f}")
    else:
        print(f"  {key}: {value:.3f}" if isinstance(value, float) else f"  {key}: {value}")

# 9. 獲取代表性評論
print("\n💬 代表性市民（10位）：")
print("=" * 60)
comments = sim.get_final_comments(num_comments=10)
for i, c in enumerate(comments, 1):
    print(f"{i}. {c['name']} ({c['element']}行, {c['structure']})")
    print(f"   初始意見: {c['abm_context']['initial_opinion']:.1f} → 最終意見: {c['opinion_score']:.1f}")
    print(f"   變化: {c['opinion_change']:+.1f} 分")
    print(f"   情緒: {c['sentiment']}")
    if c['is_leader']:
        print(f"   ⭐ 意見領袖（影響了 {c['influenced_count']} 人）")
    print()

print("=" * 60)
print("✅ ABM引擎測試完成！")
print("=" * 60)

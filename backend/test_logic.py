
import random

# Mock data
sampled_citizens = [
    {
        "id": "1",
        "name": "TestCitizen",
        "age": 30,
        "bazi_profile": {
            "luck_timeline": None, # Case 1: None
            "luck_pillars": [{"pillar": "甲子", "description": "Desc", "age_start": 10, "age_end": 19}]
        }
    },
    {
        "id": "2",
        "name": "TestCitizen2",
        "age": 30,
        "bazi_profile": {
            "luck_timeline": [], # Case 2: Empty List
            # No luck_pillars
        }
    }
]

def test_logic():
    print("Starting test...")
    for citizen in sampled_citizens:
        bazi = citizen["bazi_profile"]
        
        # LOGIC FROM STEP 441
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
        current_luck = bazi.get("current_luck", {})
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
            
        print(f"Citizen {citizen['name']} processed. Current luck: {current_luck}")

test_logic()

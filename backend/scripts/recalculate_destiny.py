import os
import sys
import random

# 添加父目錄到 path 以便導入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, Citizen

# ===== 術語與邏輯庫 =====
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
TIANGAN_ELEMENT = {"甲": "Wood", "乙": "Wood", "丙": "Fire", "丁": "Fire", "戊": "Earth", "己": "Earth", "庚": "Metal", "辛": "Metal", "壬": "Water", "癸": "Water"}
TIANGAN_POLARITY = {"甲": "Yang", "乙": "Yin", "丙": "Yang", "丁": "Yin", "戊": "Yang", "己": "Yin", "庚": "Yang", "辛": "Yin", "壬": "Yang", "癸": "Yin"}
PRODUCING = {"Wood": "Fire", "Fire": "Earth", "Earth": "Metal", "Metal": "Water", "Water": "Wood"}
CONTROLLING = {"Wood": "Earth", "Earth": "Water", "Water": "Fire", "Fire": "Metal", "Metal": "Wood"}
PRODUCED_BY = {v: k for k, v in PRODUCING.items()}
CONTROLLED_BY = {v: k for k, v in CONTROLLING.items()}

PERSONALITY_CORE = {
    "正官格": ("正官格（守序型人格）", "做事有條理、重視規則，是個值得信賴的人"),
    "七殺格": ("七殺格（挑戰型人格）", "果斷有魄力，不怕挑戰，遇到困難反而越戰越勇"),
    "正財格": ("正財格（務實型人格）", "務實穩重，理財觀念佳，喜歡腳踏實地累積財富"),
    "偏財格": ("偏財格（機會型人格）", "個性豪爽、人緣好，對賺錢很有sense，常有意外收穫"),
    "正印格": ("正印格（學習型人格）", "溫和有智慧，重視學習與精神層面，容易得到貴人相助"),
    "偏印格": ("偏印格（獨創型人格）", "思考獨特、有個人風格，適合走與眾不同的路"),
    "食神格": ("食神格（享樂型人格）", "樂觀隨和，懂生活、會享受，有藝術或美感天賦"),
    "傷官格": ("傷官格（才華型人格）", "聰明有才華，不喜歡被約束，敢說敢做有個性"),
    "建祿格": ("建祿格（自力型人格）", "獨立自主，靠自己打拼，有堅強的意志力"),
    "羊刃格": ("羊刃格（衝鋒型人格）", "性格直率、行動力強，適合需要衝勁的工作"),
    "從財格": ("從財格（順勢型人格）", "懂得順勢而為，對金錢機會很敏銳"),
    "從殺格": ("從殺格（企圖型人格）", "有強烈的企圖心，適合在大組織發展"),
    "從兒格": ("從兒格（創意型人格）", "靠創意與才華吃飯，追求自由與成就感"),
    "專旺格": ("專旺格（專業型人格）", "個性鮮明、堅持己見，在專業領域容易出頭")
}

LIFE_PHASE_NOW = {
    "Bi Jian": ("比肩運（人脈期）", "近期身邊朋友給力，團隊合作順利，是積累人脈的好時機"),
    "Jie Cai": ("劫財運（競爭期）", "最近生活節奏快、壓力不小，但野心和行動力都很強"),
    "Shi Shen": ("食神運（享受期）", "目前狀態輕鬆愉快，重視生活品質，才華容易被看見"),
    "Shang Guan": ("傷官運（突破期）", "正處於想要突破 and 改變的階段，可能會做出大膽決定"),
    "Zheng Cai": ("正財運（收穫期）", "努力開始有回報了，財運穩定，投資眼光不錯"),
    "PiAn Cai": ("偏財運（機會期）", "最近財運旺，商業嗅覺敏銳，容易遇到賺錢機會"),
    "Zheng Guan": ("正官運（升遷期）", "事業正在上升期，受到重用和認可，責任也變重了"),
    "Qi Sha": ("七殺運（挑戰期）", "面臨不小的挑戰 and 競爭，但突破後會有大進展"),
    "Zheng Yin": ("正印運（學習期）", "有貴人運，適合學習進修，或享受穩定安逸的生活"),
    "PiAn Yin": ("偏印運（沉澱期）", "思考模式在轉變，適合沉澱自己、規劃下一步")
}

# ===== 繁簡映射庫 (手動映射核心術語) =====
CN_MAPPING = {
    "正官格": "正官格", "七殺格": "七杀格", "正財格": "正财格", "偏財格": "偏财格",
    "正印格": "正印格", "偏印格": "偏印格", "食神格": "食神格", "傷官格": "伤官格",
    "建祿格": "建禄格", "羊刃格": "羊刃格", "從財格": "从财格", "從殺格": "从杀格",
    "從兒格": "从儿格", "專旺格": "专旺格", "身強": "身强", "身弱": "身弱",
    "比肩運": "比肩运", "劫財運": "劫财运", "食神運": "食神运", "傷官運": "伤官运",
    "正財運": "正财运", "偏財運": "偏财运", "正官運": "正官运", "七殺運": "七杀运",
    "正印運": "正印运", "偏印運": "偏印运", "金": "金", "木": "木", "水": "水", "火": "火", "土": "土"
}

def t_cn(text: str) -> str:
    """極簡繁轉簡（針對核心術語與常用字）"""
    res = text
    for k, v in CN_MAPPING.items():
        res = res.replace(k, v)
    # 常用字補丁
    res = res.replace("個", "个").replace("條", "条").replace("則", "则").replace("務", "务").replace("適", "适")
    res = res.replace("隨", "随").replace("處", "处").replace("對", "对").replace("賺", "赚").replace("與", "与")
    res = res.replace("學", "学").replace("應", "应").replace("導", "导").replace("創", "创").replace("進", "进")
    res = res.replace("業", "业").replace("認", "认").replace("變", "变")
    res = res.replace("級", "级").replace("專", "专").replace("現", "现").replace("點", "点")
    res = res.replace("樣", "样").replace("為", "为").replace("會", "会").replace("實", "实").replace("覺", "觉")
    res = res.replace("熱", "热").replace("樂", "乐").replace("觀", "观").replace("藝", "艺").replace("術", "术")
    res = res.replace("韌", "韧").replace("強", "强").replace("衝", "冲").replace("鋒", "锋")
    return res

def get_ten_god(me: str, target: str) -> str:
    my_elem = TIANGAN_ELEMENT[me]
    target_elem = TIANGAN_ELEMENT[target]
    is_same_pol = TIANGAN_POLARITY[me] == TIANGAN_POLARITY[target]
    if my_elem == target_elem: return "Bi Jian" if is_same_pol else "Jie Cai"
    if PRODUCED_BY[my_elem] == target_elem: return "PiAn Yin" if is_same_pol else "Zheng Yin"
    if PRODUCING[my_elem] == target_elem: return "Shi Shen" if is_same_pol else "Shang Guan"
    if CONTROLLED_BY[my_elem] == target_elem: return "Qi Sha" if is_same_pol else "Zheng Guan"
    if CONTROLLING[my_elem] == target_elem: return "PiAn Cai" if is_same_pol else "Zheng Cai"
    return "Unknown"

def get_dayun_sequence(gender, year_gan, m_gan_idx, m_zhi_idx, day_master):
    direction = 1 if (TIANGAN_POLARITY[year_gan]=="Yang") == (gender=="男") else -1
    start_age, pillars = random.randint(2, 9), []
    cur_g, cur_z = m_gan_idx, m_zhi_idx
    for i in range(8):
        cur_g, cur_z = (cur_g + direction) % 10, (cur_z + direction) % 12
        gan = TIANGAN[cur_g]
        ten_god = get_ten_god(day_master, gan)
        luck_term, luck_desc = LIFE_PHASE_NOW.get(ten_god, ("平穩運", "平穩過渡"))
        
        tw_desc = f"{luck_term}：{luck_desc}"
        cn_desc = t_cn(tw_desc)
        
        pillars.append({
            "pillar": TIANGAN[cur_g]+DIZHI[cur_z], 
            "gan": TIANGAN[cur_g], 
            "age_start": start_age+(i*10), 
            "age_end": start_age+(i*10)+9,
            "description": tw_desc,
            "localized_description": {
                "TW": tw_desc,
                "CN": cn_desc,
                "US": f"Luck Cycle of {ten_god}"
            },
            "ten_god": ten_god
        })
    return pillars

def generate_colloquial_state(age, gender, p):
    current_luck = None
    for luck in p["luck_pillars"]:
        if luck["age_start"] <= age <= luck["age_end"]:
            current_luck = luck
            break
    if not current_luck: current_luck = p["luck_pillars"][0]
    
    pattern_term, pattern_desc = PERSONALITY_CORE.get(p["structure"], ("多元格局", "個性多元，很有自己的想法"))
    ten_god = get_ten_god(p["day_master"][0], current_luck["gan"])
    luck_term, luck_desc = LIFE_PHASE_NOW.get(ten_god, ("平穩運", "目前生活平穩，順其自然"))
    
    pronoun_tw = "她" if gender == "女" else "他"
    tw_state = f"{pattern_term}：{pattern_desc}。{pronoun_tw}目前行{luck_term}，{luck_desc}。"
    
    cn_state = t_cn(tw_state)
    
    return {
        "TW": tw_state,
        "CN": cn_state,
        "US": "Strategic decision making based on Bazi structure."
    }

def get_favorable_elements(structure_name, strength, my_element):
    child, wealth, officer, mother, friend = PRODUCING[my_element], CONTROLLING[my_element], CONTROLLED_BY[my_element], PRODUCED_BY[my_element], my_element
    is_normal = structure_name in ["正官格", "七殺格", "正財格", "偏財格", "正印格", "偏印格", "食神格", "傷官格"]
    if structure_name in ["建祿格", "羊刃格"]: fav, unfav = [mother, friend, child], [wealth, officer]
    elif is_normal:
        if strength == "身弱": fav, unfav = [mother, friend], [officer, child, wealth]
        else: fav, unfav = [officer, child, wealth], [mother, friend]
    else: fav, unfav = [child, wealth], [mother, officer]
    return {"favorable": list(set(fav)), "unfavorable": list(set(unfav))}

def recalculate_destiny():
    db = SessionLocal()
    try:
        citizens = db.query(Citizen).all()
        print(f"🧬 Operation Destiny Refresh (Multi-Language): Starting for {len(citizens)} citizens...")
        fixed_count = 0
        
        for c in citizens:
            p = c.bazi_profile
            y = p.get("birth_year")
            m = p.get("birth_month")
            d = p.get("birth_day")
            
            if not (y and m and d): continue
            
            # 1. 重建基礎 Pillars
            y_gan_idx, y_zhi_idx = (y - 4) % 10, (y - 4) % 12
            m_gan_idx, m_zhi_idx = (y_gan_idx * 2 + m) % 10, (m + 1) % 12
            d_gan_idx, d_zhi_idx = random.randint(0, 9), random.randint(0, 11)
            
            shichen_branch = p.get("shichen_branch") or "子"
            h_zhi_idx = DIZHI.index(shichen_branch)
            h_gan_idx = (d_gan_idx * 2 + h_zhi_idx) % 10
            
            dm = TIANGAN[d_gan_idx]
            bz = {
                "year_pillar": TIANGAN[y_gan_idx] + DIZHI[y_zhi_idx],
                "month_pillar": TIANGAN[m_gan_idx] + DIZHI[m_zhi_idx],
                "day_pillar": TIANGAN[d_gan_idx] + DIZHI[d_zhi_idx],
                "hour_pillar": TIANGAN[h_gan_idx] + DIZHI[h_zhi_idx],
                "day_master": dm + ["木","木","火","火","土","土","金","金","水","水"][d_gan_idx],
                "element": TIANGAN_ELEMENT[dm],
                "year_gan": TIANGAN[y_gan_idx],
                "month_gan_idx": m_gan_idx,
                "month_zhi_idx": m_zhi_idx
            }
            
            # 2. 重建大運
            struct_name = p.get("structure") or random.choice(list(PERSONALITY_CORE.keys()))
            strength = p.get("strength") or random.choice(["身強", "身弱"])
            luck = get_dayun_sequence(c.gender, bz["year_gan"], bz["month_gan_idx"], bz["month_zhi_idx"], dm)
            
            luck_timeline = []
            current_luck_obj = {}
            for l in luck:
                p_name = l['pillar'] + "運"
                luck_item = {
                    "age_start": l['age_start'],
                    "age_end": l['age_end'],
                    "name": p_name,
                    "pillar": l['pillar'],
                    "description": l['description'],
                    "localized_description": l['localized_description']
                }
                luck_timeline.append(luck_item)
                
                if l['age_start'] <= c.age <= l['age_end']:
                    current_luck_obj = luck_item
            
            if not current_luck_obj and luck_timeline:
                current_luck_obj = luck_timeline[0]
            
            # 3. 生成當前狀態
            temp_p = {"day_master": bz["day_master"], "structure": struct_name, "luck_pillars": luck}
            localized_state = generate_colloquial_state(c.age, c.gender, temp_p)
            
            # 4. 更新 bazi_profile (使用 .copy() 以確保 SQLAlchemy 標記修改)
            new_p = p.copy()
            new_p.update({
                **bz,
                "four_pillars": f"{bz['year_pillar']} {bz['month_pillar']} {bz['day_pillar']} {bz['hour_pillar']}",
                "luck_pillars": luck,
                "luck_timeline": luck_timeline,
                "current_luck": current_luck_obj,
                "current_state": localized_state["TW"],
                "localized_state": localized_state,
                "favorable_elements": get_favorable_elements(struct_name, strength, bz["element"])["favorable"],
                "unfavorable_elements": get_favorable_elements(struct_name, strength, bz["element"])["unfavorable"]
            })
            
            c.bazi_profile = new_p # 重新賦值觸發 update
            fixed_count += 1
            
            if c.id == 9720:
                print(f"✅ ID 9720 (邱俊杰) Locale Data Injected:")
                print(f"   CN State: {localized_state['CN']}")
                print(f"   CN Luck: {current_luck_obj['localized_description']['CN']}")
        
        db.commit()
        print(f"🎉 Destiny Refresh complete: {fixed_count} souls revived with multi-language support.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Operation Failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    recalculate_destiny()

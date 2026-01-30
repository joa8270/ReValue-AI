"""
MIRRA Genesis Final - Strict Regional Data Generation
Generates 1000 citizens:
- 340 TW (Traditional Chinese, Taiwan Cities)
- 330 US (English, US Cities)
- 330 CN (Simplified Chinese, China Cities)
"""
import os
import sys
import json
import random
import datetime
from faker import Faker

# Add backend to path for imports if needed, but we will keep this self-contained for "Final" stability
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Initialize Fakers
fake_tw = Faker('zh_TW')
fake_cn = Faker('zh_CN')
fake_us = Faker('en_US')

# ===== Shared Data & Logic (Adapted from create_citizens.py) =====
# Reusing the core Bazi logic to ensure consistency

LOCATIONS_TW = ["台北, 台灣", "新北, 台灣", "桃園, 台灣", "台中, 台灣", "高雄, 台灣", "台南, 台灣", "新竹, 台灣"]
LOCATIONS_CN = ["北京, 中國", "上海, 中國", "廣州, 中國", "深圳, 中國", "成都, 中國", "杭州, 中國", "武漢, 中國"]
LOCATIONS_US = ["New York, USA", "Los Angeles, USA", "Chicago, USA", "Houston, USA", "San Francisco, USA", "Seattle, USA", "Boston, USA"]

SHICHEN = [
    {"name": "子時", "hours": (23, 1), "branch": "子"}, {"name": "丑時", "hours": (1, 3), "branch": "丑"},
    {"name": "寅時", "hours": (3, 5), "branch": "寅"}, {"name": "卯時", "hours": (5, 7), "branch": "卯"},
    {"name": "辰時", "hours": (7, 9), "branch": "辰"}, {"name": "巳時", "hours": (9, 11), "branch": "巳"},
    {"name": "午時", "hours": (11, 13), "branch": "午"}, {"name": "未時", "hours": (13, 15), "branch": "未"},
    {"name": "申時", "hours": (15, 17), "branch": "申"}, {"name": "酉時", "hours": (17, 19), "branch": "酉"},
    {"name": "戌時", "hours": (19, 21), "branch": "戌"}, {"name": "亥時", "hours": (21, 23), "branch": "亥"},
]

TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
TIANGAN_ELEMENT = {"甲": "Wood", "乙": "Wood", "丙": "Fire", "丁": "Fire", "戊": "Earth", "己": "Earth", "庚": "Metal", "辛": "Metal", "壬": "Water", "癸": "Water"}
TIANGAN_POLARITY = {"甲": "Yang", "乙": "Yin", "丙": "Yang", "丁": "Yin", "戊": "Yang", "己": "Yin", "庚": "Yang", "辛": "Yin", "壬": "Yang", "癸": "Yin"}
PRODUCING = {"Wood": "Fire", "Fire": "Earth", "Earth": "Metal", "Metal": "Water", "Water": "Wood"}
CONTROLLING = {"Wood": "Earth", "Earth": "Water", "Water": "Fire", "Fire": "Metal", "Metal": "Wood"}
PRODUCED_BY = {v: k for k, v in PRODUCING.items()}
CONTROLLED_BY = {v: k for k, v in CONTROLLING.items()}

STRUCTURES = [
    {"name": "正官格", "type": "Normal", "trait": "正直守法，重視名譽"},
    {"name": "七殺格", "type": "Normal", "trait": "威權果斷，富冒險精神"},
    {"name": "正財格", "type": "Normal", "trait": "勤儉務實，重視穩定收入"},
    {"name": "偏財格", "type": "Normal", "trait": "豪爽大方，善於交際"},
    {"name": "正印格", "type": "Normal", "trait": "仁慈聰慧，重精神層面"},
    {"name": "偏印格", "type": "Normal", "trait": "機智敏銳，特立獨行"},
    {"name": "食神格", "type": "Normal", "trait": "溫和樂觀，重視享受"},
    {"name": "傷官格", "type": "Normal", "trait": "才華洋溢，傲氣叛逆"},
    {"name": "建祿格", "type": "Normal", "trait": "白手起家，獨立自主"},
    {"name": "羊刃格", "type": "Normal", "trait": "性情剛烈，衝動急躁"},
    {"name": "從財格", "type": "Cong", "trait": "識時務者，隨波逐流"},
    {"name": "從殺格", "type": "Cong", "trait": "依附權威，追求權力"},
    {"name": "從兒格", "type": "Cong", "trait": "聰明絕頂，追求自由"},
    {"name": "專旺格", "type": "Dominant", "trait": "個性極強，堅持己見"},
]

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
    "Shang Guan": ("傷官運（突破期）", "正處於想要突破和改變的階段，可能會做出大膽決定"),
    "Zheng Cai": ("正財運（收穫期）", "努力開始有回報了，財運穩定，投資眼光不錯"),
    "PiAn Cai": ("偏財運（機會期）", "最近財運旺，商業嗅覺敏銳，容易遇到賺錢機會"),
    "Zheng Guan": ("正官運（升遷期）", "事業正在上升期，受到重用和認可，責任也變重了"),
    "Qi Sha": ("七殺運（挑戰期）", "面臨不小的挑戰和競爭，但突破後會有大進展"),
    "Zheng Yin": ("正印運（學習期）", "有貴人運，適合學習進修，或享受穩定安逸的生活"),
    "PiAn Yin": ("偏印運（沉澱期）", "思考模式在轉變，適合沉澱自己、規劃下一步")
}

def t_cn(text: str) -> str:
    # Simple conversion mapping for core terms
    mapping = {
        "正官格": "正官格", "七殺格": "七杀格", "正財格": "正财格", "偏財格": "偏财格",
        "正印格": "正印格", "偏印格": "偏印格", "食神格": "食神格", "傷官格": "伤官格",
        "建祿格": "建禄格", "羊刃格": "羊刃格", "從財格": "从财格", "從殺格": "从杀格",
        "從兒格": "从儿格", "專旺格": "专旺格", "身強": "身强", "身弱": "身弱",
        "運": "运", "期": "期", "人脈": "人脉", "競爭": "竞争", "收穫": "收获", "機會": "机会",
        "升遷": "升迁", "挑戰": "挑战", "學習": "学习", "沉澱": "沉淀"
    }
    for k, v in mapping.items():
        text = text.replace(k, v)
    return text

def get_ten_god(me, target):
    my_elem = TIANGAN_ELEMENT[me]
    target_elem = TIANGAN_ELEMENT[target]
    is_same_pol = TIANGAN_POLARITY[me] == TIANGAN_POLARITY[target]
    
    if my_elem == target_elem: return "Bi Jian" if is_same_pol else "Jie Cai"
    if PRODUCED_BY[my_elem] == target_elem: return "PiAn Yin" if is_same_pol else "Zheng Yin"
    if PRODUCING[my_elem] == target_elem: return "Shi Shen" if is_same_pol else "Shang Guan"
    if CONTROLLED_BY[my_elem] == target_elem: return "Qi Sha" if is_same_pol else "Zheng Guan"
    if CONTROLLING[my_elem] == target_elem: return "PiAn Cai" if is_same_pol else "Zheng Cai"
    return "Unknown"

def generate_birthdate(age):
    current_year = 2026
    birth_year = current_year - age
    birth_month = random.randint(1, 12)
    max_day = 28 if birth_month == 2 else 30
    birth_day = random.randint(1, max_day)
    shichen = random.choice(SHICHEN)
    hour = random.randint(shichen["hours"][0], shichen["hours"][1]-1) if shichen["hours"][0] < shichen["hours"][1] else 0
    return {"year": birth_year, "month": birth_month, "day": birth_day, "hour": hour, "shichen": shichen["name"], "shichen_branch": shichen["branch"]}

def calculate_bazi_pillars(bd):
    y_idx = (bd["year"] - 4) % 10
    y_zhi_idx = (bd["year"] - 4) % 12
    m_gan_idx = (y_idx * 2 + bd["month"]) % 10
    m_zhi_idx = (bd["month"] + 1) % 12
    d_gan_idx = random.randint(0, 9)
    d_zhi_idx = random.randint(0, 11)
    
    # Calculate Hour Gan
    h_zhi_idx = DIZHI.index(bd["shichen_branch"])
    h_gan_idx = (d_gan_idx * 2 + h_zhi_idx) % 10
    
    return {
        "year_pillar": TIANGAN[y_idx] + DIZHI[y_zhi_idx],
        "year_gan": TIANGAN[y_idx],
        "month_pillar": TIANGAN[m_gan_idx] + DIZHI[m_zhi_idx],
        "month_gan_idx": m_gan_idx,
        "month_zhi_idx": m_zhi_idx,
        "day_pillar": TIANGAN[d_gan_idx] + DIZHI[d_zhi_idx],
        "day_master": TIANGAN[d_gan_idx], # Just the Stem
        "hour_pillar": TIANGAN[h_gan_idx] + DIZHI[h_zhi_idx],
        "element": TIANGAN_ELEMENT[TIANGAN[d_gan_idx]]
    }

def get_dayun_sequence(gender, year_gan, m_gan_idx, m_zhi_idx, day_master):
    is_yang_year = TIANGAN_POLARITY[year_gan] == "Yang"
    is_male = (gender == "Male") # Normalized gender check
    direction = 1 if (is_yang_year and is_male) or (not is_yang_year and not is_male) else -1
    
    start_age = random.randint(2, 9)
    pillars = []
    
    cur_g, cur_z = m_gan_idx, m_zhi_idx
    
    for i in range(8):
        cur_g = (cur_g + direction) % 10
        cur_z = (cur_z + direction) % 12
        pillar = TIANGAN[cur_g] + DIZHI[cur_z]
        
        ten_god = get_ten_god(day_master, TIANGAN[cur_g])
        term, desc = LIFE_PHASE_NOW.get(ten_god, ("平穩運", "平穩過渡"))
        
        pillars.append({
            "pillar": pillar,
            "gan": TIANGAN[cur_g],
            "age_start": start_age + (i * 10),
            "age_end": start_age + (i * 10) + 9,
            "description": f"{term}：{desc}",
            "ten_god": ten_god
        })
    return pillars

def get_job(region):
    if region == 'TW':
        return random.choice(["工程師", "產品經理", "行銷專員", "教師", "公務員", "設計師", "業務", "會計師"])
    if region == 'CN':
        return random.choice(["算法工程师", "产品经理", "运营专员", "教师", "公务员", "UI设计师", "销售经理", "财务主管"])
    # US
    return random.choice(["Software Engineer", "Product Manager", "Marketing Specialist", "Teacher", "Civil Servant", "Designer", "Sales Rep", "Accountant"])

# ===== Generator Function =====

def generate_citizen_for_region(region, idx):
    # 1. Basic Info
    gender_code = random.choice(['M', 'F'])
    age = random.randint(18, 65)
    
    if region == 'TW':
        fake = fake_tw
        name = fake.name() # Traditional
        location = random.choice(LOCATIONS_TW)
        gender = "男" if gender_code == 'M' else "女"
    elif region == 'CN':
        fake = fake_cn
        name = fake.name() # Simplified
        location = random.choice(LOCATIONS_CN)
        gender = "男" if gender_code == 'M' else "女"
    else: # US
        fake = fake_us
        name = fake.name_male() if gender_code == 'M' else fake.name_female()
        location = random.choice(LOCATIONS_US)
        gender = "Male" if gender_code == 'M' else "Female"

    # 2. Bazi Calc
    bd = generate_birthdate(age)
    bz = calculate_bazi_pillars(bd)
    struct = random.choice(STRUCTURES)
    
    # Normalize gender for Dayun calc (Male/Female)
    calc_gender = "Male" if gender_code == 'M' else "Female"
    luck_seq = get_dayun_sequence(calc_gender, bz["year_gan"], bz["month_gan_idx"], bz["month_zhi_idx"], bz["day_master"])
    
    # 3. Construct Luck Timeline (Localized)
    luck_timeline = []
    current_luck = None
    
    for l in luck_seq:
        # Create Localized Descriptions
        desc_tw = l['description']
        desc_cn = t_cn(desc_tw)
        desc_us = f"Luck Cycle: {l['ten_god']} ({l['age_start']}-{l['age_end']})"
        
        item = {
            "age_start": l['age_start'],
            "age_end": l['age_end'],
            "pillar": l['pillar'],
            "description": desc_tw, # Legacy support
            "localized_description": {
                "TW": desc_tw,
                "CN": desc_cn,
                "US": desc_us
            }
        }
        luck_timeline.append(item)
        if l['age_start'] <= age <= l['age_end']:
            current_luck = item
            
    if not current_luck: current_luck = luck_timeline[0]

    # 4. Generate Current State Text (Localized)
    term, desc = PERSONALITY_CORE.get(struct["name"], ("多元格局", "個性多元"))
    pronoun = "She" if gender_code == 'F' else "He"
    state_tw = f"{term}：{desc}。"
    state_cn = t_cn(state_tw)
    state_us = f"Personality: {struct['name']} type. {pronoun} is currently in {current_luck['localized_description']['US']}."

    # 5. Assemble Object
    return {
        "id": str(idx),
        "region": region, # CRITICAL FOR FILTERING
        "name": name,
        "gender": gender,
        "age": age,
        "location": location,
        "occupation": get_job(region), # Now a STRING based on region
        "bazi_profile": {
            **bz,
            "structure": struct["name"],
            "strength": "Balanced", # Simplified
            "luck_timeline": luck_timeline,
            "current_luck": current_luck,
            "current_state": state_tw,
            "localized_state": {
                "TW": state_tw,
                "CN": state_cn,
                "US": state_us
            }
        },
        "traits": [struct["type"]] # Simplified
    }

def main():
    print(f"Generating 1000 Citizens with Strict Regional Config...")
    citizens = []
    
    # Generate 340 TW
    for i in range(340):
        citizens.append(generate_citizen_for_region('TW', len(citizens) + 1))
        
    # Generate 330 CN
    for i in range(330):
        citizens.append(generate_citizen_for_region('CN', len(citizens) + 1))
        
    # Generate 330 US
    for i in range(330):
        citizens.append(generate_citizen_for_region('US', len(citizens) + 1))
        
    print(f"Total Generated: {len(citizens)}")
    
    # Write JSON
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "citizens.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    data = {
        "meta": {"generated_at": datetime.datetime.now().isoformat(), "version": "final_strict"},
        "citizens": citizens,
        "total": len(citizens)
    }
    
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    main()

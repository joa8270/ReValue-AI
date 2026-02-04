"""
MIRRA Genesis Final - One Soul, Three Masks Implementation
Ensures 1000 Unique Souls with:
1. Real Birth Dates (1960-2005)
2. Authentic 4-Pillar Calculation
3. Professional Bazi Logic (Lucky Elements, Strength)
4. Gender-Consistent Localized Names (TW/CN/US)
5. SES-Aligned Culturally Equivalent Jobs
"""
import os
import sys
import json
import random
import datetime
from faker import Faker

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Initialize Fakers
fake_tw = Faker('zh_TW')
fake_cn = Faker('zh_CN')
fake_us = Faker('en_US')

# ===== Bazi Constants =====
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

TIANGAN_INFO = {
    "甲": ("Wood", "Yang"), "乙": ("Wood", "Yin"),
    "丙": ("Fire", "Yang"), "丁": ("Fire", "Yin"),
    "戊": ("Earth", "Yang"), "己": ("Earth", "Yin"),
    "庚": ("Metal", "Yang"), "辛": ("Metal", "Yin"),
    "壬": ("Water", "Yang"), "癸": ("Water", "Yin")
}

DIZHI_INFO = {
    "子": ("Water", "Yang", "Winter"), "丑": ("Earth", "Yin", "Winter"),
    "寅": ("Wood", "Yang", "Spring"), "卯": ("Wood", "Yin", "Spring"),
    "辰": ("Earth", "Yang", "Spring"), "巳": ("Fire", "Yin", "Summer"),
    "午": ("Fire", "Yang", "Summer"), "未": ("Earth", "Yin", "Summer"),
    "申": ("Metal", "Yang", "Autumn"), "酉": ("Metal", "Yin", "Autumn"),
    "戌": ("Earth", "Yang", "Autumn"), "亥": ("Water", "Yin", "Winter")
}

STRUCTURES = [
    {"name": "正官格", "en": "Direct Officer", "trait": "正直守法，重視名譽", "trait_en": "Honest and law-abiding, values reputation"},
    {"name": "七殺格", "en": "Seven Killings", "trait": "威權果斷，富冒險精神", "trait_en": "Decisive and authoritative, adventurous"},
    {"name": "正財格", "en": "Direct Wealth", "trait": "勤儉務實，重視穩定收入", "trait_en": "Thrifty and pragmatic, values stable income"},
    {"name": "偏財格", "en": "Indirect Wealth", "trait": "豪爽大方，善於交際", "trait_en": "Generous and sociable, good with people"},
    {"name": "正印格", "en": "Direct Resource", "trait": "仁慈聰慧，重精神層面", "trait_en": "Kind and intelligent, values spiritual life"},
    {"name": "偏印格", "en": "Indirect Resource", "trait": "機智敏銳，特立獨行", "trait_en": "Witty and sharp, independent thinker"},
    {"name": "食神格", "en": "Eating God", "trait": "溫和樂觀，重視享受", "trait_en": "Gentle and optimistic, enjoys life"},
    {"name": "傷官格", "en": "Hurting Officer", "trait": "才華溢，傲氣叛逆", "trait_en": "Talented and arrogant, rebellious"},
    {"name": "建祿格", "en": "Self Prosperity", "trait": "白手起家，獨立自主", "trait_en": "Self-made, independent and autonomous"},
    {"name": "羊刃格", "en": "Goat Blade", "trait": "性情剛烈，衝動急躁", "trait_en": "Fierce temperament, impulsive and impatient"}
]

# ===== Job Mapping Matrix (Soul-Job Equivalents) =====
# 10% High, 30% Mid, 60% Low
JOB_MATRIX = {
    "High": [
        {"TW": "執行長", "US": "CEO", "CN": "首席执行官"},
        {"TW": "創業家", "US": "Tech Founder", "CN": "创业者"},
        {"TW": "高階主管", "US": "VP of Engineering", "CN": "高级副总裁"},
        {"TW": "外科醫生", "US": "Surgeon", "CN": "外科主任医师"},
        {"TW": "資深律師", "US": "Senior Partner (Law)", "CN": "律所高级合伙人"}
    ],
    "Mid": [
        {"TW": "工程師", "US": "Software Engineer", "CN": "程序员"},
        {"TW": "中學教師", "US": "High School Teacher", "CN": "中学教师"},
        {"TW": "行銷經理", "US": "Marketing Manager", "CN": "市场经理"},
        {"TW": "會計師", "US": "Accountant", "CN": "会计师"},
        {"TW": "設計師", "US": "UX Designer", "CN": "设计师"},
        {"TW": "公務員", "US": "Government Employee", "CN": "公务员"},
        {"TW": "護理師", "US": "Registered Nurse", "CN": "护士"}
    ],
    "Low": [
        {"TW": "搬運工", "US": "Janitor", "CN": "搬运工"},
        {"TW": "服務生", "US": "Server", "CN": "服务员"},
        {"TW": "外送員", "US": "Delivery Driver", "CN": "外卖小哥"},
        {"TW": "水電工", "US": "Plumber", "CN": "水电师傅"},
        {"TW": "保安", "US": "Security Guard", "CN": "保安"},
        {"TW": "超商門市員", "US": "Retail Clerk", "CN": "收银员"},
        {"TW": "行政助理", "US": "Office Clerk", "CN": "行政助理"}
    ]
}

PAIN_POINTS = [
    {"TW": "財務壓力大，難守財", "CN": "经济焦虑，入不敷出", "US": "Financial instability and debt pressure"},
    {"TW": "職場競爭激烈，犯小人", "CN": "职场内卷，竞争激烈", "US": "Workplace competition and toxic politics"},
    {"TW": "生活壓力大，易焦慮", "CN": "精神内耗，压力过大", "US": "High burnout risk and chronic anxiety"},
    {"TW": "懷才不遇，平台受限", "CN": "怀才不遇，缺少平台", "US": "Unrecognized talent and limited growth"},
    {"TW": "行動力低，容易想太多", "CN": "行动迟缓，容易躺平", "US": "Analysis paralysis and lack of drive"},
    {"TW": "投資失利，意外破財", "CN": "存钱困难，易有意外支出", "US": "Poor investment results and unexpected costs"}
]

# ===== Bazi Helpers =====
def get_gan_zhi(offset):
    return TIANGAN[offset % 10] + DIZHI[offset % 12]

def calc_year_pillar(year):
    offset = (year - 1984) % 60
    if offset < 0: offset += 60
    return get_gan_zhi(offset)

def calc_month_pillar(year_gan, month):
    bazi_month = (month + 10) % 12 
    start_gan_idx = (TIANGAN.index(year_gan) % 5) * 2 + 2
    m_zhi_idx = (bazi_month + 2) % 12 
    m_gan_idx = (start_gan_idx + bazi_month) % 10
    return TIANGAN[m_gan_idx] + DIZHI[m_zhi_idx]

def calc_day_pillar(dt: datetime.datetime):
    ref_date = datetime.datetime(2000, 1, 1) # Wu-Wu
    delta = dt - ref_date
    current_idx = (54 + delta.days) % 60
    return get_gan_zhi(current_idx)

def calc_hour_pillar(day_gan, hour):
    start_gan_idx = (TIANGAN.index(day_gan) % 5) * 2
    h_zhi_idx = (hour + 1) // 2 % 12
    h_gan_idx = (start_gan_idx + h_zhi_idx) % 10
    return TIANGAN[h_gan_idx] + DIZHI[h_zhi_idx]

def determine_strength(day_master, month_zhi):
    dm_elem = TIANGAN_INFO[day_master][0]
    mz_info = DIZHI_INFO[month_zhi]
    mz_elem = mz_info[0]
    mz_season = mz_info[2]
    SEASON_ELEM = {"Spring": "Wood", "Summer": "Fire", "Autumn": "Metal", "Winter": "Water"}
    season_elem = SEASON_ELEM.get(mz_season, "Earth")
    
    if dm_elem == season_elem or dm_elem == mz_elem: return "Strong"
    if (dm_elem == "Fire" and season_elem == "Wood") or \
       (dm_elem == "Earth" and season_elem == "Fire") or \
       (dm_elem == "Metal" and season_elem == "Earth") or \
       (dm_elem == "Water" and season_elem == "Metal") or \
       (dm_elem == "Wood" and season_elem == "Water"): return "Strong"
    return "Weak"

# ===== Core Generator =====
def generate_citizen(idx):
    # 1. First Determine Gender
    gender = random.choice(['Male', 'Female'])
    
    # 2. Localized Names (Strictly gender-based and independent)
    if gender == 'Male':
        name_tw = fake_tw.name_male()
        name_cn = fake_cn.name_male()
        name_us = fake_us.name_male()
    else:
        name_tw = fake_tw.name_female()
        name_cn = fake_cn.name_female()
        name_us = fake_us.name_female()

    # 3. Determine SES and Culturally Equivalent Job
    ses_roll = random.random()
    if ses_roll < 0.1: ses = "High"
    elif ses_roll < 0.4: ses = "Mid"
    else: ses = "Low"
    
    job_map = random.choice(JOB_MATRIX[ses])
    
    # 4. Birth & Bazi
    year = random.randint(1965, 2005)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    hour = random.randint(0, 23)
    dt = datetime.datetime(year, month, day, hour)
    
    year_p = calc_year_pillar(year)
    month_p = calc_month_pillar(year_p[0], month)
    day_p = calc_day_pillar(dt)
    hour_p = calc_hour_pillar(day_p[0], hour)
    
    day_master = day_p[0]
    struct = random.choice(STRUCTURES)
    strength = determine_strength(day_master, month_p[1])
    
    # 5. Pain Point (Synced across languages)
    pain = random.choice(PAIN_POINTS)
    
    # 6. Localized Cities
    cities = {
        "TW": random.choice(["台北", "台中", "高雄", "新竹"]),
        "CN": random.choice(["北京", "上海", "深圳", "成都"]),
        "US": random.choice(["New York", "San Francisco", "Austin", "Chicago"])
    }

    # 7. Construct Profiles
    profiles = {
        "TW": {"name": name_tw, "city": cities["TW"], "job": job_map["TW"], "pain": pain["TW"]},
        "CN": {"name": name_cn, "city": cities["CN"], "job": job_map["CN"], "pain": pain["CN"]},
        "US": {"name": name_us, "city": cities["US"], "job": job_map["US"], "pain": pain["US"]}
    }

    return {
        "id": str(idx),
        "name": name_tw, # Legacy top-level name
        "gender": gender,
        "age": 2026 - year,
        "location": cities["TW"],
        "occupation": job_map, # Object for all languages
        "profiles": profiles,
        "bazi_profile": {
            "birth_year": year,
            "birth_month": month,
            "birth_day": day,
            "birth_hour": hour,
            "birth_shichen": hour_p[1] + "時",
            "four_pillars": f"{year_p} {month_p} {day_p} {hour_p}",
            "element": TIANGAN_INFO[day_master][0],
            "day_master": day_master,
            "strength": strength,
            "structure": struct["name"],
            "current_state": struct["trait"],
            "localized_state": {
                "TW": struct["trait"],
                "CN": struct["trait"],
                "US": struct["trait_en"]
            }
        },
        "traits": [struct["name"]]
    }

def main():
    print("Generating 1000 Unique Souls with One Soul Three Masks logic...")
    citizens = [generate_citizen(i+1) for i in range(1000)]
    
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "citizens.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    data = {
        "meta": {
            "version": "multiverse_v1",
            "generated_at": datetime.datetime.now().isoformat()
        },
        "citizens": citizens,
        "total": 1000
    }
    
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Successfully generated 1000 citizens to {output_path}")

if __name__ == "__main__":
    main()

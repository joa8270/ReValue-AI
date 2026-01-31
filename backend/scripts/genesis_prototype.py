
import json
import random
import os
import sys
from datetime import datetime

# Add backend directory to sys.path to allow imports if needed
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# ==========================================
# CONFIGURATION
# ==========================================
TOTAL_CITIZENS = 10
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "citizens_v6.json")
OUTPUT_FILE_LEGACY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "citizens.json")

# ==========================================
# BAZI LOGIC
# ==========================================
HEAVENLY_STEMS = ["jia", "yi", "bing", "ding", "wu", "ji", "geng", "xin", "ren", "gui"]
EARTHLY_BRANCHES = ["zi", "chou", "yin", "mao", "chen", "si", "wu", "wei", "shen", "you", "xu", "hai"]

def calculate_luck(gender, year_stem_idx, month_stem_idx, month_branch_idx):
    """
    Calculate 8 Luck Pillars (80 years).
    
    Rules:
    - Yang Year (Year Stem Index even): Male Forward (+), Female Backward (-)
    - Yin Year (Year Stem Index odd): Male Backward (-), Female Forward (+)
    """
    # 1. Determine Direction
    is_yang_year = (year_stem_idx % 2 == 0)
    
    if gender == "Male":
        direction = 1 if is_yang_year else -1
    else: # Female
        direction = -1 if is_yang_year else 1
        
    luck_pillars = []
    
    # Generate 8 steps (80 years)
    # Start from Month Pillar, but Luck Pillars are the *next* sequences
    # i ranges from 1 to 8
    for i in range(1, 9):
        s_idx = (month_stem_idx + (i * direction)) % 10
        b_idx = (month_branch_idx + (i * direction)) % 12
        
        stem = HEAVENLY_STEMS[s_idx]
        branch = EARTHLY_BRANCHES[b_idx]
        luck_pillars.append(f"{stem}-{branch}")
        
    return luck_pillars

def calculate_bazi(year, month, day, hour):
    # Year Pillar
    year_stem_idx = (year - 4) % 10
    year_branch_idx = (year - 4) % 12
    year_pillar = f"{HEAVENLY_STEMS[year_stem_idx]}-{EARTHLY_BRANCHES[year_branch_idx]}"
    
    # Month Pillar (Simplified)
    month_start_lookup = {0: 2, 5: 2, 1: 4, 6: 4, 2: 6, 7: 6, 3: 8, 8: 8, 4: 0, 9: 0}
    month_stem_start = month_start_lookup[year_stem_idx]
    month_branch_idx = (month + 1) % 12
    month_stem_idx = (month_stem_start + (month - 1)) % 10
    month_pillar = f"{HEAVENLY_STEMS[month_stem_idx]}-{EARTHLY_BRANCHES[month_branch_idx]}"
    
    # Day Pillar (Simplified Simulation)
    base_date = datetime(1900, 1, 1)
    target_date = datetime(year, month, day)
    delta_days = (target_date - base_date).days
    day_stem_idx = (0 + delta_days) % 10
    day_branch_idx = (10 + delta_days) % 12
    day_pillar = f"{HEAVENLY_STEMS[day_stem_idx]}-{EARTHLY_BRANCHES[day_branch_idx]}"
    
    # Hour Pillar
    hour_start_lookup = {0: 0, 5: 0, 1: 2, 6: 2, 2: 4, 7: 4, 3: 6, 8: 6, 4: 8, 9: 8}
    hour_stem_start = hour_start_lookup[day_stem_idx]
    
    hour_branch_idx = 0
    if hour >= 23 or hour < 1: hour_branch_idx = 0 # Zi
    elif hour < 3: hour_branch_idx = 1 # Chou
    elif hour < 5: hour_branch_idx = 2 # Yin
    else: hour_branch_idx = (hour + 1) // 2 % 12
    
    steps_from_zi = hour_branch_idx
    hour_stem_idx = (hour_stem_start + steps_from_zi) % 10
    hour_pillar = f"{HEAVENLY_STEMS[hour_stem_idx]}-{EARTHLY_BRANCHES[hour_branch_idx]}"

    # Element Mapping (Day Master)
    stem_elements = {
        "jia": "Wood", "yi": "Wood", 
        "bing": "Fire", "ding": "Fire", 
        "wu": "Earth", "ji": "Earth", 
        "geng": "Metal", "xin": "Metal", 
        "ren": "Water", "gui": "Water"
    }
    
    day_master_stem = HEAVENLY_STEMS[day_stem_idx]
    element = stem_elements[day_master_stem]
    
    return {
        "year": year_pillar,
        "month": month_pillar,
        "day": day_pillar,
        "hour": hour_pillar,
        "day_master": day_master_stem,
        "element": element,
        "four_pillars": f"{year_pillar} {month_pillar} {day_pillar} {hour_pillar}",
        # Internal indices for Luck Cycle Calc
        "_indices": {
            "year_stem": year_stem_idx,
            "month_stem": month_stem_idx,
            "month_branch": month_branch_idx
        }
    }

# ==========================================
# DATA & LOOKUP
# ==========================================
NAMES_TW = {
    "surnames": ["陳", "林", "黃", "張", "李", "王", "吳", "劉", "蔡", "楊"],
    "given_m": ["志豪", "俊傑", "建宏", "家豪", "冠宇"],
    "given_f": ["怡君", "雅婷", "雅雯", "心怡", "詩涵"]
}
NAMES_US = {
    "Male": ["James", "John", "Robert", "Michael", "William"],
    "Female": ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth"],
    "Surnames": ["Smith", "Johnson", "Williams", "Brown", "Jones"]
}
NAMES_CN = {
    "surnames": ["陈", "林", "黄", "张", "李", "王", "吴", "刘", "蔡", "杨"],
    "given_m": ["志豪", "俊杰", "建宏", "家豪", "冠宇"],
    "given_f": ["怡君", "雅婷", "雅雯", "心怡", "诗涵"]
}

# SES Distribution for 10 people: 1 High, 4 Mid, 5 Low
SES_POOLS = [
    # High (1)
    {"level": "High", "jobs": {"TW": "執行長", "US": "CEO", "CN": "首席执行官"}, "income": "High"},
    # Mid (4)
    {"level": "Mid", "jobs": {"TW": "專案經理", "US": "Project Manager", "CN": "项目经理"}, "income": "Mid"},
    {"level": "Mid", "jobs": {"TW": "資深工程師", "US": "Senior Engineer", "CN": "资深工程师"}, "income": "Mid"},
    {"level": "Mid", "jobs": {"TW": "會計師", "US": "Accountant", "CN": "会计师"}, "income": "Mid"},
    {"level": "Mid", "jobs": {"TW": "行銷經理", "US": "Marketing Manager", "CN": "营销经理"}, "income": "Mid"},
    # Low (5)
    {"level": "Low", "jobs": {"TW": "大學生", "US": "Student", "CN": "大学生"}, "income": "Low"},
    {"level": "Low", "jobs": {"TW": "行政助理", "US": "Admin Assistant", "CN": "行政助理"}, "income": "Low"},
    {"level": "Low", "jobs": {"TW": "初級業務", "US": "Junior Sales", "CN": "初级销售"}, "income": "Low"},
    {"level": "Low", "jobs": {"TW": "服務生", "US": "Server", "CN": "服务员"}, "income": "Low"},
    {"level": "Low", "jobs": {"TW": "外送員", "US": "Delivery Driver", "CN": "外卖员"}, "income": "Low"},
]

BAZI_STRUCTURES = ["正官格", "七殺格", "正財格", "偏財格", "正印格", "偏印格", "食神格", "傷官格", "建祿格", "羊刃格"]

# ==========================================
# GENERATION LOGIC
# ==========================================
def generate_prototype():
    citizens = []
    
    # Shuffle SES pool to distribute randomly among the 10 citizens
    random.shuffle(SES_POOLS)
    
    current_year = 2026

    for i in range(TOTAL_CITIZENS):
        cid = f"{i+1:04d}"
        
        # 1. Demographics
        gender = random.choice(["Male", "Female"])
        age = random.randint(18, 65)
        
        # Birth Date Calculation
        birth_year = current_year - age
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)
        birth_hour = random.randint(0, 23)
        
        # 2. Bazi Calculation
        bazi = calculate_bazi(birth_year, birth_month, birth_day, birth_hour)
        bazi["structure"] = random.choice(BAZI_STRUCTURES)
        bazi["strength"] = random.choice(["身強", "身弱", "中和"])
        
        # 3. Calculate Luck Pillars & Current Luck
        # Extract indices needed for luck calc
        year_stem_idx = bazi["_indices"]["year_stem"]
        month_stem_idx = bazi["_indices"]["month_stem"]
        month_branch_idx = bazi["_indices"]["month_branch"]
        
        # Remove internal indices before saving
        del bazi["_indices"]
        
        # Calculate full 8 steps
        luck_pillars = calculate_luck(gender, year_stem_idx, month_stem_idx, month_branch_idx)
        bazi["luck_pillars"] = luck_pillars
        
        # Determine Current Luck (Age // 10)
        step_index = age // 10
        if 0 <= step_index < len(luck_pillars):
            current_luck = luck_pillars[step_index]
        else:
            # Fallback if age is out of range (e.g., > 80 or < 0, though range is 18-65)
            # 18 // 10 = 1 (2nd pillar)
            # 65 // 10 = 6 (7th pillar)
            # So it should be fine.
            current_luck = luck_pillars[-1] if step_index >= len(luck_pillars) else luck_pillars[0]
            
        bazi["current_luck"] = current_luck
        
        # 4. Names
        # TW
        sn_tw = random.choice(NAMES_TW["surnames"])
        gn_tw = random.choice(NAMES_TW["given_m"] if gender == "Male" else NAMES_TW["given_f"])
        name_tw = f"{sn_tw}{gn_tw}"
        
        # US
        gn_us = random.choice(NAMES_US[gender])
        sn_us = random.choice(NAMES_US["Surnames"])
        name_us = f"{gn_us} {sn_us}"
        
        # CN
        sn_cn = random.choice(NAMES_CN["surnames"])
        gn_cn = random.choice(NAMES_CN["given_m"] if gender == "Male" else NAMES_CN["given_f"])
        name_cn = f"{sn_cn}{gn_cn}"
        
        # 5. SES & Job
        ses = SES_POOLS[i]
        
        citizen = {
            "id": i + 1,
            "meta": {"version": "v1.1", "generator": "prototype_v2_luck"},
            "name": {
                "TW": name_tw,
                "US": name_us,
                "CN": name_cn
            },
            "gender": gender,
            "age": age,
            "location": "TBD",
            "occupation": ses["jobs"],
            "bazi_profile": bazi,
            "traits": [bazi["element"], bazi["structure"], ses["level"]],
            "profiles": {
                "TW": {"name": name_tw, "city": "Taipei", "job": ses["jobs"]["TW"]},
                "US": {"name": name_us, "city": "New York", "job": ses["jobs"]["US"]},
                "CN": {"name": name_cn, "city": "Shanghai", "job": ses["jobs"]["CN"]}
            }
        }
        citizens.append(citizen)

    # Save to file (V6)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(citizens, f, ensure_ascii=False, indent=2)
        
    # Save to file (Legacy)
    with open(OUTPUT_FILE_LEGACY, "w", encoding="utf-8") as f:
        json.dump(citizens, f, ensure_ascii=False, indent=2)
    
    print(f">> Generated {len(citizens)} citizens with Luck Pillars")
    print(f"   - {OUTPUT_FILE}")
    print(f"   - {OUTPUT_FILE_LEGACY}")

if __name__ == "__main__":
    generate_prototype()

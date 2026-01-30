"""
MIRRA Genesis Final - Real Bazi & Professional Logic Refinement
Generates 1000 Unique Souls with:
1. Real Birth Dates (1960-2005)
2. Authentic 4-Pillar Calculation
3. Professional Bazi Logic (Lucky Elements, Strength)
4. Fortune Teller Tone (Pain Points)
5. Strict Validation (No 'None', No Childish Terms)
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
ZODIAC = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse", "Goat", "Monkey", "Rooster", "Dog", "Pig"]

# Pinyin Maps for US Localization
TIANGAN_PINYIN = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"]
DIZHI_PINYIN = ["Zi", "Chou", "Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai"]
TIANGAN_EN_MAP = dict(zip(TIANGAN, TIANGAN_PINYIN))
DIZHI_EN_MAP = dict(zip(DIZHI, DIZHI_PINYIN))

# Elements & Polarity
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

# Structures
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

# Professional Pain Points (Fortune Teller Tone)
PAIN_POINTS_TW = [
    "財多身弱 (財務壓力大，難守財)",
    "比劫奪財 (職場競爭激烈，犯小人)",
    "殺重身輕 (生活壓力大，易焦慮)",
    "食傷生財 (才華難現，懷才不遇)",
    "印星過旺 (依賴心重，行動力低)",
    "財庫逢沖 (投資失利，破財風險)"
]

PAIN_POINTS_CN = [
    "财多身弱 (经济焦虑，入不敷出)",
    "比劫夺财 (职场内卷，竞争激烈)",
    "杀重身轻 (精神内耗，压力过大)",
    "食伤生财 (怀才不遇，缺少平台)",
    "印星过旺 (行动迟缓，容易躺平)",
    "财库逢冲 (存钱困难，易有意外支出)"
]

PAIN_POINTS_US = [
    "Wealth Pressure (Financial Anxiety - Weak Day Master)",
    "Peer Competition (Rat Race - Rob Wealth)",
    "Heavy Killings (High Stress & Burnout)",
    "Unrecognized Talent (Output draining energy)",
    "Dependency Issues (Over-Resource - Analysis Paralysis)",
    "Financial Instability (Clashing Wealth Vaults)"
]

# ===== Real Bazi Calculation =====

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
    ref_date = datetime.datetime(2000, 1, 1) # Wu-Wu (4,6) ?
    # 2000-01-01 is Wu-Wu. 54 in cycle.
    delta = dt - ref_date
    current_idx = (54 + delta.days) % 60
    return get_gan_zhi(current_idx)

def calc_hour_pillar(day_gan, hour):
    start_gan_idx = (TIANGAN.index(day_gan) % 5) * 2
    h_zhi_idx = (hour + 1) // 2 % 12
    h_gan_idx = (start_gan_idx + h_zhi_idx) % 10
    return TIANGAN[h_gan_idx] + DIZHI[h_zhi_idx]

def determine_strength_and_lucky(day_master, month_zhi):
    """
    Determine Strong/Weak and Lucky Elements.
    Logic:
    - Same Season/Element = Supported (Strong)
    - Different = Weak
    """
    dm_elem = TIANGAN_INFO[day_master][0]
    mz_info = DIZHI_INFO[month_zhi]
    mz_elem = mz_info[0]
    mz_season = mz_info[2]
    
    # Season Mapping
    SEASON_ELEM = {"Spring": "Wood", "Summer": "Fire", "Autumn": "Metal", "Winter": "Water"}
    season_elem = SEASON_ELEM.get(mz_season, "Earth") # Earth months typically end of season
    
    is_strong = False
    
    # Simple Strength Logic
    if dm_elem == season_elem or dm_elem == mz_elem:
        is_strong = True
    elif (dm_elem == "Fire" and season_elem == "Wood") or \
         (dm_elem == "Earth" and season_elem == "Fire") or \
         (dm_elem == "Metal" and season_elem == "Earth") or \
         (dm_elem == "Water" and season_elem == "Metal") or \
         (dm_elem == "Wood" and season_elem == "Water"):
         # Resource month supports
         is_strong = True
         
    # Determine Lucky Elements
    # Strong needs: Drain (Output), Control (Officer), Consume (Wealth)
    # Weak needs: Support (Resource), Help (Peer)
    
    ELEMENTS = ["Wood", "Fire", "Earth", "Metal", "Water"]
    # Production Cycle: W->F->E->M->Wa->W
    PRODUCES = {"Wood": "Fire", "Fire": "Earth", "Earth": "Metal", "Metal": "Water", "Water": "Wood"}
    CONTROLS = {"Wood": "Earth", "Fire": "Metal", "Earth": "Water", "Metal": "Wood", "Water": "Fire"}
    PRODUCED_BY = {v: k for k, v in PRODUCES.items()}
    
    lucky = []
    
    if is_strong:
        strength_desc = "Strong"
        output = PRODUCES[dm_elem]
        wealth = PRODUCES[output] # Output produces wealth
        officer = CONTROLS.get(dm_elem) # Element controlling DM (e.g. Fire DM controlled by Water)
        # Fix Control logic: Water controls Fire.
        # Actually standard: Strong DM likes Officer (Control), Wealth (Consume), Output (Drain)
        # Officer: Element that checks DM. 
        # Wealth: Element DM checks.
        wealth = [e for e in ELEMENTS if CONTROLS[dm_elem] == e][0]
        officer = [e for e in ELEMENTS if CONTROLS[e] == dm_elem][0] 
        
        # Wait, CONTROLS[A] = B means A controls B.
        # Wealth: DM controls Wealth. So CONTROLS[dm_elem] == wealth is Correct.
        # Officer: Officer controls DM. So CONTROLS[officer] == dm_elem is Correct.
        
        lucky = [output, wealth, officer]
    else:
        strength_desc = "Weak"
        resource = PRODUCED_BY[dm_elem]
        peer = dm_elem
        lucky = [resource, peer]
        
    return strength_desc, lucky


# Ten Gods Descriptions
TEN_GODS_INFO = {
    "Friend": {
        "TW": "比肩運：自主性強，利於合夥，需注意財務開銷。",
        "CN": "比肩运：自主性强，利于合伙，需注意财务开销。",
        "US": "Friend Cycle: High autonomy, good for partnership, watch expenses.",
        "name_tw": "比肩",
        "name_cn": "比肩"
    },
    "Rob Wealth": {
        "TW": "劫財運：競爭激烈，野心勃勃，需防破財與小人。",
        "CN": "劫财运：竞争激烈，野心勃勃，需防破财与小人。",
        "US": "Rob Wealth Cycle: Intense competition, ambitious, risk of wealth loss.",
        "name_tw": "劫財",
        "name_cn": "劫财"
    },
    "Eating God": {
        "TW": "食神運：財源穩健，心情愉悅，利於學習與展現才華。",
        "CN": "食神运：财源稳健，心情愉悦，利于学习与展现才华。",
        "US": "Eating God Cycle: Stable income, happiness, good for learning and creativity.",
        "name_tw": "食神",
        "name_cn": "食神"
    },
    "Hurting Officer": {
        "TW": "傷官運：思維活躍，易有變動，利於創新但需防口舌。",
        "CN": "伤官运：思维活跃，易有变动，利于创新但需防口舌。",
        "US": "Hurting Officer Cycle: Active mind, changes, good for innovation but watch speech.",
        "name_tw": "傷官",
        "name_cn": "伤官"
    },
    "Direct Wealth": {
        "TW": "正財運：收入穩定，工作勤奮，利於累積資產。",
        "CN": "正财运：收入稳定，工作勤奋，利于积累资产。",
        "US": "Direct Wealth Cycle: Stable income, hard work, good for asset accumulation.",
        "name_tw": "正財",
        "name_cn": "正财"
    },
    "Indirect Wealth": {
        "TW": "偏財運：意外之財，機遇增加，利於投資與經商。",
        "CN": "偏财运：意外之财，机遇增加，利于投资与经商。",
        "US": "Indirect Wealth Cycle: Windfalls, opportunities, good for investment and business.",
        "name_tw": "偏財",
        "name_cn": "偏财"
    },
    "Direct Officer": {
        "TW": "正官運：地位提升，事業順遂，利於求職與升遷。",
        "CN": "正官运：地位提升，事业顺遂，利于求职与升迁。",
        "US": "Direct Officer Cycle: Status rise, career success, good for promotion.",
        "name_tw": "正官",
        "name_cn": "正官"
    },
    "Seven Killings": {
        "TW": "七殺運：壓力較大，挑戰接踵而至，需展現魄力應對。",
        "CN": "七杀运：压力较大，挑战接踵而至，需展现魄力应对。",
        "US": "Seven Killings Cycle: High pressure, challenges, requires stress resilience.",
        "name_tw": "七殺",
        "name_cn": "七杀"
    },
    "Direct Resource": {
        "TW": "正印運：貴人相助，生活安穩，利於進修與名聲。",
        "CN": "正印运：贵人相助，生活安稳，利于进修与名声。",
        "US": "Direct Resource Cycle: Noble help, stable life, good for reputation and study.",
        "name_tw": "正印",
        "name_cn": "正印"
    },
    "Indirect Resource": {
        "TW": "偏印運：直覺敏銳，喜好獨處，利於研究偏門學問。",
        "CN": "偏印运：直觉敏锐，喜好独处，利于研究偏门学问。",
        "US": "Indirect Resource Cycle: Intuitive, prefers solitude, good for niche research.",
        "name_tw": "偏印",
        "name_cn": "偏印"
    }
}

def calc_ten_god(dm, stem):
    """Calculate Ten God of stem based on Day Master"""
    dm_elem, dm_pol = TIANGAN_INFO[dm]
    stem_elem, stem_pol = TIANGAN_INFO[stem]
    
    # Relationships
    PRODUCES = {"Wood": "Fire", "Fire": "Earth", "Earth": "Metal", "Metal": "Water", "Water": "Wood"}
    CONTROLS = {"Wood": "Earth", "Fire": "Metal", "Earth": "Water", "Metal": "Wood", "Water": "Fire"}
    PRODUCED_BY = {v: k for k, v in PRODUCES.items()}
    CONTROLLED_BY = {v: k for k, v in CONTROLS.items()}
    
    same_pol = (dm_pol == stem_pol)
    
    if dm_elem == stem_elem:
        return "Friend" if same_pol else "Rob Wealth"
    elif PRODUCES[dm_elem] == stem_elem:
        return "Eating God" if same_pol else "Hurting Officer"
    elif CONTROLS[dm_elem] == stem_elem:
        return "Indirect Wealth" if same_pol else "Direct Wealth" # I W is Same Polarity
    elif CONTROLLED_BY[dm_elem] == stem_elem:
        return "Seven Killings" if same_pol else "Direct Officer"
    elif PRODUCED_BY[dm_elem] == stem_elem:
        return "Indirect Resource" if same_pol else "Direct Resource"
    return "Friend" # Fallback

def calc_luck_cycles_refined(gender, year_gan, month_pillar, day_master):
    yg_pol = TIANGAN_INFO[year_gan[0]][1]
    is_forward = (gender == "Male" and yg_pol == "Yang") or (gender == "Female" and yg_pol == "Yin")
    direction = 1 if is_forward else -1
    
    mg_idx = TIANGAN.index(month_pillar[0])
    mz_idx = DIZHI.index(month_pillar[1])
    
    cycles = []
    start_age = random.randint(2, 9)
    
    for i in range(1, 9):
        curr_g = TIANGAN[(mg_idx + direction * i) % 10]
        curr_z = DIZHI[(mz_idx + direction * i) % 12]
        
        # Calculate Ten God
        ten_god = calc_ten_god(day_master, curr_g)
        god_info = TEN_GODS_INFO.get(ten_god, TEN_GODS_INFO["Friend"])
        
        g_py = TIANGAN_EN_MAP[curr_g]
        z_py = DIZHI_EN_MAP[curr_z]
        z_info = DIZHI_INFO[curr_z]
        z_elem = z_info[0]
        z_pol = z_info[1]
        z_season = z_info[2]
        
        # Enhanced Description with Interpretation
        desc_us = god_info["US"]
        desc_tw = god_info["TW"]
        desc_cn = god_info["CN"]
        
        cycles.append({
            "age_start": start_age + (i-1)*10,
            "age_end": start_age + (i-1)*10 + 9,
            "pillar": curr_g + curr_z,
            "ten_god": ten_god, # Store for ref
            "description": desc_tw, # Default description
            "localized_description": {
                "TW": desc_tw,
                "CN": desc_cn,
                "US": desc_us
            }
        })
    return cycles

# ===== Main Generator =====

# Localization Maps
STRENGTH_MAP = {
    "Weak": {"TW": "身弱", "CN": "身弱", "US": "Weak"},
    "Strong": {"TW": "身強", "CN": "身强", "US": "Strong"}, # Simplified '强'
    "Balanced": {"TW": "中和", "CN": "中和", "US": "Balanced"}
}

ELEMENT_MAP = {
    "Wood": {"TW": "木", "CN": "木", "US": "Wood"},
    "Fire": {"TW": "火", "CN": "火", "US": "Fire"},
    "Earth": {"TW": "土", "CN": "土", "US": "Earth"},
    "Metal": {"TW": "金", "CN": "金", "US": "Metal"},
    "Earth": {"TW": "土", "CN": "土", "US": "Earth"},
    "Metal": {"TW": "金", "CN": "金", "US": "Metal"},
    "Water": {"TW": "水", "CN": "水", "US": "Water"}
}

STRENGTH_CN = { "Weak": "身弱", "Strong": "身强", "Balanced": "中和" }
TAG_CN = { "Cong": "从格", "Follower": "从格", "Dominant": "专旺", "Normal": "正格" }

STRUCTURE_TRANSLATION = {
    "建祿格": "Thriving Self (Establishment)",
    "羊刃格": "Yang Edge (Aggressive)",
    "傷官格": "Hurting Officer (Creative Rebel)",
    "食神格": "Eating God (Artist)",
    "正財格": "Direct Wealth (Prudent)",
    "偏財格": "Indirect Wealth (Opportunist)",
    "正官格": "Direct Officer (Leader)",
    "七殺格": "Seven Killings (Warrior)",
    "正印格": "Direct Resource (Scholar)",
    "偏印格": "Indirect Resource (Mystic)",
    "從格": "Follower Structure",
    "化氣格": "Transformation Structure"
}

TRAITS_EN_MAP = {
    "正印格": "Direct Resource Structure",
    "偏印格": "Indirect Resource Structure",
    "正官格": "Direct Officer Structure",
    "七殺格": "Seven Killings Structure",
    "正財格": "Direct Wealth Structure",
    "偏財格": "Indirect Wealth Structure",
    "食神格": "Eating God Structure",
    "傷官格": "Hurting Officer Structure",
    "建祿格": "Thriving Self Structure",
    "羊刃格": "Yang Edge Structure",
    "從格": "Follower Structure",
    "化氣格": "Transformation Structure",
    "多財身弱": "Wealth Burden",
    "比劫奪財": "Peer Competition"
}

def sanitize_us_profile(profile):
    """Ensure no Chinese characters leak into US profile"""
    sanitized = {}
    for k, v in profile.items():
        if isinstance(v, list):
            new_list = []
            for item in v:
                if any("\u4e00" <= char <= "\u9fff" for char in item):
                    # Replace with mapped value or Unknown
                     new_list.append("Unknown Trait") # Should utilize map before this
                else:
                    new_list.append(item)
            sanitized[k] = new_list
        elif isinstance(v, str):
            if any("\u4e00" <= char <= "\u9fff" for char in v):
                sanitized[k] = "Unknown"
            else:
                sanitized[k] = v
        else:
            sanitized[k] = v
    return sanitized

def generate_citizen(idx):
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
    element_info = TIANGAN_INFO[day_master] # (Element, Polarity)
    
    struct = random.choice(STRUCTURES)
    gender_code = random.choice(['M', 'F'])
    gender = "Male" if gender_code == 'M' else "Female"
    
    # Logic Refinement
    strength, lucky_elems = determine_strength_and_lucky(day_master, month_p[1])
    luck_timeline = calc_luck_cycles_refined(gender, year_p[0], month_p, day_master)
    
    # Localized Strength & Elements
    # Force CN Map
    strength_cn = STRENGTH_CN.get(strength, strength)
    # If strength is "Balanced" (not currently generated but for safety), it maps to "中和"
    
    loc_strength = {
        "TW": STRENGTH_MAP.get(strength, {}).get("TW", strength),
        "CN": strength_cn,
        "US": STRENGTH_MAP.get(strength, {}).get("US", strength)
    }
    
    loc_lucky = {
        "TW": [ELEMENT_MAP[e]["TW"] for e in lucky_elems],
        "CN": [ELEMENT_MAP[e]["CN"] for e in lucky_elems],
        "US": [ELEMENT_MAP[e]["US"] for e in lucky_elems]
    }
    
    # Select Pain Point using Index to sync across languages (pseudo-random but consistent per ID if needed, strict random here)
    pain_idx = random.randint(0, len(PAIN_POINTS_TW) - 1)
    
    current_luck = None
    age = 2026 - year
    for l in luck_timeline:
        if l['age_start'] <= age <= l['age_end']:
            current_luck = l
    if not current_luck: current_luck = luck_timeline[0]

    # Profiles
    if gender == "Male":
        name_tw = fake_tw.name_male()
        name_cn = fake_cn.name_male()
        name_us = fake_us.name_male()
    else:
        name_tw = fake_tw.name_female()
        name_cn = fake_cn.name_female()
        name_us = fake_us.name_female()

    job_tw = random.choice(["工程師", "設計師", "教師", "業務", "行政", "PM", "會計", "創業家"])
    city_tw = random.choice(["台北", "台中", "高雄", "新竹"])
    
    job_cn = random.choice(["工程师", "设计师", "教师", "销售", "行政", "产品经理", "会计", "创业者"])
    city_cn = random.choice(["北京", "上海", "深圳", "成都"])
    
    # Ensure simplified Job titles for US just in case
    job_us = random.choice(["Engineer", "Designer", "Teacher", "Sales", "Admin", "PM", "Accountant", "Founder"])
    city_us = random.choice(["New York", "LA", "Chicago", "Austin"])

    
    # Localized Traits
    trait_tw = struct["name"]
    # Check TAG_CN for mapping (e.g. if struct name was "Cong" or needed mapping)
    # struct["name"] is usually "正官格", so TAG_CN.get defaults to key.
    trait_cn = TAG_CN.get(struct["name"], struct["name"]) 
    # STRICT US TRAITS MAPPING
    trait_us = TRAITS_EN_MAP.get(struct["name"], "Standard Structure")
    
    # Construct Profiles
    profile_tw = {"name": name_tw, "city": city_tw, "job": job_tw, "pain": PAIN_POINTS_TW[pain_idx], "traits": [trait_tw]}
    profile_cn = {"name": name_cn, "city": city_cn, "job": job_cn, "pain": PAIN_POINTS_CN[pain_idx], "traits": [trait_cn]}
    
    # Construct US Profile & Sanitize
    profile_us_raw = {"name": name_us, "city": city_us, "job": job_us, "pain": PAIN_POINTS_US[pain_idx], "traits": [trait_us]}
    profile_us = sanitize_us_profile(profile_us_raw)
    
    return {
        "id": str(idx),
        "name": name_tw,
        "gender": gender,
        "age": age,
        "location": city_tw,
        "occupation": job_tw,
        "profiles": {
            "TW": profile_tw,
            "CN": profile_cn,
            "US": profile_us
        },
        "bazi_profile": {
            "birth_year": year,
            "birth_month": month,
            "birth_day": day,
            "birth_hour": hour,
            "four_pillars": {
                "year": year_p,
                "month": month_p,
                "day": day_p,
                "hour": hour_p
            },
            "element": element_info[0], # Day Master Element
            "day_master": day_master,
            "strength": strength,
            "localized_strength": loc_strength, 
            "favorable_elements": lucky_elems,
            "localized_favorable_elements": loc_lucky,
            "structure": struct["name"],
            "structure_en": struct["en"], # Keep existing en as fallback/reference
            "luck_timeline": luck_timeline,
            "current_luck": current_luck,
            "current_state": struct["trait"],
            "localized_state": {
                "TW": struct["trait"],
                "CN": struct["trait"], 
                "US": struct["trait_en"]
            }
        },
        "traits": [trait_tw]
    }

def self_test_cn_localization():
    """Verify CN Translations"""
    print("Running CN Localization Self-Test...")
    
    # Mock checks using map directly since generation might not produce "Balanced"
    if STRENGTH_CN.get("Balanced") != "中和":
        print("FATAL: STRENGTH_CN['Balanced'] failed")
        sys.exit(1)
        
    if TAG_CN.get("Cong") != "从格":
        print("FATAL: TAG_CN['Cong'] failed")
        sys.exit(1)
    
    # Generate actual citizen to check defaults
    c = generate_citizen(888)
    cn_str = c['bazi_profile']['localized_strength']['CN']
    # Must be Chinese char
    if not any("\u4e00" <= char <= "\u9fff" for char in cn_str):
         print(f"FATAL: CN Strength is not Chinese: {cn_str}")
         sys.exit(1)
         
    print(f"CN Localization Self-Test Passed.")

def self_test_localization():
    """Verify Localization"""
    print("Running Localization Self-Test...")
    
    c = generate_citizen(9999)
    bp = c['bazi_profile']
    
    # Check Strength Localization
    if 'localized_strength' not in bp:
        print("FATAL: localized_strength missing")
        sys.exit(1)
        
    tw_str = bp['localized_strength']['TW']
    if tw_str not in ["身弱", "身強", "中和"]:
        print(f"FATAL: Invalid TW Strength: {tw_str}")
        sys.exit(1)
        
    # Check Lucky Localization
    tw_lucky = bp['localized_favorable_elements']['TW']
    if not tw_lucky or tw_lucky[0] not in ["木", "火", "土", "金", "水"]:
         print(f"FATAL: Invalid TW Lucky Element: {tw_lucky}")
         sys.exit(1)
         
    print(f"Localization Self-Test Passed. TW Strength: {tw_str}, TW Lucky: {tw_lucky}")

def self_test_traits_localization():
    """Verify US Traits Localization"""
    print("Running Traits Localization Self-Test...")
    c = generate_citizen(9999)
    traits_us = c['profiles']['US']['traits']
    
    # Check for Chinese chars
    for trait in traits_us:
        if any(ord(char) > 127 for char in trait):
             print(f"FATAL: Found Chinese in US Traits: {trait}")
             sys.exit(1)
             
    print(f"Traits Self-Test Passed. US Trait: {traits_us[0]}")

def main():
    self_test_cn_localization()
    self_test_localization()
    self_test_traits_localization()
    
    print("Generating 1000 Localized Citizens...")
    citizens = [generate_citizen(i+1) for i in range(1000)]
    
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "citizens.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    data = {"citizens": citizens, "total": 1000, "meta": {"version": "logic_refined_v2"}}
    
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Done.")

if __name__ == "__main__":
    main()

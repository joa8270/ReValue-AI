
import json
import random
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Any

# ==========================================
# MIRRA GENESIS 2.0 (V7) - REALISM EDITION
# ==========================================
# Core Philosophy: One Soul, Three Masks (TW/CN/US)
# Demographics: De-elitized (Pyramid Structure)

# 1. 職業矩陣 (直接內嵌以確保執行)
TIER_DISTRIBUTION = {
    1: 0.02, # 2% Elites
    2: 0.18, # 18% Upper Middle
    3: 0.40, # 40% Lower Middle
    4: 0.30, # 30% Working Class
    5: 0.10  # 10% Precariat
}

JOB_MATRIX = {
    1: [
        {"role": "Executive_Tech", "TW": "科技公司執行長 (CEO)", "CN": "科技公司总裁 (CEO)", "US": "Tech Company CEO"},
        {"role": "Executive_Finance", "TW": "金控副總經理", "CN": "投资银行副总裁", "US": "VP of Investment Banking"},
        {"role": "Investor", "TW": "天使投資人", "CN": "风险投资合伙人", "US": "Venture Capital Partner"},
        {"role": "Owner_Factory", "TW": "傳產集團董事長", "CN": "大型制造集团董事长", "US": "Manufacturing Owner"},
        {"role": "Specialist_Top_Lawyer", "TW": "合夥律師", "CN": "高级合伙人律师", "US": "Senior Law Partner"}
    ],
    2: [
        {"role": "Tech_Senior_Dev", "TW": "資深工程師", "CN": "高级开发工程师", "US": "Senior Developer"},
        {"role": "Tech_Data", "TW": "資料科學家", "CN": "大数据专家", "US": "Data Scientist"},
        {"role": "Manager_Marketing", "TW": "行銷總監", "CN": "营销总监", "US": "Marketing Director"},
        {"role": "Doctor", "TW": "主治醫師", "CN": "主治医师", "US": "Physician"},
        {"role": "Professor", "TW": "大學教授", "CN": "大学教授", "US": "Professor"},
        {"role": "Manager_Product", "TW": "資深產品經理", "CN": "高级产品经理", "US": "Senior Product Manager"},
        {"role": "Engineer_Semi", "TW": "半導體工程師", "CN": "芯片工程师", "US": "Semiconductor Engineer"},
        {"role": "Gov_Official", "TW": "高階公務員", "CN": "处级干部", "US": "Senior Civil Servant"}
    ],
    3: [
        {"role": "Office_Admin", "TW": "行政專員", "CN": "行政专员", "US": "Admin Assistant"},
        {"role": "Sales_Rep", "TW": "業務代表", "CN": "销售代表", "US": "Sales Representative"},
        {"role": "Teacher", "TW": "國中小教師", "CN": "中小学教师", "US": "School Teacher"},
        {"role": "Store_Manager", "TW": "店長", "CN": "店长", "US": "Store Manager"},
        {"role": "Nurse", "TW": "護理師", "CN": "护士", "US": "Registered Nurse"},
        {"role": "Designer", "TW": "設計師", "CN": "设计师", "US": "Graphic Designer"},
        {"role": "Accountant", "TW": "會計", "CN": "会计", "US": "Accountant"},
        {"role": "IT_Support", "TW": "IT 支援", "CN": "IT 运维", "US": "IT Support"},
        {"role": "Small_Biz", "TW": "小吃店老闆", "CN": "个体户店主", "US": "Small Business Owner"}
    ],
    4: [
        {"role": "Service_Food", "TW": "餐廳服務生", "CN": "餐厅服务员", "US": "Food Server"},
        {"role": "Delivery", "TW": "外送員", "CN": "外卖骑手", "US": "Delivery Driver"},
        {"role": "Clerk", "TW": "超商店員", "CN": "便利店员", "US": "Retail Clerk"},
        {"role": "Factory", "TW": "作業員", "CN": "普工", "US": "Factory Worker"},
        {"role": "Construction", "TW": "建築工人", "CN": "建筑工", "US": "Construction Worker"},
        {"role": "Driver", "TW": "司機", "CN": "网约车司机", "US": "Driver"},
        {"role": "Security", "TW": "保全", "CN": "保安", "US": "Security Guard"},
        {"role": "Cleaner", "TW": "清潔工", "CN": "保洁", "US": "Cleaner"},
        {"role": "Mechanic", "TW": "黑手技師", "CN": "汽修工", "US": "Mechanic"}
    ],
    5: [
        {"role": "Unemployed", "TW": "待業中", "CN": "待业", "US": "Unemployed"},
        {"role": "Gig_Worker", "TW": "臨時工", "CN": "日结工", "US": "Day Laborer"},
        {"role": "Student_Poor", "TW": "半工半讀學生", "CN": "贫困学生", "US": "Working Student"},
        {"role": "Retired_Poor", "TW": "退休人士", "CN": "退休老人", "US": "Retired"}
    ]
}

# 2. 姓名庫 (文化轉譯)
SURNAMES = {
    "TW": ["陳", "林", "黃", "張", "李", "王", "吳", "劉", "蔡", "楊"],
    "CN": ["陈", "林", "黄", "张", "李", "王", "吴", "刘", "蔡", "杨"],
    "US": ["Chen", "Lin", "Huang", "Chang", "Lee", "Wang", "Wu", "Liu", "Tsai", "Yang"]
}

NAMES_TW_M = ["志豪", "俊傑", "建宏", "冠宇", "承恩", "柏翰", "家偉", "志明", "文雄", "建志"]
NAMES_TW_F = ["怡君", "雅婷", "雅雯", "心怡", "詩涵", "美玲", "惠君", "郁婷", "佳穎", "淑芬"]

NAMES_CN_M = ["军", "伟", "强", "勇", "杰", "磊", "洋", "建华", "志强", "国强"] # 兩字名為主
NAMES_CN_F = ["敏", "静", "丽", "艳", "芳", "娜", "秀英", "小丽", "丹", "萍"]

NAMES_US_M = ["Michael", "David", "James", "Kevin", "Jason", "Eric", "Brian", "Ryan", "John", "Robert"]
NAMES_US_F = ["Jennifer", "Jessica", "Emily", "Sarah", "Michelle", "Amy", "Lisa", "Ashley", "Mary", "Linda"]


# 3. 八字與常量 (Bazi & Constants)
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# [V7 Update] Translation Maps for Western Understanding
STEM_TRANSLATION = {
    "甲": "Yang Wood", "乙": "Yin Wood", "丙": "Yang Fire", "丁": "Yin Fire",
    "戊": "Yang Earth", "己": "Yin Earth", "庚": "Yang Metal", "辛": "Yin Metal",
    "壬": "Yang Water", "癸": "Yin Water"
}

BRANCH_TRANSLATION = {
    "子": "Rat (Water)", "丑": "Ox (Earth)", "寅": "Tiger (Wood)", "卯": "Rabbit (Wood)",
    "辰": "Dragon (Earth)", "巳": "Snake (Fire)", "午": "Horse (Fire)", "未": "Goat (Earth)",
    "申": "Monkey (Metal)", "酉": "Rooster (Metal)", "戌": "Dog (Earth)", "亥": "Pig (Water)"
}

FIVE_ELEMENTS_MAP = {
    "甲": "Wood", "乙": "Wood", "丙": "Fire", "丁": "Fire", "戊": "Earth",
    "己": "Earth", "庚": "Metal", "辛": "Metal", "壬": "Water", "癸": "Water",
    "子": "Water", "丑": "Earth", "寅": "Wood", "卯": "Wood", "辰": "Earth", "巳": "Fire",
    "午": "Fire", "未": "Earth", "申": "Metal", "酉": "Metal", "戌": "Earth", "亥": "Water"
}

# [V7 Update] Bazi Structure -> Western Archetype Mapping
BAZI_STRUCTURE_MAP = {
    "正官格": {"en": "The Director", "desc": "Disciplined, Responsible, Law-abiding"},
    "七殺格": {"en": "The Warrior", "desc": "Bold, Decisive, Risk-taking"},
    "正財格": {"en": "The Steward", "desc": "Pragmatic, Diligent, Resourceful"},
    "偏財格": {"en": "The Hunter", "desc": "Opportunity-seeking, Generous, Dynamic"},
    "正印格": {"en": "The Sage", "desc": "Wise, Caring, Knowledge-seeking"},
    "偏印格": {"en": "The Mystic", "desc": "Intuitive, Unconventional, Strategic"},
    "食神格": {"en": "The Creator", "desc": "Artistic, Expressive, Enjoying Life"},
    "傷官格": {"en": "The Maverick", "desc": "Rebellious, Innovative, Critical"},
    "建祿格": {"en": "The Builder", "desc": "Self-reliant, Steady, Hardworking"},
    "羊刃格": {"en": "The Commander", "desc": "Intense, Competitive, Unyielding"}
}

BAZI_STRUCTURES = list(BAZI_STRUCTURE_MAP.keys())

class GenesisEngineV7:
    def __init__(self, total=1000):
        self.total = total
        self.counts = {i: 0 for i in range(1, 6)} # Tier counts
        # Calculate target counts
        self.targets = {k: int(total * v) for k, v in TIER_DISTRIBUTION.items()}
        
    def _get_tier(self) -> int:
        # Weighted random selection based on remaining slots
        available_tiers = [t for t in self.targets if self.counts[t] < self.targets[t]]
        if not available_tiers:
            return 3 # Fallback
        
        # Simple weighted choice from available (approximate)
        return random.choice(available_tiers)

    def _get_age_by_tier(self, tier: int) -> int:
        # Tier 5 (Precariat) tends to be very young or very old
        if tier == 5:
            return random.choice([random.randint(18, 25), random.randint(60, 75)])
        # Tier 1 (Elite) needs time to accumulate
        if tier == 1:
            return random.randint(40, 65)
        # General Population
        return random.randint(22, 60)

    def _get_luck_cycle(self, bazi_structure, age):
        # 簡易大運邏輯
        cycles = [
            {"name": "少年運", "desc": "初入社會，學習與摸索期"},
            {"name": "青年運", "desc": "事業衝刺，壓力與機會並存"},
            {"name": "壯年運", "desc": "格局定型，收穫與承擔責任"},
            {"name": "晚年運", "desc": "回歸平穩，重視傳承與健康"}
        ]
        if age < 25: return cycles[0]
        elif age < 40: return cycles[1]
        elif age < 55: return cycles[2]
        else: return cycles[3]

    def _generate_persona_desc(self, tier, age, structure, strength):
        # B方案：預計算性格描述 (Rule-based Persona Injection)
        desc = f"你是一位 {age} 歲的市民，八字格局為{structure}{strength}。"
        
        if tier == 1:
            desc += "身為社會頂層菁英，你擁有極高的視野與資源，思考問題往往從戰略與資本回報切入，對細節不拘小節。"
        elif tier == 2:
            desc += "作為專業中產階級，你重視邏輯與效率，生活富足但仍有向上流動的焦慮，對品質要求高。"
        elif tier == 3:
            desc += "你是社會的中堅力量，生活平穩，追求CP值與實用性，對太過冒險的變革持保留態度。"
        elif tier == 4:
            desc += "身為基層勞動者，你每天為生活奔波，對價格極度敏感，看重產品是否耐用、便宜，討厭華而不實的話術。"
        elif tier == 5:
            desc += "你處於社會邊緣，生活充滿不確定性。你對未來感到迷茫或憤世嫉俗，對商業承諾抱持高度懷疑。"
            
        if "七殺" in structure or "傷官" in structure:
            desc += "你的性格中帶有批判性與叛逆因子，說話直接，不喜歡拐彎抹角。"
        elif "正印" in structure or "食神" in structure:
            desc += "你的性格溫和且富有同理心，喜歡和諧的氛圍，說話比較委婉。"
            
        return desc

    def generate(self, index: int) -> Dict[str, Any]:
        cid = f"{index:04d}"
        seed = int(hashlib.md5(cid.encode()).hexdigest(), 16)
        random.seed(seed)
        
        # 1. Immutable Soul DNA
        tier = self._get_tier()
        self.counts[tier] += 1
        
        gender = random.choice(["Male", "Female"])
        age = self._get_age_by_tier(tier)
        
        element_key = random.choice(list(FIVE_ELEMENTS_MAP.keys())) # Stem/Branch
        element = FIVE_ELEMENTS_MAP[element_key]
        day_master = random.choice(HEAVENLY_STEMS)
        structure = random.choice(BAZI_STRUCTURES)
        strength = random.choice(["身強", "身弱", "中和"])
        
        # 2. Occupation Logic (One Job, Three Masks)
        job_pool = JOB_MATRIX[tier]
        job_data = random.choice(job_pool)
        
        # 3. Name Logic (Cultural Transcreation)
        surname_idx = random.randint(0, 9)
        sn_tw = SURNAMES["TW"][surname_idx]
        sn_cn = SURNAMES["CN"][surname_idx]
        sn_us = SURNAMES["US"][surname_idx]
        
        if gender == "Male":
            gn_tw = random.choice(NAMES_TW_M)
            gn_cn = random.choice(NAMES_CN_M) # Localized
            gn_us = random.choice(NAMES_US_M) # Localized
        else:
            gn_tw = random.choice(NAMES_TW_F)
            gn_cn = random.choice(NAMES_CN_F)
            gn_us = random.choice(NAMES_US_F)
            
        name_tw = f"{sn_tw}{gn_tw}"
        name_cn = f"{sn_cn}{gn_cn}"
        name_us = f"{gn_us} {sn_us}"
        
        # 4. Construct Bazi Profile (Localized)
        luck = self._get_luck_cycle(structure, age)
        element_cn_val = {"Wood": "木", "Fire": "火", "Earth": "土", "Metal": "金", "Water": "水"}[element]
        
        # Get Western mappings
        structure_en = BAZI_STRUCTURE_MAP[structure]["en"]
        structure_desc_en = BAZI_STRUCTURE_MAP[structure]["desc"]
        
        # Generate Favorable Elements (Simplified Logic)
        # Strong -> Needs Output/Wealth/Power (Weaken)
        # Weak -> Needs Resource/Peer (Strengthen)
        # Map: Element -> [Resource, Output, Wealth, Power, Peer]
        # Wood: Water, Fire, Earth, Metal, Wood
        # Fire: Wood, Earth, Metal, Water, Fire
        # Earth: Fire, Metal, Water, Wood, Earth
        # Metal: Earth, Water, Wood, Fire, Metal
        # Water: Metal, Wood, Fire, Earth, Water
        
        elements_cycle = ["Wood", "Fire", "Earth", "Metal", "Water"]
        idx = elements_cycle.index(element)
        resource = elements_cycle[(idx - 1 + 5) % 5]
        peer = element
        output = elements_cycle[(idx + 1) % 5]
        wealth = elements_cycle[(idx + 2) % 5]
        power = elements_cycle[(idx + 3) % 5]
        
        favorable = []
        if strength == "身強":
            favorable = [output, wealth, power]
        else: # 身弱 or 中和 (Default to strengthen)
            favorable = [resource, peer]
            
        # Select 2 random favorable elements
        selected_favorable = random.sample(favorable, min(2, len(favorable)))

        # Generate random Pillars for display (simulated)
        y_stem = random.choice(HEAVENLY_STEMS)
        y_branch = random.choice(EARTHLY_BRANCHES)
        m_stem = random.choice(HEAVENLY_STEMS)
        m_branch = random.choice(EARTHLY_BRANCHES)
        d_stem = day_master
        d_branch = random.choice(EARTHLY_BRANCHES)
        h_stem = random.choice(HEAVENLY_STEMS)
        h_branch = random.choice(EARTHLY_BRANCHES)
        
        pillars_cn = f"{y_stem}{y_branch} {m_stem}{m_branch} {d_stem}{d_branch} {h_stem}{h_branch}"
        pillars_en = f"{STEM_TRANSLATION[y_stem]} {BRANCH_TRANSLATION[y_branch]} | {STEM_TRANSLATION[m_stem]} {BRANCH_TRANSLATION[m_branch]} | {STEM_TRANSLATION[d_stem]} {BRANCH_TRANSLATION[d_branch]} | {STEM_TRANSLATION[h_stem]} {BRANCH_TRANSLATION[h_branch]}"

        bazi_profile = {
            "day_master": day_master,
            "element": element,
            "element_cn": element_cn_val,
            "structure": structure,
            "structure_en": structure_en, 
            "strength": strength,
            "strength_en": "Dominant" if strength == "身強" else "Adaptive" if strength == "身弱" else "Balanced",
            "favorable_elements": selected_favorable, # [New]
            "trait": f"{structure}{strength}，{element_cn_val}行特質明顯",
            "trait_en": structure_en, # [New] Simplified to just the archetype name
            "current_luck": {"name": luck["name"], "description": luck["desc"]},
            "four_pillars": pillars_cn,
            "four_pillars_en": pillars_en, 
            "luck_timeline": [] 
        }
        
        # 5. Final Assembly
        citizen = {
            "id": cid,
            "social_tier": tier, 
            "career_tags": [job_data["role"], f"Tier_{tier}"], 
            "name": {
                "TW": name_tw,
                "US": name_us,
                "CN": name_cn
            },
            "gender": gender,
            "age": age,
            "occupation": {
                "TW": job_data["TW"],
                "US": job_data["US"],
                "CN": job_data["CN"]
            },
            "location": {
                "TW": random.choice(["台北", "台中", "高雄", "新竹"]),
                "US": random.choice(["New York", "San Francisco", "Austin", "Seattle"]),
                "CN": random.choice(["上海", "北京", "深圳", "杭州"])
            },
            "bazi_profile": bazi_profile,
            # Mix both Chinese and English traits for searchability/display
            "traits": [structure, structure_en, f"Tier {tier}"],
            "current_persona_desc": self._generate_persona_desc(tier, age, structure, strength),
            "profiles": {
                "TW": {"name": name_tw, "city": "Taipei", "job": job_data["TW"]},
                "US": {"name": name_us, "city": "New York", "job": job_data["US"]},
                "CN": {"name": name_cn, "city": "Shanghai", "job": job_data["CN"]}
            }
        }
        return citizen

if __name__ == "__main__":
    print(">> Genesis V7 (Realism) Initializing...")
    engine = GenesisEngineV7(1000)
    citizens = []
    for i in range(1, 1001):
        citizens.append(engine.generate(i))
        
    # Analyze Distribution
    tiers = {1:0, 2:0, 3:0, 4:0, 5:0}
    for c in citizens:
        tiers[c["social_tier"]] += 1
        
    print(">> Final Distribution:")
    for t, count in tiers.items():
        print(f"  Tier {t}: {count} ({count/10}%)")
        
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "citizens.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(citizens, f, ensure_ascii=False, indent=2)
    print(f">> Generated 1000 souls at {output_path}")

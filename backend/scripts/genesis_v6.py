
import json
import random
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Any

# ==========================================
# CONSTANTS & LOOKUP TABLES
# ==========================================

HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
FIVE_ELEMENTS_MAP = {
    "甲": "Wood", "乙": "Wood", "丙": "Fire", "丁": "Fire", "戊": "Earth",
    "己": "Earth", "庚": "Metal", "辛": "Metal", "壬": "Water", "癸": "Water",
    "子": "Water", "丑": "Earth", "寅": "Wood", "卯": "Wood", "辰": "Earth", "巳": "Fire",
    "午": "Fire", "未": "Earth", "申": "Metal", "酉": "Metal", "戌": "Earth", "亥": "Water"
}

ELEMENT_CN_MAP = {
    "Wood": "木", "Fire": "火", "Earth": "土", "Metal": "金", "Water": "水"
}

# 職涯邏輯表 (Age-Career Dependency)
# Value mapping: (TW, US, CN)
CAREER_POOLS = {
    "Student": [
        ("大學生", "University Student", "大学生"),
        ("碩士生", "Master's Student", "硕士生"),
        ("實習生", "Intern", "实习生"),
        ("研究助理", "Research Assistant", "研究助理"),
        ("外送兼職", "Gig Worker / Delivery", "外卖兼职"),
        ("天才創業家 (Genius)", "Genius Entrepreneur", "天才创业家")
    ],
    "Junior": [
        ("行銷專員", "Marketing Specialist", "营销专员"),
        ("軟體工程師", "Software Engineer", "软件工程师"),
        ("設計助理", "Design Assistant", "设计助理"),
        ("會計專員", "Accountant", "会计专员"),
        ("行政助理", "Administrative Assistant", "行政助理"),
        ("初級業務", "Junior Sales", "初级业务"),
        ("社群小編", "Social Media Manager", "社群运营"),
        ("基層公務員", "Junior Civil Servant", "基层公务员")
    ],
    "Mid": [
        ("專案經理", "Project Manager", "项目经理"),
        ("資深工程師", "Senior Engineer", "资深工程师"),
        ("行銷組長", "Marketing Lead", "营销主管"),
        ("財務主管", "Finance Manager", "财务主管"),
        ("連鎖店長", "Store Manager", "连锁店长"),
        ("產品經理", "Product Manager", "产品经理"),
        ("資深業務員", "Senior Sales Executive", "资深销售"),
        ("中階公務員", "Mid-level Civil Servant", "中阶公务员")
    ],
    "Senior": [
        ("行銷總監", "Marketing Director", "营销总监"),
        ("技術長 (CTO)", "CTO", "技术总监"),
        ("執行長 (CEO)", "CEO", "首席执行官"),
        ("分公司總經理", "General Manager", "分公司总经理"),
        ("資深顧問", "Senior Consultant", "资深顾问"),
        ("部門主管", "Department Head", "部门主管"),
        ("連續創業家", "Serial Entrepreneur", "连续创业家"),
        ("資深公務體系主管", "Senior Government Official", "资深公务员")
    ],
    "Retired": [
        ("退休教師", "Retired Teacher", "退休教师"),
        ("榮譽顧問", "Honorary Advisor", "荣誉顾问"),
        ("社區志工", "Community Volunteer", "社区志愿者"),
        ("包租公/婆", "Property Investor / Landlord", "房东"),
        ("私人投資人", "Private Investor", "个人投资者"),
        ("慈善基金會經理", "Foundation Manager", "慈善基金经理"),
        ("資深創業導師", "Senior Startup Mentor", "资深创业导师")
    ]
}

# 性格格局
BAZI_STRUCTURES = [
    "正官格", "七殺格", "正財格", "偏財格", "正印格", "偏印格", "食神格", "傷官格", "建祿格", "羊刃格"
]

# 姓名庫 (Localized Names)
NAMES_TW = {
    "surnames": ["陳", "林", "黃", "張", "李", "王", "吳", "劉", "蔡", "楊", "許", "鄭", "謝", "郭", "洪", "曾", "邱", "廖", "賴", "周"],
    "given_m": ["志豪", "俊傑", "建宏", "家豪", "冠宇", "承恩", "柏翰", "彥廷", "家偉", "宗翰", "信宏", "文雄", "志明", "建志", "俊宏"],
    "given_f": ["怡君", "雅婷", "雅雯", "心怡", "詩涵", "美玲", "惠君", "宜蓁", "郁婷", "家妤", "佳穎", "筱涵", "佩珊", "欣怡"]
}

NAMES_US = {
    "Male": [
        "James Chen", "Robert Lin", "John Huang", "Michael Chang", "William Lee", 
        "David Wang", "Richard Wu", "Joseph Liu", "Thomas Tsai", "Christopher Yang",
        "Daniel Hsu", "Matthew Cheng", "Anthony Hsieh", "Mark Kuo", "Donald Hong",
        "Kevin Tseng", "Jason Chiu", "Jeff Liao", "Ryan Lai", "Brian Zhou"
    ],
    "Female": [
        "Mary Chen", "Patricia Lin", "Jennifer Huang", "Linda Chang", "Elizabeth Lee",
        "Barbara Wang", "Susan Wu", "Jessica Liu", "Sarah Tsai", "Karen Yang",
        "Nancy Hsu", "Lisa Cheng", "Betty Hsieh", "Margaret Kuo", "Sandra Hong",
        "Ashley Tseng", "Kimberly Chiu", "Emily Liao", "Donna Lai", "Michelle Zhou"
    ]
}

NAMES_CN = {
    "surnames": ["陈", "林", "黄", "张", "李", "王", "吴", "刘", "蔡", "杨", "许", "郑", "谢", "郭", "洪", "曾", "邱", "廖", "赖", "周"],
    "given_m": ["志豪", "俊杰", "建宏", "家豪", "冠宇", "承恩", "柏翰", "彦廷", "家伟", "宗翰", "信宏", "文雄", "志明", "建志", "俊宏"],
    "given_f": ["怡君", "雅婷", "雅雯", "心怡", "诗涵", "美玲", "惠君", "宜蓁", "郁婷", "家妤", "佳颖", "筱涵", "佩珊", "欣怡"]
}

# ==========================================
# CORE LOGIC MANAGERS
# ==========================================

class QuotaSystem:
    def __init__(self, total=1000):
        self.target = total // 5
        self.counts = {"Wood": 0, "Fire": 0, "Earth": 0, "Metal": 0, "Water": 0}
        self.elements = ["Wood", "Fire", "Earth", "Metal", "Water"]

    def get_element(self) -> str:
        available = [e for e in self.elements if self.counts[e] < self.target]
        if not available:
            return random.choice(self.elements)
        choice = random.choice(available)
        self.counts[choice] += 1
        return choice

class LogicEngine:
    @staticmethod
    def get_job_tuple_by_age(age: int) -> tuple:
        if age <= 22:
            return random.choice(CAREER_POOLS["Student"])
        elif 23 <= age <= 30:
            return random.choice(CAREER_POOLS["Junior"])
        elif 31 <= age <= 45:
            return random.choice(CAREER_POOLS["Mid"])
        elif 46 <= age <= 60:
            return random.choice(CAREER_POOLS["Senior"])
        else:
            return random.choice(CAREER_POOLS["Retired"])

    @staticmethod
    def get_mbti_by_bazi(element: str, structure: str) -> str:
        probs = {"E": 0.5, "N": 0.5, "T": 0.5, "P": 0.5}
        if structure == "七殺格": probs["P"] = 0.8
        elif structure == "正印格": probs["P"] = 0.2
        if element == "Wood": probs["N"] = 0.7
        if element == "Fire": probs["E"] = 0.8
        if element == "Metal": probs["T"] = 0.7
        if element == "Water": probs["N"] = 0.6
        if element == "Earth": probs["S"] = 0.7
        res = ""
        res += "E" if random.random() < probs.get("E", 0.5) else "I"
        res += "N" if random.random() < probs.get("N", 0.5) else "S"
        res += "T" if random.random() < probs.get("T", 0.5) else "F"
        res += "P" if random.random() < probs.get("P", 0.5) else "J"
        return res

# ==========================================
# MAIN GENERATOR
# ==========================================

class GenesisEngineV6:
    def __init__(self, total=1000):
        self.quota = QuotaSystem(total)
        self.logic = LogicEngine()

    def generate(self, index: int) -> Dict[str, Any]:
        cid = f"{index:04d}"
        seed = int(hashlib.md5(cid.encode()).hexdigest(), 16)
        random.seed(seed)
        
        element = self.quota.get_element()
        element_cn = ELEMENT_CN_MAP[element]
        possible_stems = [s for s, e in FIVE_ELEMENTS_MAP.items() if e == element and s in HEAVENLY_STEMS]
        day_master = random.choice(possible_stems)
        
        age = random.randint(18, 75)
        job_tuple = self.logic.get_job_tuple_by_age(age) # (TW, US, CN)
        
        structure = random.choice(BAZI_STRUCTURES)
        strength = random.choice(["身強", "身弱", "中和"])
        mbti = self.logic.get_mbti_by_bazi(element, structure)
        
        gender = random.choice(["Male", "Female"])
        
        # TW Name
        surname_tw = random.choice(NAMES_TW["surnames"])
        given_tw = random.choice(NAMES_TW["given_m"] if gender == "Male" else NAMES_TW["given_f"])
        name_tw = f"{surname_tw}{given_tw}"
        
        # US Name (Full name directly)
        name_us = random.choice(NAMES_US[gender])
        
        # CN Name (Simplified)
        surname_cn = random.choice(NAMES_CN["surnames"])
        given_cn = random.choice(NAMES_CN["given_m"] if gender == "Male" else NAMES_CN["given_f"])
        name_cn = f"{surname_cn}{given_cn}"
        
        element_desc = {
            "Wood": "木主仁，具備成長性與生命力。你的性格中帶有向上與拓展的特質。",
            "Fire": "火主禮，象徵熱情與社交。你具備極強的感染力與行動力。",
            "Earth": "土主信，象徵穩定與誠信。你是團隊中的壓艙石，沉穩且可靠。",
            "Metal": "金主義，象徵果斷與正義。你處事俐落，重視邏輯與秩序。",
            "Water": "水主智，象徵智慧與流動。你思維敏捷，擅長處理複雜的變化。"
        }.get(element)
        
        citizen = {
            "id": cid,
            "name": {
                "TW": name_tw,
                "US": name_us,
                "CN": name_cn
            },
            "gender": gender,
            "age": age,
            "mbti": mbti,
            "occupation": {
                "TW": job_tuple[0],
                "US": job_tuple[1],
                "CN": job_tuple[2]
            },
            "bazi_profile": {
                "day_master": day_master,
                "element": element,
                "element_cn": element_cn,
                "element_desc": element_desc,
                "structure": structure,
                "strength": strength,
                "four_pillars": f"甲子 乙丑 {day_master}寅 丙辰",
                "trait": f"{structure}{strength}，{element_cn}行特質明顯",
                "current_luck": {"age_start": age//10*10, "description": "目前處於大運平穩期"},
                "luck_timeline": []
            },
            "traits": [mbti, f"五行:{element_cn}", structure],
            "profiles": {
                "TW": {
                    "name": name_tw,
                    "city": random.choice(["台北", "台中", "高雄", "新竹"]),
                    "job": job_tuple[0],
                    "cultural_settings": ["重視傳統與家庭"]
                },
                "US": {
                    "name": name_us,
                    "city": random.choice(["New York", "San Francisco", "Austin", "Seattle"]),
                    "job": job_tuple[1],
                    "cultural_settings": ["Value individual freedom and career growth"]
                },
                "CN": {
                    "name": name_cn,
                    "city": random.choice(["上海", "北京", "深圳", "杭州"]),
                    "job": job_tuple[2],
                    "cultural_settings": ["重视效率与集体协作"]
                }
            }
        }
        return citizen

if __name__ == "__main__":
    print("🚀 Operation Rebirth: Genesis V6 (Localized) Started...")
    engine = GenesisEngineV6(1000)
    citizens = []
    for i in range(1, 1001):
        citizens.append(engine.generate(i))
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "citizens_v6.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(citizens, f, ensure_ascii=False, indent=2)
    print(f"✅ Generated 1000 localized souls at {output_path}")

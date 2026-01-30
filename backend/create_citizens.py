"""
MIRRA Genesis Script V5 - 創世紀造人腳本（白話大運版）
生成 1000 位具備完整八字格局、10年大運與「白話解讀」(Current State) 的 AI 虛擬市民
"""
import os
import sys
import random
from datetime import datetime, timedelta

# 添加父目錄到 path 以便導入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# 導入資料庫模組
from app.core.database import SessionLocal, insert_citizens_batch, get_citizens_count, clear_citizens

# ===== 中文姓名庫 =====
SURNAMES = [
    "王", "李", "張", "劉", "陳", "楊", "黃", "趙", "吳", "周",
    "徐", "孫", "馬", "朱", "胡", "郭", "林", "何", "高", "羅",
    "鄭", "梁", "謝", "宋", "唐", "許", "韓", "馮", "鄧", "曹",
    "彭", "曾", "蕭", "田", "董", "潘", "袁", "蔡", "蔣", "余"
]

MALE_NAMES = [
    "偉", "強", "磊", "軍", "勇", "傑", "濤", "明", "鵬", "俊",
    "輝", "剛", "毅", "斌", "峰", "建", "文", "博", "宇", "浩",
    "志", "國", "華", "平", "東", "海", "飛", "雲", "澤", "凱",
    "翔", "龍", "威", "堅", "超", "昊", "睿", "政", "宏", "彥"
]

FEMALE_NAMES = [
    "芳", "麗", "娟", "燕", "敏", "靜", "秀", "玲", "霞", "婷",
    "慧", "穎", "雪", "梅", "蘭", "菊", "雯", "琳", "瑩", "萍",
    "雅", "欣", "夢", "佳", "怡", "淑", "詩", "琪", "嘉", "薇",
    "珊", "莉", "清", "潔", "涵", "蓉", "倩", "瑜", "璇", "妍"
]

# ===== 地理位置 =====
LOCATIONS = {
    "台北, 台灣": 20,
    "新北, 台灣": 15,
    "桃園, 台灣": 10,
    "台中, 台灣": 12,
    "高雄, 台灣": 10,
    "台南, 台灣": 8,
    "新竹, 台灣": 5,
    "嘉義, 台灣": 4,
    "彰化, 台灣": 4,
    "屏東, 台灣": 3,
    "宜蘭, 台灣": 3,
    "花蓮, 台灣": 3,
    "基隆, 台灣": 2,
    "台東, 台灣": 2,
}

# ===== 十二時辰 =====
SHICHEN = [
    {"name": "子時", "hours": (23, 1), "branch": "子"},
    {"name": "丑時", "hours": (1, 3), "branch": "丑"},
    {"name": "寅時", "hours": (3, 5), "branch": "寅"},
    {"name": "卯時", "hours": (5, 7), "branch": "卯"},
    {"name": "辰時", "hours": (7, 9), "branch": "辰"},
    {"name": "巳時", "hours": (9, 11), "branch": "巳"},
    {"name": "午時", "hours": (11, 13), "branch": "午"},
    {"name": "未時", "hours": (13, 15), "branch": "未"},
    {"name": "申時", "hours": (15, 17), "branch": "申"},
    {"name": "酉時", "hours": (17, 19), "branch": "酉"},
    {"name": "戌時", "hours": (19, 21), "branch": "戌"},
    {"name": "亥時", "hours": (21, 23), "branch": "亥"},
]

# ===== 天干地支 =====
TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

TIANGAN_POLARITY = {
    "甲": "Yang", "乙": "Yin",
    "丙": "Yang", "丁": "Yin",
    "戊": "Yang", "己": "Yin",
    "庚": "Yang", "辛": "Yin",
    "壬": "Yang", "癸": "Yin"
}

TIANGAN_ELEMENT = {
    "甲": "Wood", "乙": "Wood",
    "丙": "Fire", "丁": "Fire",
    "戊": "Earth", "己": "Earth",
    "庚": "Metal", "辛": "Metal",
    "壬": "Water", "癸": "Water"
}

# 五行生剋
PRODUCING = {"Wood": "Fire", "Fire": "Earth", "Earth": "Metal", "Metal": "Water", "Water": "Wood"}
CONTROLLING = {"Wood": "Earth", "Earth": "Water", "Water": "Fire", "Fire": "Metal", "Metal": "Wood"}
PRODUCED_BY = {v: k for k, v in PRODUCING.items()}
CONTROLLED_BY = {v: k for k, v in CONTROLLING.items()}

# ===== 高階八字格局定義 =====
STRUCTURES = [
    {"name": "正官格", "en": "Direct Officer", "type": "Normal", "trait": "正直守法，重視名譽，適合公職或管理"},
    {"name": "七殺格", "en": "Seven Killings", "type": "Normal", "trait": "威權果斷，富冒險精神，人生大起大落"},
    {"name": "正財格", "en": "Direct Wealth", "type": "Normal", "trait": "勤儉務實，重視穩定收入，保守理財"},
    {"name": "偏財格", "en": "Indirect Wealth", "type": "Normal", "trait": "豪爽大方，善於交際，有投資投機眼光"},
    {"name": "正印格", "en": "Direct Resource", "type": "Normal", "trait": "仁慈聰慧，重精神層面，有貴人相助"},
    {"name": "偏印格", "en": "Indirect Resource", "type": "Normal", "trait": "機智敏銳，特立獨行，適合偏門冷門行業"},
    {"name": "食神格", "en": "Eating God", "type": "Normal", "trait": "溫和樂觀，重視享受，有藝術才華"},
    {"name": "傷官格", "en": "Hurting Officer", "type": "Normal", "trait": "才華洋溢，傲氣叛逆，不畏強權"},
    {"name": "建祿格", "en": "Self Prosperity", "type": "Normal", "trait": "白手起家，獨立自主，性格剛毅"},
    {"name": "羊刃格", "en": "Goat Blade", "type": "Normal", "trait": "性情剛烈，衝動急躁，適合武職軍警"},
    {"name": "從財格", "en": "Follow Wealth", "type": "Cong", "trait": "識時務者，隨波逐流，為追求財富可妥協"},
    {"name": "從殺格", "en": "Follow Power", "type": "Cong", "trait": "依附權威，追求權力，有強烈事業心"},
    {"name": "從兒格", "en": "Follow Child (Output)", "type": "Cong", "trait": "聰明絕頂，靠才華智慧取勝，追求自由"},
    {"name": "專旺格", "en": "Dominant Element", "type": "Dominant", "trait": "個性極強，固執堅持，在專業領域有大成就"},
]

# ===== 帶術語的人性化描述 (權威感 + 易懂) =====
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
    """判斷十神關係"""
    my_elem = TIANGAN_ELEMENT[me]
    target_elem = TIANGAN_ELEMENT[target]
    is_same_pol = TIANGAN_POLARITY[me] == TIANGAN_POLARITY[target]
    
    if my_elem == target_elem:
        return "Bi Jian" if is_same_pol else "Jie Cai"
    if PRODUCED_BY[my_elem] == target_elem:
        return "PiAn Yin" if is_same_pol else "Zheng Yin"
    if PRODUCING[my_elem] == target_elem:
        return "Shi Shen" if is_same_pol else "Shang Guan"
    if CONTROLLED_BY[my_elem] == target_elem:
        return "Qi Sha" if is_same_pol else "Zheng Guan"
    if CONTROLLING[my_elem] == target_elem:
        return "PiAn Cai" if is_same_pol else "Zheng Cai"
    return "Unknown"

def generate_colloquial_state(citizen: dict) -> dict:
    """生成帶八字術語但白話易懂的描述 (多語言)"""
    age = citizen["age"]
    gender = citizen.get("gender", "男")
    p = citizen["bazi_profile"]
    
    # 1. 找出當前大運
    current_luck = None
    for luck in p["luck_pillars"]:
        if luck["age_start"] <= age <= luck["age_end"]:
            current_luck = luck
            break
    if not current_luck:
        current_luck = p["luck_pillars"][0]
    
    # 2. 核心性格描述（帶術語）
    pattern_term, pattern_desc = PERSONALITY_CORE.get(p["structure"], ("多元格局", "個性多元，很有自己的想法"))
    
    # 3. 當前生活狀態（帶術語）
    ten_god = get_ten_god(p["day_master"][0], current_luck["gan"])
    luck_term, luck_desc = LIFE_PHASE_NOW.get(ten_god, ("平穩運", "目前生活平穩，順其自然"))
    
    # 4. 組合：術語（解釋）+ 描述
    pronoun = "她" if gender == "女" else "他"
    tw_state = f"{pattern_term}：{pattern_desc}。{pronoun}目前行{luck_term}，{luck_desc}。"
    
    return {
        "TW": tw_state,
        "CN": t_cn(tw_state),
        "US": "Strategic decision making based on Bazi structure."
    }


# ===== 輔助函數 (延續 V4) =====

def weighted_random_choice(choices_dict):
    items = list(choices_dict.keys())
    weights = list(choices_dict.values())
    return random.choices(items, weights=weights, k=1)[0]

def random_age_from_range():
    age_ranges = {(18, 25): 15, (26, 35): 30, (36, 45): 25, (46, 55): 18, (56, 65): 10, (66, 75): 2}
    age_range = weighted_random_choice({str(k): v for k, v in age_ranges.items()})
    min_age, max_age = eval(age_range)
    return random.randint(min_age, max_age)

def generate_birthdate(age: int) -> dict:
    current_year = 2026
    birth_year = current_year - age
    birth_month = random.randint(1, 12)
    max_day = 31 if birth_month in [1, 3, 5, 7, 8, 10, 12] else (30 if birth_month != 2 else (29 if birth_year%4==0 else 28))
    birth_day = random.randint(1, max_day)
    shichen = random.choice(SHICHEN)
    hour = random.randint(shichen["hours"][0], shichen["hours"][1]-1) if shichen["hours"][0] < shichen["hours"][1] else random.choice([23, 0])
    return {"year": birth_year, "month": birth_month, "day": birth_day, "hour": hour, "shichen": shichen["name"], "shichen_branch": shichen["branch"]}

def calculate_bazi_pillars(birthdate: dict) -> dict:
    y_gan_idx, y_zhi_idx = (birthdate["year"] - 4) % 10, (birthdate["year"] - 4) % 12
    m_gan_idx, m_zhi_idx = (y_gan_idx * 2 + birthdate["month"]) % 10, (birthdate["month"] + 1) % 12
    d_gan_idx, d_zhi_idx = random.randint(0, 9), random.randint(0, 11)
    # 修正時干計算邏輯
    h_zhi_idx = DIZHI.index(birthdate["shichen_branch"])
    h_gan_idx = (d_gan_idx * 2 + h_zhi_idx) % 10
    
    dm = TIANGAN[d_gan_idx]
    return {
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

def get_favorable_elements(structure_info: dict, strength: str, my_element: str) -> dict:
    tp = structure_info["type"]; name = structure_info["name"]
    child, wealth, officer, mother, friend = PRODUCING[my_element], CONTROLLING[my_element], CONTROLLED_BY[my_element], PRODUCED_BY[my_element], my_element
    if tp == "Dominant" or name in ["建祿格", "羊刃格"]: fav, unfav = [mother, friend, child], [wealth, officer]
    elif tp == "Cong":
        if name == "從財格": fav, unfav = [wealth, child], [mother, friend]
        elif name == "從殺格": fav, unfav = [officer, wealth], [mother, friend, child]
        else: fav, unfav = [child, wealth], [mother, officer]
    else:
        if strength == "身弱": fav, unfav = [mother, friend], [officer, child, wealth]
        else: fav, unfav = [officer, child, wealth], [mother, friend]
    return {"favorable": list(set(fav)), "unfavorable": list(set(unfav))}

# 強制中文字映射 (Force Chinese Map)
# 繁體中文對照表 (確保輸出為繁體)
STEMS_CN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
BRANCHES_CN = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

def get_dayun_sequence(gender, year_gan, m_gan_idx, m_zhi_idx, day_master):
    """計算10年大運序列（真實四柱推算）"""
    # 大運排法：陽男陰女順行(+1)，陰男陽女逆行(-1)
    is_yang_year = TIANGAN_POLARITY[year_gan] == "Yang"
    is_male = (gender == "male")
    direction = 1 if (is_yang_year and is_male) or (not is_yang_year and not is_male) else -1
    
    start_age = random.randint(1, 10) # 實際應由節氣計算，此处簡化為隨機起運 1-10 歲
    pillars = []
    
    cur_g, cur_z = m_gan_idx, m_zhi_idx
    
    for i in range(8):
        cur_g = (cur_g + direction) % 10
        cur_z = (cur_z + direction) % 12
        
        gan_char = STEMS_CN[cur_g]
        zhi_char = BRANCHES_CN[cur_z]
        pillar_str = f"{gan_char}{zhi_char}"
        
        # 計算十神
        ten_god = get_ten_god(day_master, gan_char) 
        luck_term, luck_desc = LIFE_PHASE_NOW.get(ten_god, ("平穩運", "平穩過渡"))
        
        tw_desc = f"{luck_term}：{luck_desc}"
        cn_desc = t_cn(tw_desc)
        
        pillars.append({
            "pillar": pillar_str, 
            "gan": gan_char, 
            "age_start": start_age + (i * 10), 
            "age_end": start_age + (i * 10) + 9,
            "description": tw_desc,
            "localized_description": {
                "TW": tw_desc,
                "CN": cn_desc,
                "US": f"Luck Cycle: {ten_god}"
            },
            "ten_god": ten_god
        })
    return pillars

# ===== 職業列表 =====
# ===== 職業資料庫 (分層級) =====
OCCUPATIONS_DB = {
    "student": ["學生", "大學生", "研究所學生", "實習生"],
    "entry": ["行政助理", "初階工程師", "行銷專員", "銀行行員", "社群小編", "總機人員", "服務生", "咖啡師", "外送員", "保全人員"],
    "mid": ["資深工程師", "產品經理 (PM)", "UI/UX 設計師", "專案經理", "理財專員", "護理師", "健身教練", "室內設計師", "公務員", "警察", "廚師", "YouTuber", "Podcaster", "網紅/KOL", "自由業者"],
    "senior": ["技術主管 (Tech Lead)", "財務經理", "行銷總監", "大學教授", "主治醫師", "創業家", "資深顧問", "中小企業主", "部門主管"],
    "retiree": ["退休人員", "資深志工", "退休公務員"]
}

def get_valid_occupation(age):
    """
    Age-Occupation Matrix (年齡-職業矩陣)
    確保職業與年齡的合理性關係
    """
    valid_pools = []
    
    # 1. 學生/社會新鮮人 (18-24)
    if 18 <= age <= 24:
        valid_pools.extend(OCCUPATIONS_DB["student"])
        # 20歲以上可以開始做初階工作
        if age >= 20:
            valid_pools.extend(OCCUPATIONS_DB["entry"])
            
    # 2. 職場成長期 (23-30)
    elif 25 <= age <= 30:
        valid_pools.extend(OCCUPATIONS_DB["entry"])
        valid_pools.extend(OCCUPATIONS_DB["mid"])
        
    # 3. 職場成熟期 (31-45)
    elif 31 <= age <= 45:
        valid_pools.extend(OCCUPATIONS_DB["mid"])
        # 35歲以上有機率進入高階
        if age >= 35:
            valid_pools.extend(OCCUPATIONS_DB["senior"])
            
    # 4. 職場資深期 (46-60)
    elif 46 <= age <= 60:
        valid_pools.extend(OCCUPATIONS_DB["mid"]) # 仍有不少人維持中階專業職
        valid_pools.extend(OCCUPATIONS_DB["senior"])
        
    # 5. 退休/高齡期 (61+)
    else:
        valid_pools.extend(OCCUPATIONS_DB["senior"]) # 資深專業人士可能延後退休
        valid_pools.extend(OCCUPATIONS_DB["retiree"])
        
    # 防呆：如果範圍外 (極少見)，給予 generic
    if not valid_pools:
        valid_pools = ["自由業者"]
        
    return random.choice(valid_pools)

def generate_citizen(idx):
    g = random.choice(["male", "female"])
    age = random_age_from_range()
    surname = random.choice(SURNAMES)
    given = (random.choice(MALE_NAMES if g=="male" else FEMALE_NAMES) + random.choice(MALE_NAMES if g=="male" else FEMALE_NAMES)) if random.random()<0.95 else random.choice(MALE_NAMES if g=="male" else FEMALE_NAMES)
    bd = generate_birthdate(age); bz = calculate_bazi_pillars(bd)
    struct = random.choice(STRUCTURES)
    strength = random.choice(["身強", "身弱", "中和"]) if struct["type"]=="Normal" else ("極強" if struct["type"]=="Dominant" else "極弱")
    luck = get_dayun_sequence(g, bz["year_gan"], bz["month_gan_idx"], bz["month_zhi_idx"], bz["day_master"][0])
    
    # 構造 Luck Timeline (符合前端需求: name, description, age_start, age_end)
    luck_timeline = []
    current_luck_obj = {}
    
    for l in luck:
        name = l['pillar'] + "運"
        localized_desc = l.get('localized_description', {
            "TW": l['description'],
            "CN": t_cn(l['description']),
            "US": l.get('ten_god', 'Unknown')
        })
        
        lt_item = {
            "age_start": l['age_start'],
            "age_end": l['age_end'],
            "name": name,
            "pillar": l['pillar'],
            "description": l['description'],
            "localized_description": localized_desc
        }
        luck_timeline.append(lt_item)
        
        # 找出當前大運
        if l['age_start'] <= age <= l['age_end']:
            current_luck_obj = lt_item
            
    # 如果沒找到當前大運（極少情況），用第一個
    if not current_luck_obj and luck_timeline:
        current_luck_obj = luck_timeline[0]

    # 構造初步資料以便 generate_colloquial_state 讀取
    citizen_partial = {
        "age": age,
        "gender": "女" if g=="female" else "男",
        "bazi_profile": {
            "day_master": bz["day_master"],
            "structure": struct["name"],
            "luck_pillars": luck
        }
    }
    current_state_dict = generate_colloquial_state(citizen_partial)
    
    return {
        "name": surname + given,
        "gender": "男" if g=="male" else "女",
        "age": age,
        "location": weighted_random_choice({"台北, 台灣":20, "新北, 台灣":15, "台中, 台灣":12, "高雄, 台灣":10, "台南, 台灣":8}),
        "occupation": {"TW": get_valid_occupation(age)}, # Ensure JSON Object format
        "bazi_profile": {
            **bz, 
            "birth_year": bd["year"],
            "birth_month": bd["month"],
            "birth_day": bd["day"],
            "birth_shichen": bd["shichen"],
            "four_pillars": f"{bz['year_pillar']} {bz['month_pillar']} {bz['day_pillar']} {bz['hour_pillar']}",
            "structure": struct["name"], 
            "structure_en": struct["name"], 
            "strength": strength,
            "favorable": get_favorable_elements(struct, strength, bz["element"])["favorable"], # 前端用 favorable
            "unfavorable_elements": get_favorable_elements(struct, strength, bz["element"])["unfavorable"],
            "luck_pillars": luck, # 保留舊格式備用
            "luck_timeline": luck_timeline, # 前端主要使用
            "current_luck": current_luck_obj, # 前端主要使用
            "current_state": current_state_dict["TW"],
            "localized_state": current_state_dict
        },
        "traits": [struct["trait"].split("，")[0]] + random.sample(["理性", "感性", "科技迷", "環保者", "務實"], 2)
    }

def main():
    print("=" * 60)
    print("MIRRA Genesis V5 - 創世紀造人程式 (Final Production)")
    print("=" * 60)
    clear_citizens(); num = 1000
    print(f"生成 {num} 位 AI 市民 (真實演算)...")
    citizens = [generate_citizen(i) for i in range(num)]
    
    # 顯示範例
    s = citizens[0]
    print(f"\n範例: {s['name']} ({s['age']}歲)")
    print(f"   目前狀態: {s['bazi_profile']['current_state']}")
    
    # 寫入 DB
    batch_size = 100
    for i in range(0, len(citizens), batch_size):
        if insert_citizens_batch(citizens[i:i+batch_size]):
            print(f"   已插入 {i+batch_size}/{num}")

    # [NEW] 寫入 JSON (Crucial for Frontend/Genesis API)
    # Inject IDs for JSON consistency
    for idx, c in enumerate(citizens):
        c['id'] = str(idx + 1)

    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "citizens.json")
    import json
    import datetime
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    
    output_data = {
        "meta": {
            "constitution": "v5.0",
            "generated_at": datetime.datetime.now().isoformat(),
            "note": "Final Production Genesis"
        },
        "citizens": citizens,
        "total": len(citizens)
    }
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"   已儲存 JSON 到 {json_path}")
            
    print(f"\n創世紀 V5 完成！總數: {get_citizens_count()}")

if __name__ == "__main__":
    main()
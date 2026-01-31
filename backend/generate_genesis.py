import json
import random
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List

# Add project root to path to import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Try to import BaziCalcSkill, fallback if fails (though it should work)
try:
    from backend.app.skills.bazi_calc import BaZiCalcSkill
except ImportError:
    # If running from backend/ directly
    sys.path.append(os.path.join(os.path.dirname(__file__)))
    from app.skills.bazi_calc import BaZiCalcSkill

# Constants
OUTPUT_FILE = "backend/app/data/citizens.json"
TOTAL_CITIZENS = 10

# Mock Data for Profiles based on SES
SES_DATA = {
    "1-2": {
        "TW": [("臨時工", "收入不穩，生活拮据"), ("拾荒者", "受人冷眼，三餐不繼")],
        "CN": [("三和大神", "日结一天，玩三天"), ("务农人员", "靠天吃饭，收入微薄")],
        "US": [("Homeless", "Struggling with shelter and food"), ("Day Laborer", "Uncertain income, no benefits")]
    },
    "3-4": {
        "TW": [("超商店員", "輪班累，奧客多"), ("外送員", "風吹日曬，搶單壓力"), ("保全", "工時長，薪水低")],
        "CN": [("快递小哥", "分秒必争，罚款压力"), ("工厂流水线", "枯燥重复，无升迁"), ("保安", "看大门，无聊")],
        "US": [("Uber Driver", "Car maintenance costs, long hours"), ("Retail Cashier", "Standing all day, rude customers"), ("Warehouse Worker", "Physical exhaustion, quotas")]
    },
    "5-6": {
        "TW": [("公務員", "體制僵化，升遷慢"), ("護理師", "過勞，醫病關係緊張"), ("一般行政", "薪水死豬價，無成就感")],
        "CN": [("国企员工", "人际复杂，熬资历"), ("护士", "医闹风险，夜班辛苦"), ("文员", "工资低，且易被替代")],
        "US": [("Teacher", "Underpaid, managing unruly students"), ("Nurse", "Long shifts, emotional burnout"), ("Office Admin", "Boring routine, office politics")]
    },
    "7-8": {
        "TW": [("科技業工程師", "爆肝，沒時間花錢"), ("資深經理", "夾心餅乾，業績壓力"), ("律師", "案子接不完，高壓")],
        "CN": [("大厂程序员", "996福报，35岁危机"), ("投行经理", "由于常常出差，身体透支"), ("律师", "竞争激烈，由于需要维持案源")],
        "US": [("Software Engineer", "On-call stress, keeping up with tech"), ("Product Manager", "Responsibility without authority"), ("Corporate Lawyer", "Billable hours pressure, no work-life balance")]
    },
    "9-10": {
        "TW": [("上市公司CEO", "股東壓力，決策孤獨"), ("知名投資人", "市場波動，資金風險"), ("政治世家", "輿論檢視，隱私全無")],
        "CN": [("集团总裁", "政策风险，各方博弈"), ("天使投资人", "项目失败率高，看人脸色"), ("红二代", "言行受限，高处不胜寒")],
        "US": [("Tech CEO", "Public scrutiny, stock price obsession"), ("Venture Capitalist", "FOMO, high stakes bets"), ("Senator", "Constant campaigning, public attacks")]
    }
}

STRUCTURES = ["正官格", "七殺格", "正財格", "偏財格", "正印格", "偏印格", "食神格", "傷官格", "建祿格", "羊刃格"]
ELEMENTS = ["Wood", "Fire", "Earth", "Metal", "Water"]

def get_ses_group(ses):
    if ses <= 2: return "1-2"
    if ses <= 4: return "3-4"
    if ses <= 6: return "5-6"
    if ses <= 8: return "7-8"
    return "9-10"

def generate_birth_date():
    start_date = datetime(1960, 1, 1)
    end_date = datetime(2005, 12, 31)
    days_between = (end_date - start_date).days
    random_days = random.randrange(days_between)
    birth_date = start_date + timedelta(days=random_days)
    hour = random.randint(0, 23)
    return birth_date, hour

async def generate_citizen(index):
    # 1. Basic DNA
    birth_date, hour = generate_birth_date()
    
    # Call BaZi Calculator
    bazi_skill = BaZiCalcSkill()
    bazi_context = {
        "year": birth_date.year,
        "month": birth_date.month,
        "day": birth_date.day,
        "hour": hour
    }
    bazi_result = await bazi_skill.execute(bazi_context)
    bazi_data = bazi_result.get("bazi", {})
    
    # Mock Extended Bazi Data (Since the calculator is simplified)
    structure = random.choice(STRUCTURES)
    day_master_element = random.choice(ELEMENTS)
    strength = random.choice(["身強", "身弱", "中和"])
    favorable = random.sample(ELEMENTS, 2)
    
    bazi_profile = {
        "birth_year": birth_date.year,
        "birth_month": birth_date.month,
        "birth_day": birth_date.day,
        "birth_hour": hour,
        "four_pillars": bazi_data, # Object {year, month, day, hour}
        "structure": structure,
        "strength": strength,
        "element": day_master_element,
        "favorable_elements": favorable,
        "current_state": "運勢流轉，需靜待時機" if strength == "身弱" else "氣勢如虹，可大展身手",
        "luck_pillars": [] # Mock empty for now or generate simple ones
    }
    
    # 2. SES & Social Identity
    rand_val = random.random()
    if rand_val < 0.05: ses = random.randint(9, 10)
    elif rand_val < 0.20: ses = random.randint(7, 8)
    elif rand_val < 0.60: ses = random.randint(5, 6)
    elif rand_val < 0.90: ses = random.randint(3, 4)
    else: ses = random.randint(1, 2)
    
    ses_group = get_ses_group(ses)
    gender = random.choice(["Male", "Female"])
    
    # 3. Generate Profiles
    profiles = {}
    
    # Select Base Occupation/Pain for consistency or variety? 
    # Let's pick random for each region but keep SES consistent.
    
    # TW
    tw_job, tw_pain = random.choice(SES_DATA[ses_group]["TW"])
    tw_name = f"台灣人{index}" # Placeholder name
    # Real names needed? Let's use simple generated names.
    last_names = ["陳", "林", "黃", "張", "李", "王", "吳", "劉", "蔡", "楊"]
    first_names_m = ["志明", "家豪", "俊傑", "建宏", "俊宏"]
    first_names_f = ["淑芬", "淑惠", "美玲", "雅婷", "雅惠"]
    tw_name = random.choice(last_names) + (random.choice(first_names_m) if gender == "Male" else random.choice(first_names_f))
    
    profiles["TW"] = {
        "name": tw_name,
        "city": random.choice(["Taipei", "Kaohsiung", "Taichung"]),
        "job": tw_job,
        "pain": tw_pain
    }
    
    # CN
    cn_job, cn_pain = random.choice(SES_DATA[ses_group]["CN"])
    cn_last = ["王", "李", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴"]
    cn_first_m = ["伟", "强", "磊", "洋", "勇"]
    cn_first_f = ["芳", "娜", "敏", "静", "秀"]
    cn_name = random.choice(cn_last) + (random.choice(cn_first_m) if gender == "Male" else random.choice(cn_first_f))
    
    profiles["CN"] = {
        "name": cn_name,
        "city": random.choice(["Shanghai", "Beijing", "Shenzhen"]),
        "job": cn_job,
        "pain": cn_pain
    }
    
    # US
    us_job, us_pain = random.choice(SES_DATA[ses_group]["US"])
    us_first_m = ["James", "John", "Robert", "Michael", "William"]
    us_first_f = ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth"]
    us_last = ["Smith", "Johnson", "Williams", "Brown", "Jones"]
    us_name = (random.choice(us_first_m) if gender == "Male" else random.choice(us_first_f)) + " " + random.choice(us_last)
    
    profiles["US"] = {
        "name": us_name,
        "city": random.choice(["New York", "Los Angeles", "Chicago"]),
        "job": us_job,
        "pain": us_pain
    }

    age = 2026 - birth_date.year # Today is 2026 according to env
    
    return {
        "id": str(10000 + index),
        "name": tw_name, # Default name
        "gender": gender,
        "age": age,
        "location": profiles["TW"]["city"],
        "occupation": profiles["TW"]["job"],
        "bazi_profile": bazi_profile,
        "traits": [structure, strength, day_master_element], # Simple traits
        "profiles": profiles,
        "ses": ses
    }

async def main():
    print("Starting Project Genesis - Phase 1: Prototype Minting...")
    
    citizens = []
    for i in range(TOTAL_CITIZENS):
        c = await generate_citizen(i + 1)
        citizens.append(c)
        print(f"   Minted Citizen #{c['id']}: {c['name']} (SES {c['ses']})")
    
    final_data = {
        "meta": {
            "constitution": "v1.0",
            "generated_at": datetime.now().isoformat(),
            "note": "Prototype Genesis Generation"
        },
        "citizens": citizens,
        "total": len(citizens)
    }
    
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
        
    print(f"\n✅ Successfully generated {len(citizens)} citizens to {OUTPUT_FILE}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

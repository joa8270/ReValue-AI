
import os
import json
import random
import sys

# Setup Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # backend/
sys.path.append(BASE_DIR)

from app.core.database import insert_citizens_batch, clear_citizens

DATA_FILE = os.path.join(BASE_DIR, 'data', 'citizens.json')
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'citizens_repaired.json')

# --- Bazi Knowledge Base ---
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
ELEMENTS = ["Wood", "Fire", "Earth", "Metal", "Water"]

def get_random_pillar():
    stem = random.choice(HEAVENLY_STEMS)
    branch = random.choice(EARTHLY_BRANCHES)
    return f"{stem}{branch}"

def synthesize_bazi(age: int, structure: str) -> dict:
    """synthesize a realistic looking bazi profile based on age and structure"""
    
    # 1. Calc Birth Year (Approx)
    current_year = 2025
    birth_year = current_year - age
    
    # 2. Assign Element based on Structure (Simplified)
    element_map = {
        "食神格": "Wood", "傷官格": "Fire", 
        "正財格": "Earth", "偏財格": "Earth",
        "正官格": "Metal", "七殺格": "Metal",
        "正印格": "Water", "偏印格": "Water",
        "比肩格": "Wood", "劫財格": "Fire"
    }
    # Parse structure string "食神格 (講究體驗)" -> "食神格"
    struct_key = structure.split(" ")[0]
    main_element = element_map.get(struct_key, random.choice(ELEMENTS))

    # 3. Generate Pillars
    pillars = {
        "year": get_random_pillar(),
        "month": get_random_pillar(),
        "day": get_random_pillar(),
        "hour": get_random_pillar()
    }

    return {
        "birth_year": birth_year,
        "birth_month": random.randint(1, 12),
        "birth_day": random.randint(1, 28),
        "birth_shichen": random.choice(["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]),
        "four_pillars": [pillars['year'], pillars['month'], pillars['day'], pillars['hour']],
        "day_master": random.choice(HEAVENLY_STEMS),
        "structure": structure,
        "strength": random.choice(["身強", "身弱", "中和"]),
        "element": main_element,
        "favorable": random.sample(ELEMENTS, 2),
        "current_luck": {"pillar": get_random_pillar(), "start_age": (age // 10) * 10, "end_age": ((age // 10) * 10) + 9},
        "luck_timeline": [
            {"age": 10, "pillar": get_random_pillar()},
            {"age": 20, "pillar": get_random_pillar()},
            {"age": 30, "pillar": get_random_pillar()},
            {"age": 40, "pillar": get_random_pillar()},
            {"age": 50, "pillar": get_random_pillar()},
        ],
        "trait": f"命主{structure}，五行屬{main_element}。性格特質呈現{random.choice(['外向', '內斂', '強勢', '溫和'])}，適合從事{main_element}相關行業。"
    }

def seed_and_repair():
    print("🚑 Starting V4 Data Repair & Seeding...")
    
    if not os.path.exists(DATA_FILE):
        print("❌ citizens.json not found.")
        return

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        citizens = json.load(f)
    
    print(f"📖 Loaded {len(citizens)} citizens.")
    
    db_records = []
    repaired_count = 0
    
    for c in citizens:
        # Check if repair needed
        # V3 generator puts structure string in 'bazi' field, but no bazi_profile object.
        bazi_str = c.get("bazi", "Unknown")
        
        # Synthesize Bazi Profile if missing or incomplete
        # We assume if it's not a dict, or missing 'four_pillars', it needs repair.
        existing_profile = c.get("bazi_profile")
        if not isinstance(existing_profile, dict) or "four_pillars" not in existing_profile:
            bazi_profile = synthesize_bazi(c.get("age", 30), bazi_str)
            c["bazi_profile"] = bazi_profile # Save back to JSON object
            repaired_count += 1
        else:
            bazi_profile = existing_profile

        # Prepare for DB
        tw_profile = c.get("profiles", {}).get("TW", {})
        
        record = {
            "name": c.get("name"),
            "gender": c.get("gender"),
            "age": c.get("age"),
            "location": tw_profile.get("city", "Unknown"),
            "occupation": tw_profile.get("job", "Unknown"),
            "bazi_profile": bazi_profile, # Now verified/synthesized
            "traits": [c.get("mbti")] if isinstance(c.get("mbti"), str) else c.get("traits", []),
            "profiles": c.get("profiles")
        }
        db_records.append(record)
    
    print(f"🔧 Repaired {repaired_count} citizens' Bazi data.")
    
    # 1. Update JSON File first (Persistence)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(citizens, f, ensure_ascii=False, indent=2)
    # Overwrite source
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(citizens, f, ensure_ascii=False, indent=2)
    print("💾 JSON files updated.")

    # 2. Seed Database
    clear_citizens()
    success = insert_citizens_batch(db_records)
    
    if success:
        print(f"✅ Database successfully re-seeded with {len(db_records)} validated citizens.")
    else:
        print("❌ Database insert failed.")

if __name__ == "__main__":
    seed_and_repair()

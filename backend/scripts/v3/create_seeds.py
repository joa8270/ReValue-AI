
import json
import os
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'citizens_seed.json')

BAZI_TYPES = [
    "食神格 (講究體驗)", "七殺格 (行動派)", "正官格 (守規矩)", 
    "偏財格 (機靈)", "正印格 (仁慈)", "傷官格 (叛逆)", 
    "比肩格 (自我)", "劫財格 (競爭)"
]

MBTI_TYPES = ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"]
CITIES_TW = ["Taipei", "New Taipei", "Taichung", "Kaohsiung", "Hsinchu", "Tainan"]
JOBS_TW = ["Engineer", "Teacher", "Sales", "Designer", "PM", "Marketing", "Freelancer", "Student", "Civil Servant", "Doctor", "Lawyer", "Accountant", "Nurse", "Chef"]

def create_seeds():
    print(f"🌱 Generating 1,000 V3 Seeds...")
    seeds = []
    
    for i in range(1000):
        # We purposely do NOT put "name": "Citizen_xxxx" here to prevent it being used as a fallback.
        # We put a flag that MUST be replaced.
        seed = {
            "id": f"Citizen_{i:04d}",
            "gender": random.choice(["Male", "Female"]),
            "age": random.randint(22, 45),
            "bazi": random.choice(BAZI_TYPES),
            "mbti": random.choice(MBTI_TYPES),
            "base_city": random.choice(CITIES_TW),
            "base_job": random.choice(JOBS_TW),
            "status": "PENDING"
        }
        seeds.append(seed)
        
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(seeds, f, ensure_ascii=False, indent=2)
        
    print(f"✅ Saved 1,000 seeds to {OUTPUT_FILE}")

if __name__ == "__main__":
    create_seeds()

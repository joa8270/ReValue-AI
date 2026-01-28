
import json
import sys
import os

# Add path to scripts
sys.path.append(os.path.join(os.getcwd(), 'backend', 'scripts'))
from genesis_v6 import CitizenGeneratorV6

def verify():
    # 1. Load generated file
    with open('backend/data/citizens_v6.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    citizen_1_file = next(c for c in data if c["id"] == "Citizen_0001")
    
    # 2. Re-generate
    gen = CitizenGeneratorV6()
    citizen_1_regen = gen.generate_single(1)
    
    # 3. Compare Deeply
    diffs = []
    
    # Check Basics
    if citizen_1_file["mbti"] != citizen_1_regen["mbti"]:
        diffs.append(f"MBTI mismatch: File={citizen_1_file['mbti']}, Regen={citizen_1_regen['mbti']}")
    
    # Check Bazi
    bazi_f = citizen_1_file["bazi_profile"]["four_pillars"]
    bazi_r = citizen_1_regen["bazi_profile"]["four_pillars"]
    if bazi_f != bazi_r:
        diffs.append(f"Bazi mismatch: {bazi_f} vs {bazi_r}")
        
    # Check Luck
    if citizen_1_file["bazi_profile"]["current_luck"] != citizen_1_regen["bazi_profile"]["current_luck"]:
        diffs.append("Luck cycle mismatch")
        
    if not diffs:
        print("✅ CONSISTENCY VERIFIED: Citizen_0001 is identical.")
    else:
        print("❌ CONSISTENCY FAILED:")
        for d in diffs: print(d)
        sys.exit(1)

if __name__ == "__main__":
    verify()

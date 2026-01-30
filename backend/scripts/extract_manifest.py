
import json
import os
import sys

# Add backend to path to import constants if needed, but we can just use raw string matching or ignore
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

INPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "citizens.json")
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "citizen_manifest.json")

def extract():
    print(f"Reading from {INPUT_FILE}...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    citizens = data.get("citizens", [])
    manifest = []
    

    # Pain Points from genesis_final.py (Hardcoded here for matching)
    PAIN_POINTS_TW = [
        "財多身弱 (財務壓力大，難守財)",
        "比劫奪財 (職場競爭激烈，犯小人)",
        "殺重身輕 (生活壓力大，易焦慮)",
        "食傷生財 (才華難現，懷才不遇)",
        "印星過旺 (依賴心重，行動力低)",
        "財庫逢沖 (投資失利，破財風險)"
    ]

    for c in citizens:
        bp = c.get("bazi_profile", {})
        
        # Reverse lookup pain index
        current_pain = c["profiles"]["TW"]["pain"]
        try:
            pain_idx = PAIN_POINTS_TW.index(current_pain)
        except ValueError:
            pain_idx = 0 # Default if mismatch
            
        # Extract Fixed Identity Data
        entry = {
            "id": c["id"],
            "gender": c["gender"],
            "birth": {
                "year": bp["birth_year"],
                "month": bp["birth_month"],
                "day": bp["birth_day"],
                "hour": bp["birth_hour"]
            },
            "profiles": {
                "TW": {
                    "name": c["profiles"]["TW"]["name"],
                    "city": c["profiles"]["TW"]["city"],
                    "job": c["profiles"]["TW"]["job"]
                },
                "CN": {
                    "name": c["profiles"]["CN"]["name"],
                    "city": c["profiles"]["CN"]["city"],
                    "job": c["profiles"]["CN"]["job"]
                },
                "US": {
                    "name": c["profiles"]["US"]["name"],
                    "city": c["profiles"]["US"]["city"],
                    "job": c["profiles"]["US"]["job"]
                }
            },
            "seed_values": {
                "pain_idx": pain_idx
            }
        }
        manifest.append(entry)
        
    print(f"Writing manifest to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print("Done.")

if __name__ == "__main__":
    extract()

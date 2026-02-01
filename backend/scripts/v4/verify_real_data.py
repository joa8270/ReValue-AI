
import sys
import os
import asyncio
import json

# Setup Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # backend/
sys.path.append(BASE_DIR)

from app.core.database import get_random_citizens, SessionLocal
from app.services.reviewer_selector import select_reviewers

async def test_real_db_integration():
    print("[TEST] Starting Real DB Integration Test...")
    
    # 1. Fetch Candidates (Large Pool)
    print("   [1] Fetching 2000 citizens from DB...")
    try:
        candidates = await asyncio.to_thread(get_random_citizens, sample_size=2000)
    except Exception as e:
        print(f"   [FAIL] DB Connection Failed: {e}")
        return

    print(f"   [PASS] Fetched {len(candidates)} candidates.")
    
    if len(candidates) < 100:
        print("   [WARN] Not enough citizens for robust testing. (Did generation finish?)")
        
    # 2. Test Expert Selection (US Context)
    print("   [2] Selecting Experts (Mode='Expert')...")
    
    # Mock Sim ID
    sim_id = "verify_test_v1"
    
    experts = select_reviewers(candidates, sim_id, mode="Expert", target_count=10)
    print(f"   [PASS] Selected {len(experts)} experts.")
    
    # 3. Analyze Quality
    print("   [3] Analyzing Expert Quality (Title Check)...")
    fail_count = 0
    for c in experts:
        # Check US Occupation
        # [Fix] get_random_citizens returns 'occupation' as TW string (legacy). 
        # We must use 'occupation_full' to get the multi-language dict.
        occupation_data = c.get('occupation_full') or c.get('occupation')
        print(f"      [DEBUG RAW] occupation_full: {json.dumps(occupation_data, ensure_ascii=True)} (type: {type(occupation_data)})")
        
        if isinstance(occupation_data, str):
             # Legacy or simplified (likely TW string if from get_random_citizens)
             # If it's a string, we can't definitively verify US English unless we assume it's US mode?
             # But get_random_citizens returns TW by default for 'occupation'.
             us_title = occupation_data
        elif isinstance(occupation_data, dict):
             us_title = occupation_data.get('US', 'Unknown')
        else:
             us_title = str(occupation_data)
             
        # Check if title looks like English
        is_english = all(ord(char) < 128 for char in us_title.replace(" ", ""))
        
        print(f"      - ID: {c['id']} | {c['name']} | Job: {us_title} | Tier: {c.get('social_tier')}")
        
        if not is_english:
             print(f"        [FAIL] ERROR: Non-English Title detected in US field!")
             fail_count += 1
             
    if fail_count == 0:
        print("   [PASS] US Identity Check: PASS (All titles are English)")
    else:
        print(f"   [FAIL] US Identity Check: FAIL ({fail_count} non-English titles)")
        sys.exit(1)

    print("[DONE] Real Data Verification Passed!")

if __name__ == "__main__":
    asyncio.run(test_real_db_integration())

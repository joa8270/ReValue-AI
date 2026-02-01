
import sys
import os
import asyncio
import json
import random

# Setup Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # backend/
sys.path.append(BASE_DIR)

from app.core.database import get_random_citizens

async def run_census():
    print("[CENSUS] Starting Final SES Audit...")
    
    # 1. Fetch ALL citizens
    try:
        citizens = await asyncio.to_thread(get_random_citizens, sample_size=2000) # Fetch more to get all 1000
    except Exception as e:
        print(f"   [FAIL] DB Connection Failed: {e}")
        return

    # Trim to legitimate 1000 if duplicates/excess
    # Assuming get_random_citizens returns distinct if DB has < 2000.
    # Actually, create_citizens created 1000.
    
    total = len(citizens)
    print(f"   [INFO] Total Population: {total}")
    
    # 2. Categorize
    # Tier 1 (Elite): senior
    # Tier 2 (Middle): mid, entry
    # Tier 3 (Grassroots): student, blue_collar, service, unemployed
    
    tiers = {
        "Elite": [],
        "Middle": [],
        "Grassroots": []
    }
    
    cities = {"TW": set(), "CN": set(), "US": set()}
    
    for c in citizens:
        cats = c.get('persona_categories', [])
        # Fallback if cats is somehow empty (should not be after P2 fix)
        cat_str = str(cats)
        
        # Determine Tier
        if "senior" in cat_str:
            tiers["Elite"].append(c)
        elif "mid" in cat_str or "entry" in cat_str:
            tiers["Middle"].append(c)
        else:
            # Default to Grassroots for safety (student, blue_collar, service, unemployed)
            tiers["Grassroots"].append(c)
            
        # Collect Cities
        loc = c.get('location_full') or c.get('location')
        if isinstance(loc, dict):
            if loc.get("TW"): cities["TW"].add(loc.get("TW"))
            if loc.get("CN"): cities["CN"].add(loc.get("CN"))
            if loc.get("US"): cities["US"].add(loc.get("US"))
        elif isinstance(loc, str):
            # Legacy string, assign to one bucket or ignore
            cities["TW"].add(loc) 

    # 3. Report Generation
    print("\n" + "="*40)
    print("📊 FINAL CENSUS REPORT (MIRRA 3.0)")
    print("="*40)
    
    # SES Distribution
    e_count = len(tiers["Elite"])
    m_count = len(tiers["Middle"])
    g_count = len(tiers["Grassroots"])
    
    print(f"1. SES Distribution:")
    print(f"   - Elite      (Tier 1): {e_count:<4} ({e_count/total:.1%})")
    print(f"   - Middle     (Tier 2): {m_count:<4} ({m_count/total:.1%})")
    print(f"   - Grassroots (Tier 3): {g_count:<4} ({g_count/total:.1%})")
    
    status = "✅ PASS" if g_count >= 500 else "❌ FAIL"
    print(f"   >>> Result: {status} (Target: Grassroots > 50%)")
    
    # Job Sampling
    print(f"\n2. Job Sampling:")
    
    print(f"   [Tier 1 - Elite Samples]")
    for c in random.sample(tiers["Elite"], min(3, len(tiers["Elite"]))):
        job = c.get('occupation_full', {}).get('US', str(c.get('occupation')))
        print(f"     - {job} ({c['location_full'].get('US', 'Unknown')})")
        
    print(f"   [Tier 3 - Grassroots Samples]")
    for c in random.sample(tiers["Grassroots"], min(5, len(tiers["Grassroots"]))):
        job = c.get('occupation_full', {}).get('US', str(c.get('occupation')))
        print(f"     - {job} ({c['location_full'].get('US', 'Unknown')})")

    # City Spread
    print(f"\n3. City Spread:")
    print(f"   - TW Cities: {len(cities['TW'])} unique")
    print(f"   - CN Cities: {len(cities['CN'])} unique")
    print(f"   - US Cities: {len(cities['US'])} unique")
    
    all_30_plus = all(len(s) >= 30 for s in cities.values())
    city_status = "✅ PASS" if all_30_plus else "⚠️ WARNING (Some < 30)"
    print(f"   >>> Result: {city_status}")
    
    print("="*40 + "\n")

if __name__ == "__main__":
    asyncio.run(run_census())

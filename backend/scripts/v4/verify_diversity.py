
import sys
import os
import asyncio
import json

# Setup Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # backend/
sys.path.append(BASE_DIR)

from app.core.database import get_random_citizens, SessionLocal

async def audit_diversity():
    print("[AUDIT] Starting Diversity & Class Audit...")
    
    # 1. Fetch ALL citizens (Sample 1000)
    print("   [1] Fetching 1000 citizens sample...")
    try:
        citizens = await asyncio.to_thread(get_random_citizens, sample_size=1000)
    except Exception as e:
        print(f"   [FAIL] DB Connection Failed: {e}")
        return

    total = len(citizens)
    print(f"   [PASS] Analyzed {total} citizens.")
    
    # 2. Count Classes
    grassroots_count = 0
    elite_count = 0
    
    # Grassroots Keywords (TW/US/CN mixed)
    grassroots_keywords = [
        "student", "blue_collar", "service", "unemployed",
        "學生", "工人", "服務生", "待業", "店員", "司機", "Student", "Worker", "Driver", "Waiter"
    ]
    
    cities = set()
    pain_count = 0
    
    for c in citizens:
        # Check Job Class
        # We need to rely on 'persona_categories' if available, or infer from job title
        # In P2, we don't have explicit class tags in the final dict easily, 
        # but create_citizens.py logic mapped tags to jobs.
        # Let's check occupation string against known keywords or re-infer.
        
        # Actually, get_random_citizens returns 'persona_categories' list.
        cats = c.get('persona_categories', [])
        
        # [DEBUG] Print first one
        if total > 0 and c['id'] == citizens[0]['id']:
             print(f"   [DEBUG_RAW] ID: {c['id']} | Job: {c.get('occupation')} | Cats: {cats}")
        
        is_grassroots = False
        
        # Check keys from create_citizens categories
        if any(k in str(cats) for k in ['student', 'blue_collar', 'service', 'unemployed']):
            is_grassroots = True
            
        if is_grassroots:
            grassroots_count += 1
        else:
            elite_count += 1
            
        # Check Cities
        loc = c.get('location', '')
        if isinstance(loc, dict): loc = loc.get('US', '')
        cities.add(loc)
        
        # Check Pain Points (Sample check)
        pain = c.get('profiles', {}).get('US', {}).get('pain', '')
        if "Debt" in pain or "Inflation" in pain or "Rent" in pain:
            pain_count += 1

    ratio = grassroots_count / total
    print(f"   [STATS] Grassroots: {grassroots_count} ({ratio:.1%}) | Elite: {elite_count}")
    print(f"   [STATS] Unique Cities: {len(cities)}")
    print(f"   [STATS] Citizens with Explicit Pain (US Sample): {pain_count}")

    # 3. Assertions
    if ratio < 0.55: # Allow slight variance but aim for 0.6
        print(f"   [FAIL] Grassroots ratio {ratio:.1%} is below target 60%!")
        sys.exit(1)
    else:
        print(f"   [PASS] Grassroots ratio met ({ratio:.1%})")
        
    if len(cities) < 25:
        print(f"   [FAIL] City diversity too low ({len(cities)})")
        sys.exit(1)
    else:
        print(f"   [PASS] City diversity good ({len(cities)}+)")

    print("[DONE] Diversity Audit Passed!")

if __name__ == "__main__":
    asyncio.run(audit_diversity())

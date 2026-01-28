import asyncio
import os
import sys
from dotenv import load_dotenv

# Setup path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.core.database import SessionLocal, get_random_citizens
from app.core.abm_engine import ABMSimulation

async def test_abm_citizens():
    load_dotenv()
    
    print("🧪 Testing Citizen Data Integrity...")
    
    # 1. Fetch Random Citizens
    citizens = get_random_citizens(sample_size=10)
    print(f"✅ Fetched {len(citizens)} citizens from DB")
    
    if not citizens:
        print("❌ No citizens found!")
        return

    # 2. Check Raw Data
    c1 = citizens[0]
    print(f"👤 Sample Citizen: {c1['name']} ({c1['age']}y) - {c1['occupation']}")
    
    if not c1.get('age') or not c1.get('occupation'):
        print("❌ CRITICAL: Raw citizen missing Age or Occupation!")
    
    # 3. Simulate ABM Engine Output
    product_info = {"element": "Fire", "price": 100, "market_price": 100}
    sim = ABMSimulation(citizens, product_info)
    sim.initialize_opinions()
    comments = sim.get_final_comments(num_comments=5)
    
    print("\n💬 [ABM Engine Comments Output]")
    passed = True
    for comm in comments:
        print(f"   - {comm['name']} | Age: {comm.get('age')} | Occ: {comm.get('occupation')}")
        if not comm.get('age') or not comm.get('occupation'):
            passed = False
            print("   ❌ MISSING DATA HERE!")
    
    if passed:
        print("\n✅ ABM Engine passed: All comments have Age and Occupation.")
    else:
        print("\n❌ ABM Engine failed: Missing Age or Occupation in comments.")

    # 4. Simulate PDF Prompt Construction (LineBotService Logic)
    citizens_for_prompt = [
        {
            "id": c["id"],
            "name": c["name"],
            "age": c["age"],  # Ensure this matches line_bot_service.py logic
            "gender": c.get("gender"),
            "occupation": c.get("occupation", "未知"), # Ensure this matches patch
            "location": c.get("location"),
        }
        for c in citizens
    ]
    
    print("\n📄 [PDF Prompt Data Construction]")
    pdf_passed = True
    for cp in citizens_for_prompt:
        print(f"   - {cp['name']} | Age: {cp.get('age')} | Occ: {cp.get('occupation')}")
        if not cp.get('age') or not cp.get('occupation'):
            pdf_passed = False
            print("   ❌ MISSING DATA IN PROMPT PREP!")

    if pdf_passed:
        print("\n✅ PDF Prompt Logic passed: All entries have Age and Occupation.")
    else:
        print("\n❌ PDF Prompt Logic failed.")

if __name__ == "__main__":
    asyncio.run(test_abm_citizens())

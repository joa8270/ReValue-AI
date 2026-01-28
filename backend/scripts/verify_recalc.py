import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from app.core.database import SessionLocal, Citizen

def verify_id_9584():
    db = SessionLocal()
    try:
        c = db.query(Citizen).filter(Citizen.id == 9584).first()
        if not c:
            print("❌ ID 9584 not found.")
            return

        p = c.bazi_profile
        print(f"\n--- [FINAL SOUL VALIDATION ID 9584] ---")
        
        # 處理 name 和 occupation 可能是 JSON 或 String 的情況
        display_name = c.name.get('TW', '?') if isinstance(c.name, dict) else str(c.name)
        display_job = c.occupation.get('TW', '?') if isinstance(c.occupation, dict) else str(c.occupation)
        
        print(f"Name: {display_name}")
        print(f"Birthday: {p.get('birth_year')}年{p.get('birth_month')}月{p.get('birth_day')}日")
        print(f"Occupation: {display_job}")
        
        print(f"\n[命理數據]")
        print(f"Structure: {p.get('structure')} ({p.get('strength')})")
        print(f"Pillars: {p.get('four_pillars')}")
        
        fe = p.get("favorable_elements", [])
        print(f"Favorable Elements (喜用五行): {fe if fe else '❌ NONE'}")
        
        cl = p.get("current_luck", {})
        print(f"Current Luck: {cl.get('name')} | {cl.get('description', '❌ NO DESCRIPTION')}")
        
        cs = p.get("current_state")
        print(f"Current State: {cs if cs else '❌ NO STATE'}")
        
        lt = p.get("luck_timeline", [])
        print(f"Luck Cycles Count: {len(lt)}")
        
        if fe and cl.get('description') and cs:
            print("\n✅ PASSED: Soul fully restored and fields aligned.")
        else:
            print("\n❌ FAILED: Some fields are still empty.")

    finally:
        db.close()

if __name__ == "__main__":
    verify_id_9584()

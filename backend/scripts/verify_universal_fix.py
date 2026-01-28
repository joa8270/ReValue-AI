import os
import sys
import random

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from app.core.database import SessionLocal, Citizen

def simulate_frontend_date(y, m, d, market):
    if not y: return "Unknown"
    if market == "US":
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        m_str = month_names[int(m)-1] if m else ""
        d_str = f"{d}, " if d else ""
        return f"{m_str} {d_str}{y}"
    else: # TW / CN
        return f"{y}年{m}月{d}日"

def verify_universal():
    db = SessionLocal()
    try:
        # 1. 統計總數
        all_citizens = db.query(Citizen).all()
        total_citizens = len(all_citizens)
        
        # 2. 檢測是否還有壞數據
        broken = [c for c in all_citizens if not c.bazi_profile.get("birth_day") or "?" in str(c.bazi_profile.get("birth_day"))]
        
        print(f"📊 [DATABASE QUALITY REPORT]")
        print(f"Total Citizens: {total_citizens}")
        print(f"Broken/Masked Birthdays Remaining: {len(broken)}")
        
        # 3. 隨機抽樣 3 位 ID > 9000
        high_ids = [c for c in all_citizens if c.id > 9000]
        samples = random.sample(high_ids, 3) if len(high_ids) >= 3 else high_ids
        
        print("\n--- [UNIVERSAL SCAN SAMPLE (ID > 9000)] ---")
        for sc in samples:
            bp = sc.bazi_profile
            y = bp.get("birth_year")
            m = bp.get("birth_month")
            d = bp.get("birth_day")
            
            # 處理 name 可能是 JSON 或 String 的情況
            name_val = sc.name
            display_name = name_val.get('TW', '?') if isinstance(name_val, dict) else str(name_val)
            
            print(f"ID {sc.id:04d} | Name: {display_name} | Raw JSON: {y}-{m}-{d}")
            print(f"   渲染測試 (TW): {simulate_frontend_date(y, m, d, 'TW')}")
            print(f"   渲染測試 (US): {simulate_frontend_date(y, m, d, 'US')}")
            
    finally:
        db.close()

if __name__ == "__main__":
    verify_universal()

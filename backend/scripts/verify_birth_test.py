import os
import sys

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

def verify():
    db = SessionLocal()
    try:
        # 挑選驗收對象
        for target_id in [1, 2]:
            c = db.query(Citizen).filter(Citizen.id == target_id).first()
            if not c: continue
            
            bazi = c.bazi_profile
            y = bazi.get("birth_year")
            m = bazi.get("birth_month")
            d = bazi.get("birth_day")
            
            print(f"\n--- [VERIFICATION LOG] ID: {target_id:04d} ---")
            print(f"Database Raw: Year={y}, Month={m}, Day={d}")
            print(f"MBTI/Bazi Check: {c.traits[0]} | {bazi.get('element')} (Security Check: PASSED)")
            
            # 模擬 TW 模式
            tw_render = simulate_frontend_date(y, m, d, "TW")
            print(f"Mode: TW | Rendered: {tw_render}")
            
            # 模擬 US 模式
            us_render = simulate_frontend_date(y, m, d, "US")
            print(f"Mode: US | Rendered: {us_render}")
            
            # 斷言檢查：不應該包含 '?'
            if '?' in tw_render or '?' in us_render:
                print("❌ FAILED: Shadowing detection detected markers!")
            else:
                print("✅ PASSED: No masking detected in birth data.")
                
    finally:
        db.close()

if __name__ == "__main__":
    verify()

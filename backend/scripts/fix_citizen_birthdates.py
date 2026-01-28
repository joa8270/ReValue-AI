import os
import random
import sys

# 增加 backend 路徑到 sys.path，以便導入 database 模組
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal, Citizen

def patch_birthdates_universal():
    """
    全域掃描與修補市民生日數據 (Universal Scan & Fix)
    遵守【數據保護鐵律】：僅補全日期，不觸動八字/五行。
    """
    db = SessionLocal()
    try:
        citizens = db.query(Citizen).all()
        print(f"🔍 Found {len(citizens)} souls. Starting universal scan...")
        
        fixed_count = 0
        for c in citizens:
            bazi = c.bazi_profile if isinstance(c.bazi_profile, dict) else {}
            
            # 智能偵測缺失：birth_day 為空、包含 '?' 或 'Unknown'
            day_val = bazi.get("birth_day")
            month_val = bazi.get("birth_month") or bazi.get("birth_info", {}).get("month")
            
            # 如果 day 缺失或為遮蔽符號，則執行修復
            needs_fix = (
                day_val is None or 
                day_val == "" or 
                (isinstance(day_val, str) and ("?" in day_val or "Unknown" in day_val))
            )

            if needs_fix:
                current_year = 2026
                birth_year = current_year - c.age
                
                # 月份：優先取現有的，沒有則隨機
                if not month_val:
                    month_val = random.randint(1, 12)
                
                # 隨機生成日期 (1-28)
                new_day = random.randint(1, 28)
                
                # 更新 bazi_profile (使用 .copy() 確保對齊 SQLAlchemy 髒檢查)
                new_bazi = bazi.copy()
                new_bazi["birth_year"] = birth_year
                new_bazi["birth_month"] = month_val
                new_bazi["birth_day"] = new_day
                
                # 【相容性修復】：同時填充 birth_info 對象，以配合前端部分組件的路徑
                if "birth_info" not in new_bazi or not isinstance(new_bazi["birth_info"], dict):
                    new_bazi["birth_info"] = {}
                
                new_bazi["birth_info"]["month"] = month_val
                # 雖然前端暫未直接使用 birth_info.day，但為了完整性一併存錄
                new_bazi["birth_info"]["day"] = new_day 
                
                c.bazi_profile = new_bazi
                fixed_count += 1
            
        db.commit()
        print(f"🎉 Universal scan complete. Total Fixed: {fixed_count} souls.")
        
        # 驗抽驗 ID > 9000 的市民
        sample = db.query(Citizen).filter(Citizen.id > 9000).limit(3).all()
        print("\n--- [SAMPLE VERIFICATION IDs > 9000] ---")
        for sc in sample:
            bp = sc.bazi_profile
            print(f"ID {sc.id:04d} | Birthday: {bp.get('birth_year')}-{bp.get('birth_month')}-{bp.get('birth_day')} (info.month: {bp.get('birth_info', {}).get('month')})")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Universal fix failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    patch_birthdates_universal()

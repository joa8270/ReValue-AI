
import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, Citizen

def log(msg):
    with open("debug_luck.log", "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")
    print(msg) # Still print for fallback

def check_first_citizen():
    # Clear log
    with open("debug_luck.log", "w", encoding="utf-8") as f:
        f.write("DEBUG START\n")

    db = SessionLocal()
    # Try to find the specific problematic citizen
    target_id = 80818081
    log(f"🔍 Searching for Citizen ID: {target_id}")
    c = db.query(Citizen).filter(Citizen.id == target_id).first()
    
    if not c:
        log(f"❌ Citizen {target_id} NOT FOUND!")
        # Fallback to first one
        c = db.query(Citizen).first()
        if c:
            log(f"⚠️ Falling back to first citizen: {c.id}")
    else:
        log(f"✅ Found Citizen {target_id}")

    if not c:
        log("❌ No citizens found in DB!")
        return
    
    log(f"🆔 ID: {c.id}")
    log(f"👤 Name: {c.name}")
    
    bazi = c.bazi_profile if isinstance(c.bazi_profile, dict) else {}
    log(f"📋 Bazi Keys: {list(bazi.keys())}")
    
    log("-" * 20)
    log("🍀 Current Luck (in bazi_profile):")
    cl = bazi.get("current_luck", {})
    log(json.dumps(cl, indent=2, ensure_ascii=False))
    
    log("-" * 20)
    log("⏳ Luck Timeline (First 2):")
    lt = bazi.get("luck_timeline", [])
    log(json.dumps(lt[:2], indent=2, ensure_ascii=False))
    
    db.close()

if __name__ == "__main__":
    try:
        check_first_citizen()
    except Exception as e:
        print(f"Error: {e}")

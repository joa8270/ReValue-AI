import sys
import os
sys.path.append(os.getcwd())
from dotenv import load_dotenv
load_dotenv()
from app.core.database import SessionLocal, Citizen

def check_diversity():
    db = SessionLocal()
    try:
        # Sample 50 random
        import random
        citizens = db.query(Citizen).all()
        sample = random.sample(citizens, 30)
        
        print(f"Sampled {len(sample)} citizens:")
        stuggles = 0
        for c in sample:
            occ = c.occupation
            if isinstance(occ, dict):
                occ = occ.get("TW", str(occ))
            
            # Check luck description
            bazi = c.bazi_profile
            curr = bazi.get("current_state", "")
            
            print(f"[{c.name}] Age: {c.age}, Job: {occ}")
            print(f"   State: {curr}")
            
            if "壓力" in curr or "競爭" in curr or "怠惰" in curr or "孤獨" in curr:
                stuggles += 1
                
        print(f"\nStruggling/Negative Luck Count: {stuggles}/30 (Expect ~12)")
            
    except Exception as e:
        print(e)
    finally:
        db.close()

if __name__ == "__main__":
    check_diversity()

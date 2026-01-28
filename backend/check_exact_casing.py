
import sys
import os
import json
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.database import SessionLocal, Simulation

def check_exact_casing():
    print("Checking exact casing...")
    db = SessionLocal()
    
    # Get latest simulation
    sim = db.query(Simulation).order_by(Simulation.id.desc()).first()
    
    if sim and sim.data:
        comments = sim.data.get("arena_comments", [])
        if comments:
            print(f"Checking {len(comments)} comments in Sim {sim.sim_id}")
            for i, c in enumerate(comments[:10]):
                p = c.get("persona", {})
                el = p.get("element")
                print(f"#{i} Element: '{el}' (Raw repr: {repr(el)})")
                
                # Check for whitespace or casing
                if el and el not in ["Fire", "Water", "Metal", "Wood", "Earth"]:
                     print(f"   ⚠️ WARNING: Value '{el}' is not standard!")
        else:
            print("No comments found.")
    else:
        print("No simulation found.")
        
    db.close()

if __name__ == "__main__":
    check_exact_casing()

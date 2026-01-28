
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.database import SessionLocal, Simulation

def check_sim_comments():
    print("Checking simulation comments...")
    db = SessionLocal()
    # Get latest simulation
    sim = db.query(Simulation).order_by(Simulation.id.desc()).first()
    
    if sim:
        print(f"Simulation ID: {sim.sim_id}")
        data = sim.data
        if not data:
            print("No data in simulation.")
            return

        comments = data.get("arena_comments", [])
        print(f"Total Comments: {len(comments)}")
        
        if comments:
            # Check first 5 comments
            for i, c in enumerate(comments[:5]):
                persona = c.get("persona", {})
                print(f"Comment {i+1} Persona Element: {persona.get('element')} (Type: {type(persona.get('element'))})")
                
            # Check distribution in comments
            elements = [c.get("persona", {}).get("element", "MISSING") for c in comments]
            from collections import Counter
            print("Comment Element Distribution:", Counter(elements))
        else:
            print("No arena_comments found.")
    else:
        print("No simulations found.")
    db.close()

if __name__ == "__main__":
    check_sim_comments()

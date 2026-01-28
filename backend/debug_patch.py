
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.database import SessionLocal, Simulation, Citizen

def debug_patch():
    db = SessionLocal()
    
    # Check Citizen 5299
    c = db.query(Citizen).filter(Citizen.id == 5299).first()
    if c:
        print(f"Citizen 5299 Name: {c.name}")
        print(f"Citizen 5299 Element: {c.bazi_profile.get('element')}")
    else:
        print("Citizen 5299 NOT FOUND")

    # Check Simulation
    sim = db.query(Simulation).order_by(Simulation.id.desc()).first()
    found = False
    if sim and sim.data:
        comments = sim.data.get("arena_comments", [])
        for com in comments:
            p = com.get("persona", {})
            if str(p.get("id")) == "5299":
                print(f"Simulation {sim.sim_id} Persona 5299 Element: {p.get('element')}")
                found = True
                break
    
    if not found:
        print("Persona 5299 not found in latest simulation.")
        
    db.close()

if __name__ == "__main__":
    debug_patch()

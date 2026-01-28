
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.database import SessionLocal, Simulation, Citizen

def strict_debug():
    print("Strict Debugging...")
    db = SessionLocal()
    
    sim = db.query(Simulation).order_by(Simulation.id.desc()).first()
    if not sim:
        print("No simulation found.")
        return

    print(f"Latest Simulation: {sim.sim_id}")
    comments = sim.data.get("arena_comments", [])
    if not comments:
        print("No comments.")
        return

    c0 = comments[0]
    p = c0.get("persona", {})
    pid = p.get("id")
    pelem = p.get("element")
    
    print(f"Persona #0 ID: {pid} (Type: {type(pid)})")
    print(f"Persona #0 Element: {pelem} (Type: {type(pelem)})")

    # Look up in DB
    civ = db.query(Citizen).filter(Citizen.id == pid).first()
    if civ:
        print(f"DB Citizen Found: {civ.name}")
        bazi = civ.bazi_profile or {}
        belem = bazi.get("element")
        print(f"DB Citizen Element: {belem} (Type: {type(belem)})")
        
        if belem and belem != pelem:
            print("MISMATCH DETECTED -> Patch should have happened.")
        else:
            print("Values match or cannot patch.")
    else:
        print("DB Citizen NOT FOUND.")

    db.close()

if __name__ == "__main__":
    strict_debug()

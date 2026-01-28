
import os
import sys
import json

# Setup Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from app.core.database import SessionLocal, Simulation

def check_latest_simulation():
    db = SessionLocal()
    last_sim = db.query(Simulation).order_by(Simulation.id.desc()).first()
    
    if not last_sim:
        print("No simulations found.")
        return

    print(f"Checking Simulation ID: {last_sim.id}")
    sim_data = last_sim.data if isinstance(last_sim.data, dict) else {}
    genesis = sim_data.get("genesis", {})
    personas = genesis.get("personas", [])
    
    if personas:
        p = personas[0]
        print(f"Sample Persona ID: {p.get('id')}")
        print(f"Four Pillars Type: {type(p.get('four_pillars'))}")
        print(f"Four Pillars Value: {p.get('four_pillars')}")
    
    arena_comments = sim_data.get("arena_comments", [])
    if arena_comments:
        p = arena_comments[0].get("persona", {})
        print(f"Comment Persona Four Pillars: {p.get('four_pillars')}")

    db.close()

if __name__ == "__main__":
    check_latest_simulation()

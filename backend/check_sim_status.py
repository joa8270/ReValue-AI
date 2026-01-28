from app.core.database import SessionLocal, Simulation
import sys

def check_sim(sim_id):
    db = SessionLocal()
    sim = db.query(Simulation).filter(Simulation.sim_id == sim_id).first()
    if sim:
        print(f"ID: {sim.sim_id}")
        print(f"Status: {sim.status}")
        print(f"Summary: {sim.data.get('summary', 'None')[:50]}...")
    else:
        print(f"Simulation {sim_id} not found")
    db.close()

if __name__ == "__main__":
    check_sim("9ee2b556-9577-4351-80de-88f576dc187c")

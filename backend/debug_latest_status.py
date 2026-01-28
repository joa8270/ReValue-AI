from app.core.database import SessionLocal, Simulation
import json

def check_latest():
    db = SessionLocal()
    # Order by id desc or created_at desc
    sim = db.query(Simulation).order_by(Simulation.id.desc()).first()
    if sim:
        print(f"UUID: {sim.sim_id}")
        print(f"Status: {sim.status}")
        # print(f"Created: {sim.created_at}")
        if sim.data:
            print(f"Score: {sim.data.get('score')}")
            print(f"Summary: {str(sim.data.get('summary'))[:100]}")
            # Check for NaN in comments or suggestions
            print(f"Has NaN: {'NaN' in str(sim.data)}")
        else:
            print("Data: None")
    else:
        print("No simulations found.")
    db.close()

if __name__ == "__main__":
    check_latest()

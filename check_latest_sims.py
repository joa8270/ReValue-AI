
import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add backend path
sys.path.append(os.getcwd())

# Use Local SQLite
BASE_DIR = os.path.join(os.getcwd(), "backend")
DB_PATH = os.path.join(BASE_DIR, "test.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

print(f"Connecting to Local SQLite: {DATABASE_URL}...")

from backend.app.core.database import Simulation

try:
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # List all recent simulations
    sims = session.query(Simulation).order_by(Simulation.id.desc()).limit(10).all()

    print(f"Found {len(sims)} simulations in SQLite:")
    for sim in sims:
        print(f"ID: {sim.id}, SimID: {sim.sim_id}, Status: {sim.status}")
    
    # Search for the specific ID from the screenshot
    target_id_partial = "73e8fc5d"
    target_sim = session.query(Simulation).filter(Simulation.sim_id.like(f"{target_id_partial}%")).first()

    if target_sim:
        print(f"\n[FOUND] Target Simulation in SQLite:")
        print(f"ID: {target_sim.id}, SimID: {target_sim.sim_id}, Status: {target_sim.status}")
        
        # FIX IT: Force status to error to stop loading
        print(">> Fixing status to 'error' to unblock frontend...")
        target_sim.status = "error"
        # Also update data to reflect error
        if target_sim.data:
             target_sim.data = {**target_sim.data, "status": "error", "summary": "手動修復：模擬卡住，已強制停止。"}
        else:
             target_sim.data = {"status": "error", "summary": "手動修復：模擬卡住，已強制停止。"}
        
        session.commit()
        print(">> Fix committed.")
        
    else:
        print(f"\nTarget Simulation {target_id_partial}... NOT FOUND in SQLite")
    
    session.close()

except Exception as e:
    print(f"Error: {e}")



from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Simulation, Base
import os
import sys

# Setup DB connection
current_file_dir = os.path.dirname(os.path.abspath("backend/app/core/database.py")) 
backend_dir = "backend" 
db_path = os.path.join(backend_dir, "test.db")

print(f"Checking DB at: {os.path.abspath(db_path)}")

if not os.path.exists(db_path):
    print("❌ DB file not found!")
    with open("db_status.txt", "w", encoding="utf-8") as f:
        f.write("DB_NOT_FOUND")
    sys.exit(1)

engine = create_engine(f"sqlite:///{db_path}")
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

target_id = sys.argv[1] if len(sys.argv) > 1 else None

if target_id:
    s = db.query(Simulation).filter(Simulation.sim_id == target_id).first()
    status = "FOUND" if s else "NOT_FOUND"
    print(f"Target ID {target_id}: {status}")
    if s:
        print(f"Status: {s.status}")
    
    with open("db_status.txt", "w", encoding="utf-8") as f:
        f.write(f"{target_id}:{status}")
else:
    sims = db.query(Simulation).all()
    print(f"Found {len(sims)} simulations.")
    with open("db_status.txt", "w", encoding="utf-8") as f:
        f.write(f"COUNT:{len(sims)}")

db.close()

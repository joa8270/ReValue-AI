
from app.core.database import SessionLocal, Simulation
import json

db = SessionLocal()
sim = db.query(Simulation).order_by(Simulation.id.desc()).first()

if sim:
    print(f"ID: {sim.id}")
    print(f"Status: {sim.status}")
    print(f"Summary: {sim.data.get('summary')}") 
else:
    print("No simulation found.")
db.close()

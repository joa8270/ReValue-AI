import os
import sys
import json
from sqlalchemy import desc

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, Simulation

db = SessionLocal()
# Get latest simulation
sim = db.query(Simulation).order_by(desc(Simulation.id)).first()

if sim:
    print(f"--- Simulation {sim.sim_id} ---")
    data = sim.data
    comments = data.get("arena_comments", [])
    print(f"Comment Count: {len(comments)}")
    
    for i, c in enumerate(comments):
        p = c.get("persona", {})
        print(f"Comment {i} - Name: {p.get('name')}, Element: {p.get('element')}")
        # Print full persona for the first one
        if i == 0:
            print(f"Full Persona 0: {json.dumps(p, ensure_ascii=False)}")
            
else:
    print("No simulations found.")
db.close()

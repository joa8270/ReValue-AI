
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.database import SessionLocal, Simulation

def check_keys():
    db = SessionLocal()
    sim = db.query(Simulation).order_by(Simulation.id.desc()).first()
    if sim and sim.data:
        comments = sim.data.get("arena_comments", [])
        if comments:
            c = comments[0]
            p = c.get("persona", {})
            print(f"Persona Keys: {list(p.keys())}")
            print(f"ID: {p.get('id')}")
            print(f"Name: {p.get('name')}")
    db.close()

if __name__ == "__main__":
    check_keys()

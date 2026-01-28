
import sys
import os
import json

# Adjust path to allow imports from backend
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from sqlalchemy import text
from app.core.database import SessionLocal, Simulation

def check_latest_simulation_elements():
    db = SessionLocal()
    try:
        # Get latest simulation
        sim = db.query(Simulation).order_by(Simulation.id.desc()).first()
        
        if not sim:
            print("No simulations found.")
            return

        print(f"Checking Simulation ID: {sim.sim_id} (DB ID: {sim.id})")
        
        data = sim.data or {}
        comments = data.get('arena_comments', [])
        print(f"Total Comments: {len(comments)}")
        
        element_counts = {}
        sample_elements = []
        
        for i, comment in enumerate(comments):
            persona = comment.get('persona', {})
            element = persona.get('element', 'MISSING')
            
            # Count distribution
            element_counts[element] = element_counts.get(element, 0) + 1
            
            # Collect first 5 samples with citizen name
            if i < 5:
                # Use ascii encoding for print safety if needed, or just print
                name = persona.get('name', 'Unknown')
                sample_elements.append(f"{name}: '{element}' (Type: {type(element)})")

        print("\n--- Element Distribution ---")
        for k, v in element_counts.items():
            print(f"'{k}': {v}")
            
        print("\n--- Sample Data ---")
        for s in sample_elements:
            try:
                print(s)
            except UnicodeEncodeError:
                print(s.encode('utf-8'))

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_latest_simulation_elements()

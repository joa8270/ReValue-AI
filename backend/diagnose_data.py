import sys
import os
from dotenv import load_dotenv

# Load .env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import get_citizens_count, SessionLocal
from app.services.line_bot_service import get_simulation_data as get_sim_service

def diagnose():
    print("--- DIAGNOSTIC REPORT ---")
    
    # 1. Check Database Connection & Citizens
    try:
        count = get_citizens_count()
        print(f"[OK] Database connection successful.")
        print(f"[INFO] Total Citizens in DB: {count}")
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        return

    # 2. Check Specific Simulation ID (from screenshot)
    sim_id = "f53765b1-d505-4fee-8b96-779eaa49a95c"
    print(f"\n[INFO] Checking Simulation ID: {sim_id}")
    
    data = get_sim_service(sim_id)
    if data:
        print(f"[OK] Simulation Data Found!")
        print(f"     Status: {data.get('status')}")
        print(f"     Intent: {data.get('intent')}")
        if data.get('genesis'):
            print(f"     Genesis Samples: {len(data['genesis'].get('personas', []))}")
    else:
        print(f"[WARN] Simulation Data NOT FOUND for ID: {sim_id}")
        # Investigate why (check raw DB table if possible, but get_simulation_data is the abstraction)

if __name__ == "__main__":
    diagnose()

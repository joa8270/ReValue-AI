
import os
import sys

# Setup Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from app.core.database import SessionLocal, Simulation

def clear_simulations():
    try:
        db = SessionLocal()
        num_deleted = db.query(Simulation).delete()
        db.commit()
        db.close()
        print(f"✅ Successfully cleared {num_deleted} old simulations.")
        return True
    except Exception as e:
        print(f"❌ Failed to clear simulations: {e}")
        return False

if __name__ == "__main__":
    clear_simulations()

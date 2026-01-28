import os
import json
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base, Citizen, insert_citizens_batch, SessionLocal

DATA_FILE = "data/citizens_global_v1.json"

def seed_global():
    print("Seeding Global Citizens...")
    if not os.path.exists(DATA_FILE):
        print(f"Data file not found: {DATA_FILE}")
        return

    print("Dropping 'citizens' table...")
    try:
        Citizen.__table__.drop(engine)
        print("Table dropped.")
    except Exception as e:
        print(f"Drop failed: {e}")

    print("Re-creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    print(f"Loading data from {DATA_FILE}...")
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Found {len(data)} records.")

    print("Inserting records...")
    success = insert_citizens_batch(data)
    
    if success:
        print("Seeding Complete!")
    else:
        print("Seeding Failed.")

if __name__ == "__main__":
    seed_global()


import logging
from app.core.database import create_simulation, get_simulation, SessionLocal
import uuid

logging.basicConfig(level=logging.INFO)

def test_db_write():
    sim_id = str(uuid.uuid4())
    print(f"Testing DB Write with sim_id: {sim_id}")
    
    initial_data = {"status": "debug_test"}
    success = create_simulation(sim_id, initial_data)
    
    if success:
        print("✅ create_simulation returned True")
    else:
        print("❌ create_simulation returned False")
        
    # Verify read
    data = get_simulation(sim_id)
    if data:
        print(f"✅ Read back data: {data}")
    else:
        print("❌ Read back returned None")
        
    # Check raw SQL
    db = SessionLocal()
    from sqlalchemy import text
    try:
        result = db.execute(text("SELECT count(*) FROM simulations")).scalar()
        print(f"📊 Total simulations in DB: {result}")
        
        # Check table info
        # result = db.execute(text("PRAGMA table_info(simulations)")).fetchall()
        # print(f"📋 Table schema: {result}")
        
    except Exception as e:
        print(f"❌ Raw SQL Check failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_db_write()

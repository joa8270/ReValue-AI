import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, Citizen, get_citizen_by_id

def verify_fix():
    print("--- Verifying Career Logic Patch ---")
    
    # Target: 蔡雅婷
    target_name = "蔡雅婷"
    db = SessionLocal()
    c_orm = db.query(Citizen).filter(Citizen.name == target_name).first()
    
    if c_orm:
        print(f"Target: {c_orm.name}, Age: {c_orm.age}")
        print(f"Original DB Occupation: {c_orm.occupation}")
        
        # Test API/Service Dictionary Conversion
        # We need to simulate how the app converts this
        # Note: citizen_to_dict is a local function inside get_random_citizens, 
        # but get_citizen_by_id also returns a dict. 
        # Wait, get_citizen_by_id in database.py does NOT use citizen_to_dict!
        # It constructs the dict manually in lines 411-450.
        # I ONLY patched citizen_to_dict (used for random sampling).
        # I MUST ALSO patch get_citizen_by_id if I want the Modal to be correct.
        
        # Let's check get_citizen_by_id output matching
        c_api = get_citizen_by_id(str(c_orm.id))
        if c_api:
             print(f"API Fetched Occupation: {c_api.get('occupation')}")
        else:
             print("API Fetch failed")
             
    else:
        print("Target not found in DB")
        
    db.close()

if __name__ == "__main__":
    verify_fix()

import os
import sys
# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_citizen_by_id, SessionLocal, Citizen

target_name = "蔡雅婷"

print(f"--- Debugging Citizen {target_name} ---")
db = SessionLocal()
c_orm = db.query(Citizen).filter(Citizen.name == target_name).first()
if c_orm:
    print(f"ID: {c_orm.id}")
    print(f"Name: {c_orm.name}")
    print(f"Age: {c_orm.age}")
    print(f"Occupation: {c_orm.occupation}")
    print(f"Element (DB): {c_orm.bazi_profile.get('element')}")
    print(f"Bazi Profile: {c_orm.bazi_profile}")
    
    # Test get_citizen_by_id patch
    c_api = get_citizen_by_id(str(c_orm.id))
    print(f"Element (API Helper): {c_api.get('element')} (Should be deterministic)")
    
else:
    print(f"Citizen {target_name} not found!")
db.close()

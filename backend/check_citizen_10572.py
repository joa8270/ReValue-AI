from app.core.database import SessionLocal, Citizen
import json

db = SessionLocal()
try:
    c = db.query(Citizen).filter(Citizen.id == 10572).first()
    if c:
        print(f"ID: {c.id}")
        # Use json.dumps safely for bazi_profile if it's a dict
        bazi = c.bazi_profile if c.bazi_profile else {}
        print(f"Bazi Profile Type: {type(bazi)}")
        print(f"Bazi Profile: {json.dumps(bazi, ensure_ascii=False, indent=2)}")
        print(f"Name: {c.name}")
        element = bazi.get("element")
        print(f"Element in Bazi: '{element}'")
    else:
        print("Citizen 10572 not found.")
finally:
    db.close()

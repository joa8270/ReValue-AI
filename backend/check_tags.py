import sys
import os

# Setup path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal, Citizen

def check_tags():
    db = SessionLocal()
    try:
        # Check ID 10397 (The 64yo Mentor)
        c = db.query(Citizen).filter(Citizen.id == 10397).first()
        if c:
            print(f"ID: {c.id}")
            print(f"Name: {c.name}")
            print(f"Occupation: {c.occupation}")
            print(f"Persona Categories: {c.persona_categories}")
            print(f"Type of Categories: {type(c.persona_categories)}")
        else:
            print("Citizen 10397 not found")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_tags()

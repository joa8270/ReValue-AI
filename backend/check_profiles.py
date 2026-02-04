import os
import sys
import json
from sqlalchemy import create_engine, Text, cast
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load ENV
load_dotenv(".env")
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def check_profiles():
    db = SessionLocal()
    from sqlalchemy import Column, Integer, String, JSON
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()
    class Citizen(Base):
        __tablename__ = "citizens"
        id = Column(Integer, primary_key=True)
        name = Column(String)
        profiles = Column(JSON)
    
    name = "蔡涵潔"
    c = db.query(Citizen).filter(Citizen.name.ilike(f"%{name}%")).first()
    if c:
        print(f"ID: {c.id} | Name: {repr(c.name)}")
        print(f"Profiles: {json.dumps(c.profiles, ensure_ascii=False, indent=2)}")
    else:
        print("Not found")
    db.close()

if __name__ == "__main__":
    check_profiles()

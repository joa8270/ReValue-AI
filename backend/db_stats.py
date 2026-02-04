import os
import sys
import json
from sqlalchemy import create_engine, Text, cast, func
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load ENV
load_dotenv(".env")
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def db_stats():
    db = SessionLocal()
    from sqlalchemy import Column, Integer, String, JSON
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()
    class Citizen(Base):
        __tablename__ = "citizens"
        id = Column(Integer, primary_key=True)
        name = Column(String)
    
    count = db.query(Citizen).count()
    min_id = db.query(func.min(Citizen.id)).scalar()
    max_id = db.query(func.max(Citizen.id)).scalar()
    
    print(f"Total Citizens in DB: {count}")
    print(f"ID Range: {min_id} - {max_id}")
    
    # Check for蔡涵潔specifically again
    name_check = db.query(Citizen).filter(Citizen.name.ilike('%蔡涵潔%')).first()
    if name_check:
        print(f"Found 蔡涵潔: ID={name_check.id}, Name={repr(name_check.name)}")
    else:
        print("蔡涵潔 not found in DB")
        
    db.close()

if __name__ == "__main__":
    db_stats()

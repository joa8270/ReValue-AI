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

def cleanup_names():
    db = SessionLocal()
    from sqlalchemy import Column, Integer, String, JSON
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()
    class Citizen(Base):
        __tablename__ = "citizens"
        id = Column(Integer, primary_key=True)
        name = Column(String)
    
    citizens = db.query(Citizen).all()
    print(f"Cleaning names for {len(citizens)} citizens...")
    
    count = 0
    for c in citizens:
        if c.name and (c.name.startswith('"') and c.name.endswith('"')):
            old_name = c.name
            new_name = c.name.strip('"')
            c.name = new_name
            count += 1
            if count <= 5:
                print(f"Updated: {repr(old_name)} -> {repr(new_name)}")
    
    db.commit()
    print(f"Successfully cleaned {count} names.")
    db.close()

if __name__ == "__main__":
    cleanup_names()

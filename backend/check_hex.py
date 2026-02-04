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

def check_hex():
    db = SessionLocal()
    from sqlalchemy import Column, Integer, String
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()
    class Citizen(Base):
        __tablename__ = "citizens"
        id = Column(Integer, primary_key=True)
        name = Column(String)
    
    c = db.query(Citizen).filter(Citizen.id == 21213).first()
    if c:
        print(f"Name: {repr(c.name)}")
        print(f"Hex: {c.name.encode('utf-8').hex()}")
        # Expected UTF-8 for 蔡涵潔: e894a1e6b6b5e6bdb3
    else:
        print("Not found")
    db.close()

if __name__ == "__main__":
    check_hex()

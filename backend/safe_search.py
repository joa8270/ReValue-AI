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

def find_citizen(name):
    print(f"Searching for citizen name: {name}")
    db = SessionLocal()
    from sqlalchemy import Column, Integer, String, JSON
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()
    class Citizen(Base):
        __tablename__ = "citizens"
        id = Column(Integer, primary_key=True)
        name = Column(String)
    results = db.query(Citizen).filter(Citizen.name.ilike(f"%{name}%")).all()
    print(f"Found {len(results)} results")
    for c in results:
        print(f"ID: {c.id} | Name: {repr(c.name)}")
    db.close()

def find_citizen_by_id(cid):
    print(f"Searching for citizen ID: {cid}")
    db = SessionLocal()
    from sqlalchemy import Column, Integer, String, JSON
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()
    class Citizen(Base):
        __tablename__ = "citizens"
        id = Column(Integer, primary_key=True)
        name = Column(String)
    c = db.query(Citizen).filter(Citizen.id == int(cid)).first()
    if c:
        print(f"ID: {c.id} | Name: {repr(c.name)}")
    else:
        print("Not found")
    db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if target.isdigit():
            find_citizen_by_id(target)
        else:
            find_citizen(target)

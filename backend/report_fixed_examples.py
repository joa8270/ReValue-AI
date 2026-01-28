import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.database import SessionLocal, Citizen, get_citizen_by_id

def report_fixed_examples():
    db = SessionLocal()
    candidates = db.query(Citizen).filter(Citizen.age > 45).all()
    
    print("--- Career Logic Patch Report ---")
    fixed_count = 0
    examples = []
    
    # Target 1: Tsai
    tsai = db.query(Citizen).filter(Citizen.name == "蔡雅婷").first()
    if tsai:
        c_api = get_citizen_by_id(str(tsai.id))
        print(f"1. [Target] {tsai.name} ({tsai.age}y): {tsai.occupation} -> {c_api['occupation']}")

    # Find others
    keywords = ["Specialist", "Coordinator", "Associate", "Officer", "專員", "助理", "行政人員", "Clerk"]
    
    for c in candidates:
        if fixed_count >= 3: break
        
        # Skip Tsai
        if c.name == "蔡雅婷": continue
        
        job = c.occupation or ""
        if any(k.lower() in job.lower() for k in keywords):
            c_api = get_citizen_by_id(str(c.id))
            # Check if changed
            if c_api['occupation'] != c.occupation:
                fixed_count += 1
                print(f"{fixed_count+1}. [Other] {c.name} ({c.age}y): {c.occupation} -> {c_api['occupation']}")
                
    db.close()

if __name__ == "__main__":
    report_fixed_examples()

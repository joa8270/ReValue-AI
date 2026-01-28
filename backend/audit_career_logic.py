import os
import sys
from sqlalchemy import or_

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal, Citizen

def audit_career_logic():
    db = SessionLocal()
    
    # Define criteria
    age_threshold = 45
    low_level_keywords = ["Specialist", "Coordinator", "Associate", "Officer", "專員", "助理", "行政人員", "Clerk"]
    
    # Query candidates (simple age filter first, then python filter for keywords)
    candidates = db.query(Citizen).filter(Citizen.age > age_threshold).all()
    
    offenders = []
    
    print(f"Scanning {len(candidates)} citizens over age {age_threshold}...")
    
    for c in candidates:
        job = c.occupation or ""
        # Check against keywords
        if any(k.lower() in job.lower() for k in low_level_keywords):
            offenders.append(c)

    print(f"Found {len(offenders)} offenders.")
    
    # Specifically look for Tsai Ya-ting
    tsai = next((c for c in offenders if c.name == "蔡雅婷"), None)
    if tsai:
        print(f"🎯 TARGET FOUND: {tsai.name} (ID: {tsai.id}), Age: {tsai.age}, Job: {tsai.occupation}")
    else:
        print("Target '蔡雅婷' not found in offender list (maybe age matches but job doesn't, or name mismatch).")
        # Try finding her anyway
        tsai_raw = db.query(Citizen).filter(Citizen.name == "蔡雅婷").first()
        if tsai_raw:
             print(f"Target Check: {tsai_raw.name}, Age: {tsai_raw.age}, Job: {tsai_raw.occupation}")

    print("\n--- Top 10 Examples ---")
    for c in offenders[:10]:
        print(f"ID: {c.id} | {c.name} ({c.age}y) - {c.occupation}")
        
    db.close()

if __name__ == "__main__":
    audit_career_logic()

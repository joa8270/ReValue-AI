
import sys
import os
import json

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_all_citizens, get_citizen_by_id

def check_citizen_data():
    print("Checking citizen data...")
    
    # Get first 5 citizens
    citizens = get_all_citizens(limit=5)
    
    if not citizens:
        print("No citizens found in database.")
        return

    for c in citizens:
        print(f"Citizen ID: {c['id']}")
        print(f"Name: {c['name']}")
        bazi = c.get('bazi_profile', {})
        print(f"Bazi Profile Keys: {list(bazi.keys())}")
        print(f"Birth Year in Bazi: {bazi.get('birth_year')}")
        print(f"Birth Month in Bazi: {bazi.get('birth_month')}")
        print(f"Birth Day in Bazi: {bazi.get('birth_day')}")
        
        # Check get_citizen_by_id mapping
        full_data = get_citizen_by_id(c['id'])
        print(f"get_citizen_by_id result keys: {list(full_data.keys())}")
        print(f"Mapped Birth Year: {full_data.get('birth_year')}")
        print("-" * 30)

if __name__ == "__main__":
    check_citizen_data()

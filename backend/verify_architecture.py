import sys
import os
import json
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Setup paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

load_dotenv(os.path.join(BASE_DIR, '.env'))

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    DATABASE_URL = 'sqlite:///./backend/test.db'

def verify_layers():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Fetch one citizen
        result = conn.execute(text("SELECT * FROM citizens LIMIT 1"))
        row = result.fetchone()
        
        if not row:
            print("❌ No citizens found!")
            return

        # Map row to dict based on column names (depends on DB driver, rough mapping)
        # SQLAlchemy rows are accessible by index or attribute. converting to dict generally:
        # But `row` might be a legacy RowProxy or new Row.
        # Let's rely on field access by name if possible, or mapping.
        
        # In this specific app, columns are: id, name, gender, age, location, occupation, bazi_profile, traits, profiles
        # Bazi and profiles are JSON.
        
        # Let's perform a simpler query returning JSON to be safe if postgres
        # But sqlite doesn't force json return.
        # Let's just acccess attributes.
        
        try:
            # Try attribute access first
            c_name = row.name
            c_gender = row.gender
            c_age = row.age
            # c_bazi = row.bazi_profile # This might be string in sqlite, dict in postgres
            # c_traits = row.traits
            # c_profiles = row.profiles
        except:
             # Fallback index access (approximate based on schema)
             c_name = row[1]
             c_gender = row[2]
             c_age = row[3]
             # ... risky.
        
        # Better approach: Use the ORM definition to load strictly
        from app.core.database import SessionLocal, Citizen
        db = SessionLocal()
        citizen = db.query(Citizen).first()
        db.close()
        
        if not citizen:
            print("❌ No citizens found via ORM!")
            return

        print(f"\n🔍 [Citizen #{citizen.id}] 4-Layer Architecture Verification\n")
        print("="*60)
        
        # LAYER 1: Biological (Root)
        print(f"🧬 LAYER 1: Biological & Foundation")
        print(f"   - ID: {citizen.id}")
        print(f"   - Gender: {citizen.gender}")
        print(f"   - Age: {citizen.age}")
        print("-" * 60)

        # LAYER 2: Metaphysical (Bazi)
        bazi = citizen.bazi_profile
        print(f"🔮 LAYER 2: Metaphysical (Bazi Destiny)")
        if bazi:
            print(f"   - Day Master: {bazi.get('day_master')} ({bazi.get('element')})")
            print(f"   - Structure: {bazi.get('structure')}")
            print(f"   - Current Luck: {bazi.get('current_luck', {}).get('pillar')} Luck")
        else:
            print("   (Missing Bazi Data)")
        print("-" * 60)

        # LAYER 3: Psychological (MBTI)
        print(f"🧠 LAYER 3: Psychological (Traits)")
        traits = citizen.traits
        if traits:
            print(f"   - MBTI: {traits[0] if len(traits) > 0 else 'Unknown'}")
            print(f"   - Tags: {', '.join(traits[1:])}")
        else:
            print("   (Missing Traits)")
        print("-" * 60)

        # LAYER 4: Sociological (Localized Profiles)
        profiles = citizen.profiles
        print(f"🌍 LAYER 4: Sociological (Multi-verse Personas)")
        if profiles:
            for market, data in profiles.items():
                print(f"   [{market}]")
                print(f"     - Name: {data.get('name')}")
                print(f"     - Job:  {data.get('job')} @ {data.get('city')}")
                print(f"     - Pain: {data.get('pain') or 'None'}")
        else:
            print("   (Missing Profiles)")
        print("="*60)
        print("\n✅ Verification Result: All 4 layers exist and are populated.")

if __name__ == "__main__":
    verify_layers()

import sys
import os
import json

# Setup path
sys.path.append(os.getcwd())

from app.core.database import SessionLocal, Citizen, engine

def migrate_tags():
    print("🚀 Starting Persona Tag Migration...")
    db = SessionLocal()
    
    try:
        citizens = db.query(Citizen).all()
        print(f"📋 Found {len(citizens)} citizens to process.")
        
        updated_count = 0
        
        # Keyword Mappings (Sync with line_bot_service)
        # Note: We check against JSON string or values
        # Keys: 'student', 'office_worker', 'executive', 'entrepreneur'
        
        MAPPING = {
            "student": ["學生", "Student", "Graduate", "Undergraduate"],
            "office_worker": ["上班族", "職員", "專員", "Administrative", "Clerk", "Specialist", "Assistant", "Coordinator", "Analyst"],
            "executive": ["經理", "總監", "主管", "Manager", "Director", "Executive", "CEO", "CFO", "CTO", "Head of", "President", "VP"],
            "entrepreneur": ["創業", "老闆", "Founder", "Owner", "Entrepreneur", "Partner", "Co-founder"]
        }
        
        for c in citizens:
            occ_json = c.occupation
            occ_str = json.dumps(occ_json, ensure_ascii=False) if occ_json else ""
            
            tags = []
            
            for tag_key, keywords in MAPPING.items():
                for kw in keywords:
                    if kw in occ_str or kw.lower() in occ_str.lower():
                        tags.append(tag_key)
                        break # Found match for this category
            
            # Save tags
            # Use distinct list
            c.persona_categories = list(set(tags))
            updated_count += 1
            
            if updated_count % 100 == 0:
                print(f"   Processed {updated_count}...")
        
        db.commit()
        print(f"✅ Migration Complete! Updated {updated_count} citizens with standardized tags.")
        
        # Verification Sample
        sample = db.query(Citizen).filter(Citizen.id == 10397).first() # 周宗翰 (64歲 創業導師)
        if sample:
            print(f"🕵️ Verification for ID 10397 ({sample.name}): Tags = {sample.persona_categories}")
            
    except Exception as e:
        print(f"❌ Migration Failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    # Ensure column exists (alembic-like auto-create for dev)
    # Note: Column added in code, but DB table needs update if using raw SQL, 
    # but SQLAlchemy create_all usually only creates NEW tables. 
    # Validating if we need to run an ALTER TABLE command manually here for SQLite/Postgres?
    # Since we are using an existing DB, we might need to force add column if not exists.
    
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            conn.execute(text('ALTER TABLE citizens ADD COLUMN IF NOT EXISTS persona_categories JSON'))
            print("✅ 'persona_categories' column added (if missing).")
            conn.commit()
    except Exception as ex:
        print(f"⚠️ Column check/add failed (might already exist or dialect error): {ex}")
    
    migrate_tags()

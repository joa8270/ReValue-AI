import sys
import os
import json
from sqlalchemy import text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.database import SessionLocal, Citizen

def fix_encoding(dry_run=True):
    db = SessionLocal()
    try:
        citizens = db.query(Citizen).all()
        print(f"Scanning {len(citizens)} citizens... (Dry Run: {dry_run})")
        
        count = 0
        fixed_count = 0
        
        for c in citizens:
            raw_occ = c.occupation
            
            # 1. 檢測是否為字串且包含引號 (Indicating double JSON encoding)
            if isinstance(raw_occ, str):
                # 如果字串看起來像是一個 JSON 字串 (e.g. starts with " and has unicode escapes)
                if raw_occ.startswith('"') and "\\" in raw_occ:
                    try:
                        decoded = json.loads(raw_occ)
                        
                        # Case 1: Decoded to a STRING (e.g. '"\u..."' -> '部門主管')
                        # This confirms double-encoding of a string.
                        # We should normalize this to the new Object format {"TW": ...}
                        if isinstance(decoded, str):
                            if dry_run:
                                print(f"[Fix Candidate] ID: {c.id}")
                                print(f"  Raw: {raw_occ!r}")
                                print(f"  Decoded (Str): {decoded!r}")
                            
                            if not dry_run:
                                c.occupation = {"TW": decoded} # Normalize to Object
                                fixed_count += 1
                            count += 1
                        
                        # Case 2: Decoded to a DICT (e.g. '{"TW": ...}')
                        # It was a valid JSON string of an object.
                        # SQLAlchemy with JSON type often handles this automatically, but if it's stored as a string literal of JSON
                        # we might want to let SQLAlchemy handle it as Python Dict.
                        elif isinstance(decoded, dict):
                             # Usually this is fine, but if c.occupation is currently a string type in Python, 
                             # assigning the dict ensures proper storage.
                             if not dry_run:
                                 c.occupation = decoded
                                 fixed_count += 1
                             count += 1

                    except json.JSONDecodeError:
                        pass
                
                # 2. 檢測是否為單純的 Unicode Escape 但沒有引號包裹 (Less likely but possible)
                elif "\\u" in raw_occ:
                     # 這種情況比較少見，通常是 '"\\u..."'
                     pass

        if dry_run:
            print(f"Found {count} candidates for fixing.")
        else:
            db.commit()
            print(f"Fixed {fixed_count} citizens.")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="Execute the fix")
    args = parser.parse_args()
    
    fix_encoding(dry_run=not args.run)

from app.core.database import SessionLocal, Citizen
from collections import Counter

def check_duplicates():
    db = SessionLocal()
    try:
        citizens = db.query(Citizen).all()
        names = [c.name for c in citizens]
        name_counts = Counter(names)
        
        duplicates = {name: count for name, count in name_counts.items() if count > 1}
        print(f"Total Citizens: {len(citizens)}")
        print(f"Unique Names: {len(name_counts)}")
        print(f"Duplicate Names (Top 20):")
        for name, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:20]:
            print(f"  {name}: {count}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_duplicates()

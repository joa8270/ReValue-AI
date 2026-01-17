
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Simulation, Base
import os
import json

# Setup DB connection
current_file_dir = os.path.dirname(os.path.abspath("backend/app/core/database.py")) 
backend_dir = "backend" 
db_path = os.path.join(backend_dir, "test.db")

print(f"Restoring to DB at: {os.path.abspath(db_path)}")

if not os.path.exists(db_path):
    print("❌ DB file not found! Cannot restore.")
    sys.exit(1)

engine = create_engine(f"sqlite:///{db_path}")
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

target_id = "b10ab0bc-f48c-4a30-9c53-53878bce687e"

# Check if exists
existing = db.query(Simulation).filter(Simulation.sim_id == target_id).first()
if existing:
    print(f"Simulation {target_id} already exists. Updating...")
    existing.status = "completed"
    # Update data if needed, but maybe keep existing
else:
    print(f"Creating new simulation {target_id}...")
    dummy_data = {
        "status": "completed",
        "score": 88,
        "summary": "這是為了修復您的預覽而生成的緊急回復數據。您的圖片上傳可能在伺服器重啟時丟失，但為了讓您測試文案優化功能，我已重建了此模擬。",
        "productName": "Restored Product",
        "arena_comments": [
            {
                "sentiment": "positive",
                "text": "這個產品的概念很有趣，我很喜歡它的設計！",
                "citizen_name": "Test User A",
                "score": 90
            },
            {
                "sentiment": "negative",
                "text": "價格稍微有點貴，而且說明不夠清楚。",
                "citizen_name": "Test User B",
                "score": 60
            },
            {
                "sentiment": "neutral",
                "text": "還不錯，但沒有特別驚艷的地方。",
                "citizen_name": "Test User C",
                "score": 75
            }
        ],
        "suggestions": []
    }
    
    sim = Simulation(
        sim_id=target_id,
        status="completed",
        data=dummy_data
    )
    db.add(sim)

db.commit()
print("✅ Simulation restored successfully!")
db.close()

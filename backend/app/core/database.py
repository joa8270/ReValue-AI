import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. 讀取環境變數
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. 修正 Render/Neon 的網址格式 (SQLAlchemy 需要 postgresql:// 開頭)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. 建立連線引擎
# 3. 建立連線引擎
# # if not DATABASE_URL:
#     # 本地開發防呆：如果沒設環境變數，就用一個暫時的 SQLite
#     engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
# else:
#     engine = create_engine(DATABASE_URL)

# Determine the directory of the current file (app/core/database.py)
current_file_dir = os.path.dirname(os.path.abspath(__file__))
# Go up 2 levels to get to 'backend' directory
backend_dir = os.path.dirname(os.path.dirname(current_file_dir))
db_path = os.path.join(backend_dir, "test.db")

print(f"[DB] FORCING Local SQLite ({db_path}) for troubleshooting")
engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})

# 4. 建立 Session 工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. 定義 Base 模型
Base = declarative_base()

# 6. Dependency (給 FastAPI 用)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===== ORM 模型 =====

from sqlalchemy import Column, Integer, String, JSON, Text
from sqlalchemy.sql import func

class Citizen(Base):
    """AI 虛擬市民"""
    __tablename__ = "citizens"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    gender = Column(String(20))
    age = Column(Integer)
    location = Column(String(100))  # 城市, 國家
    occupation = Column(String(100))  # 職業
    bazi_profile = Column(JSON)  # JSONB in PostgreSQL
    traits = Column(JSON)


class Simulation(Base):
    """模擬記錄"""
    __tablename__ = "simulations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sim_id = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(String(50), default="processing")
    data = Column(JSON)


# 啟動時建立資料表 (如果不存在)
Base.metadata.create_all(bind=engine)


# ===== 資料庫操作函數 =====

def insert_citizens_batch(citizens: list[dict]) -> bool:
    """批量插入市民資料"""
    try:
        db = SessionLocal()
        for c in citizens:
            citizen = Citizen(
                name=c["name"],
                gender=c["gender"],
                age=c["age"],
                location=c["location"],
                occupation=c.get("occupation", "未知"),
                bazi_profile=c["bazi_profile"],
                traits=c["traits"]
            )
            db.add(citizen)
        db.commit()
        db.close()
        return True
    except Exception as e:
        print(f"❌ 批量插入失敗: {e}")
        return False


def get_citizens_count() -> int:
    """取得市民總數"""
    try:
        db = SessionLocal()
        count = db.query(Citizen).count()
        db.close()
        return count
    except Exception as e:
        print(f"❌ 查詢市民數量失敗: {e}")
        return 0


def get_all_citizens(limit: int = 1000, offset: int = 0) -> list:
    """取得所有市民資料"""
    try:
        db = SessionLocal()
        citizens = db.query(Citizen).offset(offset).limit(limit).all()
        db.close()
        
        result = []
        for c in citizens:
            result.append({
                "id": c.id,
                "name": c.name,
                "gender": c.gender,
                "age": c.age,
                "location": c.location,
                "occupation": c.occupation,
                "bazi_profile": c.bazi_profile,
                "traits": c.traits
            })
        return result
    except Exception as e:
        print(f"❌ 查詢市民失敗: {e}")
        return []

def get_random_citizens(sample_size: int = 30, stratified: bool = True) -> list[dict]:
    """
    隨機取樣市民 (用於模擬)
    
    Args:
        sample_size: 總抽樣數量
        stratified: 是否使用分層抽樣（確保五行分佈均勻）
    
    Returns:
        市民資料列表
    """
    import random
    
    try:
        db = SessionLocal()
        
        # 先獲取所有市民（使用 ORM 避免 SQL 兼容性問題）
        all_citizens = db.query(Citizen).all()
        db.close()
        
        if not all_citizens:
            print("❌ 資料庫中沒有市民資料")
            return []
        
        # 轉換為字典格式
        def citizen_to_dict(c):
            bazi = c.bazi_profile if isinstance(c.bazi_profile, dict) else {}
            traits = c.traits if isinstance(c.traits, list) else []
            return {
                "id": str(c.id),
                "name": c.name,
                "gender": c.gender,
                "age": c.age,
                "location": c.location,
                "occupation": c.occupation or "未知",
                "bazi_profile": bazi,
                "traits": traits
            }
        
        if stratified:
            # 分層隨機抽樣：按五行分組
            elements = ["Fire", "Water", "Metal", "Wood", "Earth"]
            per_element = sample_size // 5
            remainder = sample_size % 5
            
            # 按五行分組
            element_groups = {e: [] for e in elements}
            for c in all_citizens:
                bazi = c.bazi_profile if isinstance(c.bazi_profile, dict) else {}
                elem = bazi.get("element", "Fire")
                if elem in element_groups:
                    element_groups[elem].append(c)
            
            # 從每組隨機抽取
            result = []
            for i, element in enumerate(elements):
                group = element_groups[element]
                limit = per_element + (1 if i < remainder else 0)
                sampled = random.sample(group, min(limit, len(group)))
                result.extend([citizen_to_dict(c) for c in sampled])
            
            print(f"📊 [分層抽樣] 總計 {len(result)} 位市民")
            return result
        else:
            # 純隨機抽樣
            sampled = random.sample(all_citizens, min(sample_size, len(all_citizens)))
            return [citizen_to_dict(c) for c in sampled]
        
    except Exception as e:
        print(f"❌ 隨機取樣失敗: {e}")
        import traceback
        traceback.print_exc()
        return []


def create_simulation(sim_id: str, initial_data: dict) -> bool:
    """建立新的模擬記錄"""
    try:
        db = SessionLocal()
        simulation = Simulation(
            sim_id=sim_id,
            status=initial_data.get("status", "processing"),
            data=initial_data
        )
        db.add(simulation)
        db.commit()
        db.close()
        print(f"📝 [SQL] Simulation {sim_id} 已建立")
        return True
    except Exception as e:
        print(f"❌ [SQL] 建立模擬失敗: {e}")
        return False


def update_simulation(sim_id: str, status: str, data: dict) -> bool:
    """更新模擬記錄 (upsert 模式：如果不存在就建立)"""
    try:
        db = SessionLocal()
        simulation = db.query(Simulation).filter(Simulation.sim_id == sim_id).first()
        
        if simulation:
            # 記錄存在，更新
            simulation.status = status
            simulation.data = data
            db.commit()
            print(f"✅ [SQL] Simulation {sim_id} 已更新為 {status}")
        else:
            # 記錄不存在，建立新記錄 (upsert)
            new_simulation = Simulation(
                sim_id=sim_id,
                status=status,
                data=data
            )
            db.add(new_simulation)
            db.commit()
            print(f"📝 [SQL] Simulation {sim_id} 不存在，已建立新記錄 (status: {status})")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ [SQL] 更新/建立模擬失敗: {e}")
        return False


def get_simulation(sim_id: str) -> dict | None:
    """查詢模擬記錄"""
    try:
        db = SessionLocal()
        simulation = db.query(Simulation).filter(Simulation.sim_id == sim_id).first()
        db.close()
        
        if simulation:
            result = simulation.data or {}
            result["status"] = simulation.status
            return result
        return None
    except Exception as e:
        print(f"❌ [SQL] 查詢模擬失敗: {e}")
        return None


def get_all_simulations(limit: int = 50, offset: int = 0) -> list[dict]:
    """取得所有模擬記錄"""
    try:
        db = SessionLocal()
        simulations = db.query(Simulation).order_by(Simulation.id.desc()).offset(offset).limit(limit).all()
        db.close()
        
        result = []
        for s in simulations:
            item = s.data or {}
            item["sim_id"] = s.sim_id
            item["status"] = s.status
            # 確保有基本資訊，避免前端出錯
            if "product_name" not in item:
                item["product_name"] = "未命名專案"
            result.append(item)
        return result
    except Exception as e:
        print(f"❌ [SQL] 查詢所有模擬失敗: {e}")
        return []


def clear_citizens():
    """清空市民資料表"""
    try:
        db = SessionLocal()
        # SQLite 不支援 TRUNCATE，改用 DELETE
        num_deleted = db.query(Citizen).delete()
        db.commit()
        db.close()
        print(f"✅ 已清空市民資料表 (刪除 {num_deleted} 筆)")
        return True
    except Exception as e:
        print(f"❌ 清空市民失敗: {e}")
        return False
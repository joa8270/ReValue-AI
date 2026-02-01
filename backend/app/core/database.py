import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. 讀取環境變數 (Force Load Root .env)
from dotenv import load_dotenv
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # backend/
PROJECT_ROOT = os.path.dirname(BASE_DIR) # MIRRA/
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))

DATABASE_URL = os.getenv("DATABASE_URL")

# 2. 修正 Render/Neon 的網址格式 (SQLAlchemy 需要 postgresql:// 開頭)
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. 建立連線引擎
import json

def json_serializer(obj):
    return json.dumps(obj, ensure_ascii=False)

if not DATABASE_URL:
    # 本地開發防呆：如果沒設環境變數，就用一個暫時的 SQLite
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(current_file_dir))
    db_path = os.path.join(backend_dir, "test.db")
    print(f"[DB] No DATABASE_URL found, using local SQLite ({db_path})")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False}, json_serializer=json_serializer)
else:
    print(f"[DB] Connecting to PostgreSQL: {DATABASE_URL[:50]}...")
    engine = create_engine(DATABASE_URL, json_serializer=json_serializer)

# 🔄 Force Update: 2026-01-14 01:15

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
    """AI 虛擬市民 (Genesis 2.0 Schema)"""
    __tablename__ = "citizens"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # [V7 Change] Name & Location are now JSON for localized profiles
    name = Column(JSON, nullable=False) # { "TW": "...", "CN": "...", "US": "..." }
    gender = Column(String(20))
    age = Column(Integer)
    
    location = Column(JSON)  # { "TW": "...", "CN": "...", "US": "..." }
    occupation = Column(JSON) # { "TW": "...", "CN": "...", "US": "..." }
    
    # [V7 New Fields]
    social_tier = Column(Integer) # 1-5 (Elite to Precariat)
    career_tags = Column(JSON)    # ["Tech", "Executive", "Tier_1"]
    current_persona_desc = Column(Text) # "經歷過..." (B方案性格)
    
    bazi_profile = Column(JSON)  
    traits = Column(JSON)
    profiles = Column(JSON)      
    persona_categories = Column(JSON)


class Simulation(Base):
    """模擬記錄"""
    __tablename__ = "simulations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sim_id = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(String(50), default="processing")
    data = Column(JSON)



def init_db():
    """初始化資料庫表格 (由 main.py 啟動時呼叫)"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ [DB] Database tables created successfully.")
    except Exception as e:
        print(f"❌ [DB] Error creating tables: {e}")



# ===== 資料庫操作函數 =====

def insert_citizens_batch(citizens: list[dict]) -> bool:
    """批量插入市民資料"""
    try:
        db = SessionLocal()
        for c in citizens:
            # [V7] Handle JSON Name/Location
            name_val = c["name"] # Should be dict now
            loc_val = c.get("profiles", {}).get("TW", {}).get("city", "Unknown") # Fallback to TW city if simple string
            
            # If input is V7 format, use it directly
            if isinstance(c.get("location"), dict):
                loc_val = c["location"]
            elif isinstance(c.get("location"), str):
                 # Convert legacy string to dict
                 loc_val = {"TW": c["location"], "CN": c["location"], "US": "Unknown"}

            citizen = Citizen(
                id=c.get("id"),
                name=name_val,
                gender=c["gender"],
                age=c["age"],
                location=loc_val,
                occupation=c.get("occupation", {}),
                bazi_profile=c["bazi_profile"],
                traits=c["traits"],
                profiles=c.get("profiles", {}),
                # [V7 New Fields]
                social_tier=c.get("social_tier", 3),
                career_tags=c.get("career_tags", []),
                current_persona_desc=c.get("current_persona_desc", ""),
                persona_categories=c.get("persona_categories", []) # [Fix] P2 Diversity Audit
            )
            db.add(citizen)
        db.commit()
        db.close()
        return True
    except Exception as e:
        print(f"[ERROR] Batch insert failed: {e}")
        return False



def get_citizens_count(search: str = None) -> int:
    """取得市民總數"""
    try:
        db = SessionLocal()
        query = db.query(Citizen)
        
        if search:
            from sqlalchemy import or_, cast, Text
            pattern = f"%{search}%"
            # [V7 Fix] Cast JSON to Text for searching
            query = query.filter(
                or_(
                    cast(Citizen.name, Text).ilike(pattern),
                    cast(Citizen.location, Text).ilike(pattern),
                    cast(Citizen.occupation, Text).ilike(pattern),
                    cast(Citizen.career_tags, Text).ilike(pattern)
                )
            )
            
        count = query.count()
        db.close()
        return count
    except Exception as e:
        print(f"[ERROR] Failed to count citizens: {e}")
        return 0


def get_all_citizens(limit: int = 1000, offset: int = 0, search: str = None) -> list:
    """取得所有市民資料"""
    try:
        db = SessionLocal()
        query = db.query(Citizen)
        
        if search:
            from sqlalchemy import or_, cast, Text
            pattern = f"%{search}%"
            query = query.filter(
                or_(
                    cast(Citizen.name, Text).ilike(pattern),
                    cast(Citizen.location, Text).ilike(pattern),
                    cast(Citizen.occupation, Text).ilike(pattern)
                )
            )
        
        citizens = query.offset(offset).limit(limit).all()
        db.close()
        
        result = []
        for c in citizens:
            # [V7 Compatibility] Return TW name as default string for legacy frontend
            name_display = c.name.get("TW", "Unknown") if isinstance(c.name, dict) else str(c.name)
            loc_display = c.location.get("TW", "Unknown") if isinstance(c.location, dict) else str(c.location)
            
            # Occupation handling
            occ_val = c.occupation
            occ_display = "Unknown"
            if isinstance(occ_val, dict):
                occ_display = occ_val.get("TW", "Unknown")
            else:
                occ_display = str(occ_val) if occ_val else "Unknown"

            result.append({
                "id": c.id,
                "name": name_display, # Legacy string
                "name_full": c.name,  # V7 Full Object
                "gender": c.gender,
                "age": c.age,
                "location": loc_display, # Legacy string
                "location_full": c.location, # V7 Full Object
                "occupation": occ_display, # Legacy string
                "occupation_full": c.occupation, # V7 Full Object
                "bazi_profile": c.bazi_profile,
                "traits": c.traits,
                "profiles": c.profiles if c.profiles else {},
                "social_tier": c.social_tier,
                "career_tags": c.career_tags,
                "current_persona_desc": c.current_persona_desc
            })
        return result
    except Exception as e:
        print(f"[ERROR] Query citizens failed: {e}")
        return []

def get_random_citizens(sample_size: int = 30, stratified: bool = True, seed: int = None, filters: dict = None) -> list[dict]:
    """
    隨機取樣市民 (用於模擬)，支援代理人購買邏輯 (Proxy Buying)
    
    Args:
        sample_size: 總抽樣數量
        stratified: 是否使用分層抽樣（確保五行分佈均勻）
        seed: 隨機數種子 (用於一致性抽樣)
        filters: 篩選條件 {"age_min": 20, "age_max": 45, "occupation": "Executive"}
    
    Returns:
        市民資料列表 (包含 proxy_role 欄位)
    """
    import random
    
    # [Consistency] 如果有種子，設定隨機數狀態
    rng = random.Random(seed) if seed is not None else random

    # 🟢 代理人邏輯判斷 (Proxy Logic)
    proxy_role = None
    target_age_min = 0
    target_age_max = 100
    
    if filters:
        target_age_min = int(filters.get("age_min") or 0)
        target_age_max = int(filters.get("age_max") or 100)
        
        print(f"[DB] Original filters: {filters} (Range: {target_age_min}-{target_age_max})")


        # Scene B: 嬰幼兒產品 (Baby Formula/Diapers) -> Parents (25-45)
        if target_age_max < 12:
            print(f"[DB] Triggered Baby Proxy mode (Target: 0-{target_age_max}y -> Proxy: 25-45y Parents)")

            filters["age_min"] = 25
            filters["age_max"] = 45
            proxy_role = "parent" # 標記身份
            
        # Scene C: 高齡照護 (Elderly Care) -> Mixed (50% Real Elderly + 50% Children)
        elif target_age_min > 75:
            print(f"[DB] Triggered Elderly Care Mixed mode (Target: {target_age_min}y+ -> Mixed)")

            
            # Recursive Call for Mixed Sampling
            half_size = sample_size // 2
            
            # Group 1: 真實老人 (>75)
            f1 = filters.copy()
            f1["age_min"] = 75
            f1["age_max"] = 100
            
            # Group 2: 中年子女 (40-60)
            f2 = filters.copy()
            f2["age_min"] = 40
            f2["age_max"] = 60
            
            print(f"   -> Sampling Group 1 (Elderly): {half_size}")
            g1 = get_random_citizens(half_size, stratified, seed, f1)
            
            print(f"   -> Sampling Group 2 (Children): {sample_size - half_size}")
            # Ensure distinct seed for second group if seeded
            seed2 = seed + 1 if seed is not None else None
            g2 = get_random_citizens(sample_size - half_size, stratified, seed2, f2)
            
            # Inject Roles
            for c in g1: c["proxy_role"] = "elderly_self"
            for c in g2: c["proxy_role"] = "elderly_caregiver"
            
            result = g1 + g2
            rng.shuffle(result)
            return result

    try:
        db = SessionLocal()
        
        # Build query with filters
        query = db.query(Citizen)
        
        if filters:
            if "age_min" in filters and filters["age_min"] is not None:
                query = query.filter(Citizen.age >= int(filters["age_min"]))
            if "age_max" in filters and filters["age_max"] is not None:
                query = query.filter(Citizen.age <= int(filters["age_max"]))
            if "occupation" in filters and filters["occupation"]:
                from sqlalchemy import or_, cast, Text
                occ_filter = filters["occupation"]
                
                # Check if filter is a list of keys (e.g. ['student', 'executive'])
                if isinstance(occ_filter, list) and len(occ_filter) > 0:
                    conditions = []
                    for key in occ_filter:
                        conditions.append(cast(Citizen.persona_categories, Text).ilike(f'%"{key}"%'))
                    query = query.filter(or_(*conditions))
                    
                # Single string fallback
                elif isinstance(occ_filter, str):
                    query = query.filter(cast(Citizen.persona_categories, Text).ilike(f'%"{occ_filter}"%'))

        # 獲取符合條件的市民
        all_citizens = query.all()
        db.close()
        
        if not all_citizens:
            print(f"[DB] No citizens matching filters found (Filters: {filters}). Triggering Fallback...")
            
            # Fallback 1: Remove Occupation Filter, keep Age
            if "occupation" in filters:
                print(f"[DB] Fallback 1: Removing occupation filter...")
                fallback_filters = filters.copy()
                del fallback_filters["occupation"]
                # Recursively call without occupation
                return get_random_citizens(sample_size, stratified, seed, fallback_filters)
                
            # Fallback 2: Remove Age Filter (Full Random)
            if "age_min" in filters or "age_max" in filters:
                print(f"[DB] Fallback 2: Removing age filter (Full Random)...")
                return get_random_citizens(sample_size, stratified, seed, None)

            return []
        
        # 轉換為字典格式 (Fix: Allow passing corrected element)
        def citizen_to_dict(c, override_element=None):
            bazi = c.bazi_profile if isinstance(c.bazi_profile, dict) else {}
            traits = c.traits if isinstance(c.traits, list) else []
            # [Fix] 優先使用覆蓋的 element，若讀取 bazi 為空則依 ID 決定 (Deterministic)
            raw_elem = bazi.get("element")
            final_element = override_element or (raw_elem if raw_elem not in [None, "", "Unknown"] else ["Fire", "Water", "Metal", "Wood", "Earth"][int(c.id) % 5])

            # [Fix] 同步更新 bazi_profile 內的 element，避免下游 AI 讀到舊資料
            if override_element:
                bazi["element"] = override_element

            # [V7 Compatibility] Name/Location/Occupation Handling
            # If fields are JSON (dict), pick TW for legacy string field to prevent frontend crash
            name_str = c.name.get("TW", "Unknown") if isinstance(c.name, dict) else str(c.name)
            loc_str = c.location.get("TW", "Unknown") if isinstance(c.location, dict) else str(c.location)
            
            occ_val = c.occupation or "未知"
            occ_str = "未知"
            if isinstance(occ_val, dict):
                occ_str = occ_val.get("TW", "Unknown")
            else:
                occ_str = str(occ_val)

            c_dict = {
                "id": str(c.id),
                "name": name_str, # Legacy string
                "name_full": c.name if isinstance(c.name, dict) else {}, # V7 Full Object
                "gender": c.gender,
                "age": c.age,
                "location": loc_str, # Legacy string
                "location_full": c.location if isinstance(c.location, dict) else {}, # V7 Full Object
                "occupation": occ_str, # Legacy string (Fix for frontend list crash)
                "occupation_full": c.occupation if isinstance(c.occupation, dict) else {}, # V7 Full Object
                "bazi_profile": bazi,
                "traits": traits,
                "element": final_element, # Ensure top-level key is correct
                "structure": bazi.get("structure"),
                "strength": bazi.get("strength"),
                "favorable": bazi.get("favorable", []),
                "current_luck": bazi.get("current_luck", {}),
                "luck_timeline": bazi.get("luck_timeline", []),
                "profiles": c.profiles or {},
                "persona_categories": c.persona_categories or [],
                "proxy_role": proxy_role,  # [New] Inject Proxy Role
                
                # [V7 New Fields]
                "social_tier": c.social_tier,
                "career_tags": c.career_tags,
                "current_persona_desc": c.current_persona_desc
            }
            
            # 🛡️ [New] P0 Career Logic Patch
            # Fix "High Age, Low Job" issues (e.g. 52y Marketing Specialist)
            if c.age and c.age > 45:
                # Get current job (might be object or string if single language)
                job_data = c_dict["occupation"]
                if isinstance(job_data, dict):
                    # Handle multi-language career patch
                    for lang in ["TW", "US", "CN"]:
                        job = job_data.get(lang, "")
                        if not job: continue
                        
                        if "行銷專員" in job or "Marketing Specialist" in job:
                             job_data[lang] = "行銷總監 (Marketing Director)"
                        elif "專員" in job:
                             job_data[lang] = job.replace("專員", "資深經理")
                        elif "Specialist" in job:
                             job_data[lang] = job.replace("Specialist", "Senior Manager")
                        elif "助理" in job or "Assistant" in job:
                             job_data[lang] = "行政顧問 (Senior Consultant)"
                        elif "Coordinator" in job:
                             job_data[lang] = job.replace("Coordinator", "Director")
                        elif "Associate" in job:
                             job_data[lang] = job.replace("Associate", "Partner")
                        elif "Officer" in job:
                             job_data[lang] = job.replace("Officer", "Chief Officer")
                        elif "行政人員" in job or "Clerk" in job:
                             job_data[lang] = "營運經理 (Operations Manager)"
                elif isinstance(job_data, str):
                    # Legacy string handling
                    job = job_data
                    if "行銷專員" in job or "Marketing Specialist" in job:
                         c_dict["occupation"] = "行銷總監 (Marketing Director)"
                    elif "專員" in job:
                         c_dict["occupation"] = job.replace("專員", "資深經理")
                    elif "Specialist" in job:
                         c_dict["occupation"] = job.replace("Specialist", "Senior Manager")
                    elif "助理" in job or "Assistant" in job:
                         c_dict["occupation"] = "行政顧問 (Senior Consultant)"
                    elif "Coordinator" in job:
                         c_dict["occupation"] = job.replace("Coordinator", "Director")
                    elif "Associate" in job:
                         c_dict["occupation"] = job.replace("Associate", "Partner")
                    elif "Officer" in job:
                         c_dict["occupation"] = job.replace("Officer", "Chief Officer")
                    elif "行政人員" in job or "Clerk" in job:
                         c_dict["occupation"] = "營運經理 (Operations Manager)"

            return c_dict
        
        if stratified:
            # 分層隨機抽樣：按五行分組
            elements = ["Fire", "Water", "Metal", "Wood", "Earth"]
            per_element = sample_size // 5
            remainder = sample_size % 5
            
            # 按五行分組
            element_groups = {e: [] for e in elements}
            missing_count = 0
            
            # 建立每個市民的臨時 element 映射 (用於一致性)
            citizen_element_map = {}

            for c in all_citizens:
                bazi = c.bazi_profile if isinstance(c.bazi_profile, dict) else {}
                elem = bazi.get("element")
                
                # 防呆：如果資料庫缺五行，隨機分配一個 (避免全部判定為 Fire)
                if not elem or elem not in elements:
                    # [Consistency] 使用市民 ID 做為種子，確保留用同一位市民時屬性不變
                    # 但這裡為了補全資料，我們需要一個「確定性」的隨機
                    c_seed = int(c.id) if isinstance(c.id, int) else hash(str(c.id))
                    elem = elements[c_seed % 5] 
                    missing_count += 1
                
                citizen_element_map[c.id] = elem
                if elem in element_groups:
                    element_groups[elem].append(c)
            
            if missing_count > 0:
                print(f"[DB] Warning: {missing_count} citizens missing element data (Assigned deterministically by ID)")

            
            # 從每組隨機抽取
            result = []
            for i, element in enumerate(elements):
                group = element_groups[element]
                # [Consistency] 對群組內的市民進行排序，確保 RNG 取樣一致
                group.sort(key=lambda x: x.id)
                
                limit = per_element + (1 if i < remainder else 0)
                
                if len(group) > 0:
                    sampled = rng.sample(group, min(limit, len(group)))
                    # 傳入正確的 element
                    result.extend([citizen_to_dict(c, override_element=element) for c in sampled])
            
            print(f"[Sampling] Total {len(result)} citizens")

            # [Consistency] 打亂最終結果，避免永遠按五行排序
            rng.shuffle(result)
            return result
        else:
            # 純隨機抽樣
            all_citizens.sort(key=lambda x: x.id) # Sort for consistency
            sampled = rng.sample(all_citizens, min(sample_size, len(all_citizens)))
            
            # [Fix] 即使是純隨機，也必須確保 Element 正確補全 (同 Stratified 邏輯)
            result = []
            elements_pool = ["Fire", "Water", "Metal", "Wood", "Earth"]
            for c in sampled:
                bazi = c.bazi_profile if isinstance(c.bazi_profile, dict) else {}
                elem = bazi.get("element")
                
                # 如果 DB 缺資料，計算確定性的 Element
                if not elem or elem not in elements_pool:
                    c_seed = int(c.id) if isinstance(c.id, int) else hash(str(c.id))
                    elem = elements_pool[c_seed % 5]
                
                result.append(citizen_to_dict(c, override_element=elem))
            
            return result


        
    except Exception as e:
        print(f"[ERROR] Random sample failed: {e}")
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
        print(f"[SQL] Simulation {sim_id} created")

        try:
            with open("db_debug.log", "a", encoding="utf-8") as f:
                f.write(f"[CREATE] {sim_id} Success\n")
        except: pass
        return True
    except Exception as e:
        print(f"[ERROR] [SQL] Create simulation failed: {e}")
        try:
            with open("db_debug.log", "a", encoding="utf-8") as f:
                f.write(f"[CREATE] {sim_id} FAILED: {e}\n")
        except: pass
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
            print(f"[SQL] Simulation {sim_id} updated to {status}")

            try:
                with open("db_debug.log", "a", encoding="utf-8") as f:
                    f.write(f"[UPDATE] {sim_id} Updated to {status}\n")
            except: pass
        else:
            # 記錄不存在，建立新記錄 (upsert)
            new_simulation = Simulation(
                sim_id=sim_id,
                status=status,
                data=data
            )
            db.add(new_simulation)
            db.commit()
            print(f"[SQL] Simulation {sim_id} not found, created new record (status: {status})")

            try:
                with open("db_debug.log", "a", encoding="utf-8") as f:
                    f.write(f"[UPDATE] {sim_id} Created New (status: {status})\n")
            except: pass
        
        db.close()
        return True
    except Exception as e:
        error_msg = f"[ERROR] [SQL] Update/Create simulation failed: {e}\n"
        print(error_msg.strip())
        try:
            with open("db_errors.log", "a", encoding="utf-8") as f:
                f.write(f"[{sim_id}] {error_msg}")
                import traceback
                f.write(traceback.format_exc() + "\n")
        except:
            pass
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
        print(f"[ERROR] [SQL] Query simulation failed: {e}")
        return None


def clear_citizens():
    """清空市民資料表"""
    try:
        db = SessionLocal()
        # SQLite 不支援 TRUNCATE，改用 DELETE
        num_deleted = db.query(Citizen).delete()
        db.commit()
        db.close()
        return True
    except Exception as e:
        print(f"[ERROR] Clear citizens failed: {e}")
        return False


def get_citizen_by_id(citizen_id: str) -> dict | None:
    """根據 ID 查詢單一市民的完整資料"""
    try:
        db = SessionLocal()
        
        # 嘗試用整數 ID 查詢
        try:
            int_id = int(citizen_id)
            citizen = db.query(Citizen).filter(Citizen.id == int_id).first()
        except ValueError:
            # 如果 ID 不是整數，可能是 UUID 格式
            citizen = None
        
        db.close()
        
        if citizen:
            bazi = citizen.bazi_profile if isinstance(citizen.bazi_profile, dict) else {}
            traits = citizen.traits if isinstance(citizen.traits, list) else []
            result_dict = {
                "id": str(citizen.id),
                "name": citizen.name.strip('"').strip("'") if citizen.name else citizen.name,
                "gender": citizen.gender,
                "age": citizen.age,
                "location": citizen.location,
                "occupation": citizen.occupation or "未知",
                "bazi_profile": bazi,
                "traits": traits,
                "#": "--- Localized Profiles ---",
                "profiles": citizen.profiles or {},
                # 直接展開常用欄位，方便前端使用
                "birth_year": bazi.get("birth_year"),
                "birth_month": bazi.get("birth_month"),
                "birth_day": bazi.get("birth_day"),
                "birth_shichen": bazi.get("birth_shichen"),
                "four_pillars": bazi.get("four_pillars"),
                "day_master": bazi.get("day_master"),
                "structure": bazi.get("structure"),
                "strength": bazi.get("strength"),
                # [Fix] Deterministic Fallback for Element (Treat None/Unknown as invalid, but accept Fire)
                "element": bazi.get("element") if bazi.get("element") not in [None, "", "Unknown"] else ["Fire", "Water", "Metal", "Wood", "Earth"][int(citizen.id) % 5],
                "favorable": bazi.get("favorable", []),
                "current_luck": bazi.get("current_luck", {}),
                "luck_timeline": bazi.get("luck_timeline", []),
                "trait": bazi.get("trait", "性格均衡")
            }
            
            # 🛡️ [New] P0 Career Logic Patch (Sync with citizen_to_dict)
            if citizen.age and citizen.age > 45:
                job = result_dict["occupation"]
                if "行銷專員" in job or "Marketing Specialist" in job:
                     result_dict["occupation"] = "行銷總監 (Marketing Director)"
                elif "專員" in job:
                     result_dict["occupation"] = job.replace("專員", "資深經理")
                elif "Specialist" in job:
                     result_dict["occupation"] = job.replace("Specialist", "Senior Manager")
                elif "助理" in job or "Assistant" in job:
                     result_dict["occupation"] = "行政顧問 (Senior Consultant)"
                elif "Coordinator" in job:
                     result_dict["occupation"] = job.replace("Coordinator", "Director")
                elif "Associate" in job:
                     result_dict["occupation"] = job.replace("Associate", "Partner")
                elif "Officer" in job:
                     result_dict["occupation"] = job.replace("Officer", "Chief Officer")
                elif "行政人員" in job or "Clerk" in job:
                     result_dict["occupation"] = "營運經理 (Operations Manager)"
            
            return result_dict
        return None
    except Exception as e:
        print(f"[ERROR] Query citizen {citizen_id} failed: {e}")
        return None
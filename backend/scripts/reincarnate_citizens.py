
import os
import json
import asyncio
import logging
from dotenv import load_dotenv

# 設定日誌 (Move to top)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load .env from backend root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor

# 嘗試導入 CrewAI，如果沒有安裝則報錯提示

# 嘗試導入 CrewAI，如果沒有安裝則使用 Fallback
HAS_CREWAI = False
try:
    from crewai import Agent, Task, Crew, Process
    # from langchain_openai import ChatOpenAI # Deprecated
    from langchain_google_genai import ChatGoogleGenerativeAI
    HAS_CREWAI = True
except ImportError:
    logger.warning("⚠️ CrewAI 未安裝或安裝失敗，將使用 Lightweight Fallback 模式執行任務。")
    # 定義 Fallback 類別以模擬 CrewAI 介面
    class Agent:
        def __init__(self, role, goal, backstory, verbose=False, allow_delegation=False, llm=None):
            self.role = role
            self.goal = goal
            self.backstory = backstory
            self.llm = llm
        
        def execute_task(self, task_desc):
            # 簡單的使用 LLM 執行
            system_prompt = f"You are {self.role}. {self.backstory}\nYour goal is: {self.goal}"
            
            # Inject Schema for Data Engineer
            if "JSON" in task_desc or "json" in task_desc:
                schema_json = """
{
    "name_tw": "Generated Taiwanese Name (Traditional Chinese)",
    "US": {
        "name": "English Name",
        "city": "US City",
        "job": "US Job Title",
        "pain": "US Pain Point"
    },
    "CN": {
        "name": "Chinese Name",
        "city": "CN City",
        "job": "CN Job Title",
        "pain": "CN Pain Point"
    }
}
"""
                system_prompt += f"\nIMPORTANT: You must output ONLY valid JSON matching this structure exactly:\n{schema_json}\nDo not include root keys like 'agent_id' or 'data'. The root must have keys 'name_tw', 'US' and 'CN'."

            messages = [
                ("system", system_prompt),
                ("human", task_desc)
            ]
            if self.llm:
                content = self.llm.invoke(messages).content
                # Aggressive cleanup common in Gemini responses
                content = content.replace("```json", "").replace("```", "").strip()
                return content
            return "Simulated Output"

    class Task:
        def __init__(self, description, expected_output, agent, output_pydantic=None):
            self.description = description
            self.expected_output = expected_output
            self.agent = agent
            self.output_pydantic = output_pydantic
            self.output = None

    class Process:
        sequential = "sequential"

    class Crew:
        def __init__(self, agents, tasks, process=Process.sequential, verbose=False):
            self.agents = agents
            self.tasks = tasks
            self.verbose = verbose

        def kickoff(self):
            logger.info("🚀 Starting Crew (Fallback Mode)")
            context = ""
            for task in self.tasks:
                logger.info(f"👉 Agent {task.agent.role} working on task...")
                # 將上一個任務的結果作為 Context
                full_transcription = f"{task.description}\n\nContext from previous steps:\n{context}"
                result = task.agent.execute_task(full_transcription)
                
                # 如果需要 Pydantic 解析
                if task.output_pydantic:
                    try:
                        # 嘗試解析 JSON
                        clean_json = result.replace("```json", "").replace("```", "").strip()
                        # 這裡簡化處理，實際可能需要重試
                        import json
                        data_dict = json.loads(clean_json)
                        # 驗證結構 (簡單檢查)
                        # 驗證結構 (簡單檢查)
                        # result = task.output_pydantic(**data_dict) # Direct unpacking might fail if keys mismatch
                        
                        # Safer construction manually mapping fields to avoid validation errors
                        result = task.output_pydantic(
                            name_tw=data_dict.get("name_tw", "Unknown"),
                            US=data_dict.get("US", {}),
                            CN=data_dict.get("CN", {})
                        )
                    except Exception as e:
                        logger.error(f"JSON Parsing failed in fallback: {e}")
                        # 回傳空物件避免崩潰
                        result = task.output_pydantic(name_tw="Unknown", US={"name":"", "city":"", "job":"", "pain":""}, CN={"name":"", "city":"", "job":"", "pain":""})
                
                task.output = result
                context += f"\nOutput of {task.agent.role}: {result}"
            
            return self.tasks[-1].output

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    print("❌ 錯誤: 請先安裝依賴庫: pip install langchain-google-genai")
    exit(1)

from pydantic import BaseModel, Field


# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ==========================================
# 1. 定義資料結構 (Pydantic Models)
# ==========================================

class ProfileData(BaseModel):
    name: str = Field(description="該國家身分的姓名 Identity Name")
    city: str = Field(description="居住城市 (e.g., Austin, Shenzhen)")
    job: str = Field(description="職業頭銜 (e.g., Senior Engineer)")
    pain: str = Field(description="該階級的核心焦慮 (e.g., H1B Visa, 35歲優化)")

class GlobalIdentity(BaseModel):
    name_tw: str = Field(description="[NEW] 為此市民生成的真實台灣姓名 (繁體中文, 1990-2000出生風格)")
    US: ProfileData = Field(description="美國身分資料")
    CN: ProfileData = Field(description="中國身分資料")

# ==========================================
# 2. 定義 Agent 與 Task 
# ==========================================

def create_reincarnation_crew(citizen: Dict) -> Crew:
    """
    為單一位市民建立轉生團隊
    """
    
    # 提取關鍵資訊
    citizen_id = citizen.get('id')
    tw_profile = f"當前代號: {citizen.get('name')}, 居住: {citizen.get('city')}, 職位: {citizen.get('job')}, 年齡: {citizen.get('age')}"
    bazi = citizen.get('bazi', 'Unknown')
    bazi_summary = citizen.get('bazi_summary', '')

    # 設定 Gemini LLM (Gemini 2.5 Pro)
    gemini_llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.5-pro",
        verbose=True,
        temperature=0.8,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    # --- Agent 1: 文化人類學家 ---
    anthropologist = Agent(
        role='Cultural Anthropologist (文化人類學家)',
        goal='為市民賦予真實姓名，並映射出美中平行身分',
        backstory="""你是一位精通東亞與北美社會結構的文化人類學家。
        你的任務有兩個：
        1. **為代號市民命名**：目前的市民只有代號 (Citizen_xxxx)。請根據他的「八字性格」與「職業」，為他取一個**真實、接地氣的台灣名字** (繁體中文)。
           - 年齡設定為 1990-2000 年出生 (約 25-35 歲)。
           - 名字要符合該世代的命名習慣 (如：雅婷, 冠宇, 怡君, 承恩, 筱涵 等，或更現代的)。
           - 名字氣質需符合其命理格局 (例如「七殺格」可能叫 志豪，「食神格」可能叫 佳薇)。
        
        2. **平行宇宙轉生**：推導出他在美國 (US) 與中國 (CN) 的對應身分與焦慮。""",
        verbose=True,
        allow_delegation=False,
        llm=gemini_llm 
    )

    # --- Agent 2: 資料工程師 ---
    data_engineer = Agent(
        role='Data Engineer (資料工程師)',
        goal='將敘事性的身分描述轉化為嚴格的 JSON 格式',
        backstory="""你是一位對資料結構有潔癖的工程師。負責輸出 JSON。""",
        verbose=True,
        allow_delegation=False,
        llm=gemini_llm 
    )

    # --- Task 1: 身分映射 ---
    mapping_task = Task(
        description=f"""
        分析以下台灣市民資料：
        [ID]: {citizen_id}
        [Profile]: {tw_profile}
        [Bazi]: {bazi}

        任務 A: 命名 (Naming)
        請為他取一個真實的台灣姓名 (name_tw)。

        任務 B: 轉生 (Reincarnation)
        1. **US Identity**:
           - 英文姓名 (可與中文名諧音或完全不同)。
           - 城市 (產業聚落)。
           - 職業 (對應資歷)。
           - **Pain Point**: 真實的美國職場/生活焦慮。
        
        2. **CN Identity**:
           - 簡體中文姓名。
           - 一線/新一線城市。
           - 職業 (大廠職級 P6/P7 等)。
           - **Pain Point**: 內捲、房貸、35歲優化等真實焦慮。
        """,
        expected_output="一份包含 台灣新姓名、US 身分、CN 身分 的完整分析。",
        agent=anthropologist
    )

    # --- Task 2: 格式化 ---
    formatting_task = Task(
        description="將分析報告轉換為 JSON，必須包含 name_tw, US, CN 欄位。",
        expected_output="JSON object matching GlobalIdentity schema.",
        agent=data_engineer,
        output_pydantic=GlobalIdentity
    )

    crew = Crew(
        agents=[anthropologist, data_engineer],
        tasks=[mapping_task, formatting_task],
        process=Process.sequential,
        verbose=True
    )

    return crew

# ==========================================
# 3. 非同步處理邏輯
# ==========================================

async def process_single_citizen(semaphore: asyncio.Semaphore, citizen: Dict) -> Dict:
    async with semaphore:
        try:
            logger.info(f"🚀 開始轉生: {citizen.get('id')} ({citizen.get('bazi')})")
            print(f"DEBUG: Processing {citizen.get('id')}...")

            
            crew = create_reincarnation_crew(citizen)
            
            # Run Crew
            # Note: CrewAI kickoff is blocking.
            result = await asyncio.to_thread(crew.kickoff)
            
            # Parse Result
            if hasattr(result, 'dict'):
                parsed_data = result.dict()
            elif hasattr(result, 'model_dump'):
                 parsed_data = result.model_dump()
            elif isinstance(result, str):
                try:
                    clean_json = result.replace("```json", "").replace("```", "").strip()
                    parsed_data = json.loads(clean_json)
                except:
                    logger.error(f"⚠️ JSON Parse Error for {citizen.get('id')}")
                    logger.error(f"⚠️ JSON Parse Error for {citizen.get('id')}")
                    parsed_data = {"name_tw": "Unknown", "US": {}, "CN": {}}
            else:
                parsed_data = {}

            # Construct Record
            # 優先使用 LLM 生成的 name_tw，如果沒有則回退到原始 name (但通常應該要有)
            new_name = parsed_data.get('name_tw') 
            if not new_name or new_name == "Unknown":
                 new_name = citizen.get('name')
            
            final_record = {
                "id": citizen.get('id'),
                "name": new_name, # REPLACE ROOT NAME!
                "bazi": citizen.get('bazi'),
                "gender": citizen.get('gender'), # Preserve original gender
                "age": citizen.get('age'),
                "profiles": {
                    "TW": {
                        "name": new_name,
                        "city": citizen.get('city'),
                        "job": citizen.get('job'),
                        "pain": "未知 (待補完)" 
                    },
                    "US": parsed_data.get('US', {}),
                    "CN": parsed_data.get('CN', {})
                }
            }
            
            logger.info(f"✅ 轉生成功: {citizen.get('id')} -> {new_name}")
            return final_record

        except Exception as e:
            logger.error(f"❌ 處理失敗 {citizen.get('id')}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

import random

BAZI_TYPES = [
    "食神格 (講究體驗)", "七殺格 (行動派)", "正官格 (守規矩)", 
    "偏財格 (機靈)", "正印格 (仁慈)", "傷官格 (叛逆)", 
    "比肩格 (自我)", "劫財格 (競爭)"
]

MBTI_TYPES = ["INTJ", "INTP", "ENTJ", "ENTP", "INFJ", "INFP", "ENFJ", "ENFP", "ISTJ", "ISFJ", "ESTJ", "ESFJ", "ISTP", "ISFP", "ESTP", "ESFP"]

CITIES_TW = ["Taipei", "New Taipei", "Taichung", "Kaohsiung", "Hsinchu", "Tainan"]
JOBS_TW = ["Engineer", "Teacher", "Sales", "Designer", "PM", "Marketing", "Freelancer", "Student", "Civil Servant", "Doctor"]

def generate_raw_seeds(output_path: str, count: int = 1000):
    logger.info(f"🌱 Generating {count} Raw Seeds...")
    seeds = []
    for i in range(count):
        seed = {
            "id": f"Citizen_{i:04d}",
            "name": f"Citizen_{i:04d}", # Temp name
            "age": random.randint(22, 45),
            "gender": random.choice(["Male", "Female", "Non-binary"]),
            "city": random.choice(CITIES_TW),
            "job": random.choice(JOBS_TW),
            "bazi": random.choice(BAZI_TYPES),
            "mbti": random.choice(MBTI_TYPES),
            "bazi_summary": "Auto-generated seed."
        }
        seeds.append(seed)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(seeds, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✅ Raw seeds saved to {output_path}")
    return seeds

async def main():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_FILE = os.path.join(BASE_DIR, 'data', 'citizens.json')
    OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'citizens_global_v2.json') # saving to v2

    citizens = []
    DO_DEBUG = False

    
    # 1. 讀取與自動補種
    need_seeding = False
    if not os.path.exists(DATA_FILE):
        need_seeding = True
    else:
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                citizens = json.load(f)
            if len(citizens) < 10:
                need_seeding = True
        except:
             need_seeding = True
    
    if need_seeding:
        logger.warning(f"⚠️ Source data invalid or empty (Count: {len(citizens)}). Triggering Auto-Seeding.")
        citizens = generate_raw_seeds(DATA_FILE, 1000)
        print("🔄 Generated 1,000 raw seeds because source was empty.")

    # 0. Clean Slate (User Request)
    if os.path.exists(OUTPUT_FILE):
        logger.warning(f"🧹 Clearing existing output file: {OUTPUT_FILE}")
        os.remove(OUTPUT_FILE)

    logger.info(f"🔥 Project REINCARNATION V2 Start. Total: {len(citizens)}")
    if DO_DEBUG:
        citizens = citizens[:2]
        print("[DEBUG] Processing only 2 citizens.")

    
    # Batch Processing with Incremental Save
    BATCH_SIZE = 10 # Save every 10
    MAX_CONCURRENCY = 5 # Moderate concurrency to avoid rate limits
    semaphore = asyncio.Semaphore(MAX_CONCURRENCY)
    
    completed_citizens = []
    total_processed = 0
    
    # Iterate in batches
    for i in range(0, len(citizens), BATCH_SIZE):
        batch = citizens[i : i + BATCH_SIZE]
        logger.info(f"⚡ Processing Batch {i}-{i+len(batch)}...")
        
        tasks = [process_single_citizen(semaphore, c) for c in batch]
        results = await asyncio.gather(*tasks)
        
        valid_batch = [r for r in results if r is not None]
        completed_citizens.extend(valid_batch)
        total_processed += len(valid_batch)
        
        # INCREMENTAL SAVE
        logger.info(f"💾 Saving {total_processed} citizens to {OUTPUT_FILE}...")
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(completed_citizens, f, ensure_ascii=False, indent=2)

    logger.info(f"🎉 All Done! Generated {len(completed_citizens)} citizens.")

if __name__ == "__main__":
    asyncio.run(main())

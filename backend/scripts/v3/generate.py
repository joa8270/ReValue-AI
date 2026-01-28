
import os
import json
import asyncio
import logging
import random
import re
from typing import Dict, Optional, List
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("backend/data/v3_generation.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
SEED_FILE = os.path.join(DATA_DIR, 'citizens_seed.json')
PROGRESS_FILE = os.path.join(DATA_DIR, 'citizens_progress.jsonl')
FINAL_FILE = os.path.join(DATA_DIR, 'citizens_global.json')

load_dotenv(os.path.join(BASE_DIR, '.env'))

# --- Data Structures ---

class ProfileData(BaseModel):
    name: str = Field(description="Name")
    city: str = Field(description="City")
    job: str = Field(description="Job Title")
    pain: str = Field(description="Core Anxiety/Pain Point")

class GlobalIdentity(BaseModel):
    name_tw: str = Field(description="Taiwanese Name")
    US: ProfileData
    CN: ProfileData

# --- Logic ---

class ReincarnationEngine:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.5-pro", # Using the strong model
            temperature=0.9, # High creativity for names
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            request_timeout=60
        )
        self.semaphore = asyncio.Semaphore(5) # Concurrency limit

    def is_valid_chinese_name(self, name: str) -> bool:
        # Check if it contains Chinese characters and NO "Citizen_"
        if "Citizen_" in name:
            return False
        if len(name) < 2 or len(name) > 4:
            return False
        # Basic regex for Chinese characters
        if not re.search(r'[\u4e00-\u9fff]', name):
            return False
        return True

    async def generate_identity(self, seed: Dict, retry_count=0) -> Optional[Dict]:
        if retry_count > 3:
            logger.error(f"❌ Failed to generate valid identity for {seed['id']} after 3 retries.")
            return None

        prompt = f"""
        You are an expert Cultural Anthropologist and Novelist.
        Task: Create a REALISTIC identity profile for a Taiwanese citizen and their parallel universe selves in US and CN.
        
        Input Context:
        - ID: {seed['id']}
        - Gender: {seed['gender']}
        - Age: {seed['age']}
        - Bazi: {seed['bazi']}
        - MBTI: {seed['mbti']}
        - Job Type: {seed['base_city']} / {seed['base_job']}

        Requirements:
        1. [CRITICAL] **TAIWAN NAME (name_tw)**: 
           - MUST be a realistic Traditional Chinese name (e.g., 陳志豪, 林雅婷).
           - Do NOT use "Citizen_xxxx".
           - Match the Age ({seed['age']} y/o means born around {2025 - seed['age']}).
           - Match Gender ({seed['gender']}).
        
        2. **US Identity**:
           - English Name (can be related or adopted).
           - Realistic City & Job based on MBTI/Skills.
           - REAL pain point (Visa, Bamboo ceiling, Layoffs).

        3. **CN Identity**:
           - Simplified Chinese Name.
           - Tier 1/New Tier 1 City.
           - REAL pain point (996, 35-year-old curse, Housing).

        Output JSON format strictly:
        {{
            "name_tw": "王小明",
            "US": {{ "name": "...", "city": "...", "job": "...", "pain": "..." }},
            "CN": {{ "name": "...", "city": "...", "job": "...", "pain": "..." }}
        }}
        """

        try:
            async with self.semaphore:
                response = await self.llm.ainvoke(prompt)
                content = response.content.replace("```json", "").replace("```", "").strip()
                data = json.loads(content)
                
                # VALIDATION
                name_tw = data.get("name_tw", "")
                if not self.is_valid_chinese_name(name_tw):
                    logger.warning(f"⚠️ Invalid Name '{name_tw}' for {seed['id']}. Retrying ({retry_count+1}/3)...")
                    return await self.generate_identity(seed, retry_count + 1)
                
                # Construct Final Record
                final_record = {
                    "id": seed['id'],
                    "name": name_tw, # Root name is the TW name
                    "bazi": seed['bazi'],
                    "mbti": seed['mbti'],
                    "gender": seed['gender'],
                    "age": seed['age'],
                    "profiles": {
                        "TW": {
                            "name": name_tw,
                            "city": seed['base_city'],
                            "job": seed['base_job'],
                            "pain": "Waiting for simulation..." 
                        },
                        "US": data.get("US"),
                        "CN": data.get("CN")
                    }
                }
                logger.info(f"✅ Generated: {name_tw} ({seed['id']})")
                return final_record

        except Exception as e:
            logger.error(f"⚠️ Error processing {seed['id']}: {e}")
            return await self.generate_identity(seed, retry_count + 1)

    async def save_progress(self, record: Dict):
        # Atomic append to JSONL
        with open(PROGRESS_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

async def main():
    # 0. Load Seeds
    if not os.path.exists(SEED_FILE):
        print("❌ Seed file missing! Run create_seeds.py first.")
        return
    
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        seeds = json.load(f)
    
    # 1. Resume Capability
    completed_ids = set()
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    completed_ids.add(rec['id'])
                except:
                    pass
    
    print(f"[INFO] Total Seeds: {len(seeds)}")
    print(f"[INFO] Already Done: {len(completed_ids)}")
    
    pending_seeds = [s for s in seeds if s['id'] not in completed_ids]
    
    # 2. Safety Limit (for Test Run)
    import sys
    if "--limit" in sys.argv:
        limit_idx = sys.argv.index("--limit") + 1
        limit = int(sys.argv[limit_idx])
        pending_seeds = pending_seeds[:limit]
        print(f"🧪 Test Mode: Processing only {limit} seeds.")

    if not pending_seeds:
        print("[SUCCESS] All done! Nothing to process.")
        return

    # 3. Execution
    engine = ReincarnationEngine()
    tasks = []
    
    # We process in small chunks to manage memory/connections, though semaphore handles concurrency
    chunk_size = 20 
    for i in range(0, len(pending_seeds), chunk_size):
        chunk = pending_seeds[i:i+chunk_size]
        print(f"[INFO] Processing chunk {i} - {i+len(chunk)}...")
        
        chunk_tasks = [engine.generate_identity(seed) for seed in chunk]
        results = await asyncio.gather(*chunk_tasks)
        
        for res in results:
            if res:
                await engine.save_progress(res)
    
    print("[SUCCESS] Batch Complete.")

if __name__ == "__main__":
    asyncio.run(main())

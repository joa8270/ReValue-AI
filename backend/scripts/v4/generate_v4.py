
import os
import json
import asyncio
import logging
import random
import re
import sys
from typing import Dict, Optional, List
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("backend/data/v4_generation.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Config
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
SEED_FILE = os.path.join(DATA_DIR, 'citizens_seed.json')
PROGRESS_FILE = os.path.join(DATA_DIR, 'citizens_progress.jsonl')

load_dotenv(os.path.join(BASE_DIR, '.env'))

# --- Logic ---

class ReincarnationEngineV4:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="models/gemini-2.5-pro", 
            temperature=1.0, 
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            request_timeout=60
        )
        self.semaphore = asyncio.Semaphore(5)

    def is_valid_chinese_name(self, name: str) -> bool:
        if "Citizen_" in name: return False
        if len(name) < 2 or len(name) > 4: return False
        if not re.search(r'[\u4e00-\u9fff]', name): return False
        return True

    def get_diverse_role_prompt(self):
        roll = random.random()
        if roll < 0.33:
            return "CATEGORY: [BLUE COLLAR / MANUAL LABOR]. Examples: Factory Worker, Construction, Delivery Driver, Plumber, Farmer."
        elif roll < 0.66:
            return "CATEGORY: [SERVICE INDUSTRY]. Examples: 7-11 Clerk, Security Guard, Cleaner, Waiter, Caretaker."
        else:
            return "CATEGORY: [UNEMPLOYED / MARGINALIZED]. Examples: Unemployed, Layoff Victim, Struggling Artist, Gig Worker (Unstable)."

    async def generate_identity(self, seed: Dict, retry_count=0) -> Optional[Dict]:
        if retry_count > 3:
            logger.error(f"❌ Failed to generate {seed['id']} after 3 retries.")
            return None

        forced_category = self.get_diverse_role_prompt()
        
        prompt = f"""
        You are a Sociologist recording the lives of ordinary people in Taiwan, US, and China.
        
        Target Identity:
        - ID: {seed['id']}
        - Gender: {seed['gender']}
        - Age: {seed['age']}
        - Bazi: {seed['bazi']}
        - MBTI: {seed['mbti']}
        
        🔥 **MANDATORY JOB REQUIREMENT (Must Apply to ALL 3 Identites)**:
        {forced_category}
        
        **STRICT RULES**:
        1. **NO ELITES**: Do NOT generate CEOs, Directors, Managers, or High-Level Professionals.
        2. **REALITY**: Focus on the struggles of ordinary life (low wages, long hours, instability).
        3. **NAMES**: Must be REAL Traditional Chinese names (e.g. 陳怡君) for TW.

        Output JSON format strictly:
        {{
            "name_tw": "王小明",
            "TW": {{ "city": "...", "job": "...", "pain": "..." }},
            "US": {{ "name": "...", "city": "...", "job": "...", "pain": "..." }},
            "CN": {{ "name": "...", "city": "...", "job": "...", "pain": "..." }}
        }}
        """

        try:
            async with self.semaphore:
                response = await self.llm.ainvoke(prompt)
                content = response.content.replace("```json", "").replace("```", "").strip()
                data = json.loads(content)
                
                name_tw = data.get("name_tw", "")
                if not self.is_valid_chinese_name(name_tw):
                    return await self.generate_identity(seed, retry_count + 1)
                
                final_record = {
                    "id": seed['id'],
                    "name": name_tw,
                    "bazi": seed['bazi'],
                    "mbti": seed['mbti'],
                    "gender": seed['gender'],
                    "age": seed['age'],
                    "profiles": {
                        "TW": {
                            "name": name_tw,
                            "city": data.get("TW", {}).get("city", seed.get("base_city")),
                            "job": data.get("TW", {}).get("job", "Worker"),
                            "pain": data.get("TW", {}).get("pain", "Daily struggle")
                        },
                        "US": data.get("US"),
                        "CN": data.get("CN")
                    }
                }
                logger.info(f"✅ Generated (V4 Diverse): {name_tw} - {final_record['profiles']['TW']['job']}")
                return final_record

        except Exception as e:
            logger.warning(f"Error {seed['id']}: {e}")
            return await self.generate_identity(seed, retry_count + 1)

    async def save_progress(self, record: Dict):
        with open(PROGRESS_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

async def main():
    if not os.path.exists(SEED_FILE):
        print("❌ Seed file missing!")
        return
    
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        seeds = json.load(f)
    
    completed_ids = set()
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    completed_ids.add(rec['id'])
                except: pass
    
    print(f"[INFO] V4 Diversity Run. Total Seeds: {len(seeds)}")
    print(f"[INFO] Already Done: {len(completed_ids)}")
    
    pending_seeds = [s for s in seeds if s['id'] not in completed_ids]

    if "--limit" in sys.argv:
        try:
            limit_idx = sys.argv.index("--limit") + 1
            limit = int(sys.argv[limit_idx])
            pending_seeds = pending_seeds[:limit]
            print(f"🧪 Test Mode: Processing only {limit} seeds.")
        except:
             pass

    if not pending_seeds:
        print("[SUCCESS] All done!")
        return

    engine = ReincarnationEngineV4()
    
    chunk_size = 20 
    for i in range(0, len(pending_seeds), chunk_size):
        chunk = pending_seeds[i:i+chunk_size]
        print(f"[INFO] Processing V4 Batch {i}...")
        
        chunk_tasks = [engine.generate_identity(seed) for seed in chunk]
        results = await asyncio.gather(*chunk_tasks)
        
        for res in results:
            if res:
                await engine.save_progress(res)
    
    print("[SUCCESS] V4 Batch Complete.")

if __name__ == "__main__":
    asyncio.run(main())

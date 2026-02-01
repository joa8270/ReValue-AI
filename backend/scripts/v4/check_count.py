
import os
import sys
from dotenv import load_dotenv

# Setup Path to import from app
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # backend/
PROJECT_ROOT = os.path.dirname(BASE_DIR) # MIRRA/

# 1. LOAD ROOT ENV
load_dotenv(os.path.join(PROJECT_ROOT, '.env'))
sys.path.append(BASE_DIR)

from app.core.database import get_citizens_count

if __name__ == "__main__":
    try:
        url = os.getenv('DATABASE_URL')
        print(f"[INFO] Checking Database: {url[:20]}...")
        count = get_citizens_count()
        print(f"[SUCCESS] Current Citizen Count in Remote DB: {count}")
    except Exception as e:
        print(f"[ERROR] Failed to get count: {e}")

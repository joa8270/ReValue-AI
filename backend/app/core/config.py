import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 強制載入 .env 檔案
load_dotenv()

class Settings(BaseSettings):
    """
    MIRRA 全域設定類別
    負責統一管理所有的 API Keys 與系統開關
    """
    
    # 1. 專案基本資訊
    PROJECT_NAME: str = "MIRRA Backend"
    VERSION: str = "1.0.0"
    
    # 2. 核心金鑰 (從 .env 讀取)
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    LINE_CHANNEL_ACCESS_TOKEN: str = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    LINE_CHANNEL_SECRET: str = os.getenv("LINE_CHANNEL_SECRET", "")
    
    # 3. 模擬控制 (成本控管核心)
    # 預設為 MOCK 模式以防萬一
    SIMULATION_MODE: str = os.getenv("SIMULATION_MODE", "MOCK").upper()
    MINI_BATCH_SIZE: int = int(os.getenv("MINI_BATCH_SIZE", 5))
    FULL_BATCH_SIZE: int = int(os.getenv("FULL_BATCH_SIZE", 1000))
    DEFAULT_LOCATION: str = os.getenv("DEFAULT_LOCATION", "Taipei")
    
    @property
    def agent_count(self) -> int:
        """
        智慧判斷：根據目前的 SIMULATION_MODE 決定要生成多少個 AI 模擬市民
        """
        if self.SIMULATION_MODE == "MINI":
            return self.MINI_BATCH_SIZE
        elif self.SIMULATION_MODE == "FULL":
            return self.FULL_BATCH_SIZE
        else:
            # MOCK 模式下，後端不需要真的生成 Agent 物件，
            # 而是會由 Service 層直接回傳假資料
            return 0 

    @property
    def is_mock(self) -> bool:
        """快速判斷是否為開發模式"""
        return self.SIMULATION_MODE == "MOCK"

# 實例化設定物件，讓其他檔案可以直接 import settings
settings = Settings()
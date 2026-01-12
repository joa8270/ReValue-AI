from pydantic import BaseModel, Field

class BaZiWeights(BaseModel):
    """
    八字十神權重模型 (Ten Gods Weights)
    
    此模型定義了八字中「十神」的能量分佈。
    每個欄位為 0.0 至 1.0 的浮點數，數值越高代表該特質對 Agent 行為的影響力越大。
    
    這些權重將直接映射到 Agent 的消費價值觀與決策邏輯：
    - 比劫 (Self): 自我意識與同儕影響
    - 食傷 (Output): 表現慾與感性享受
    - 財星 (Wealth): 物質追求與金錢觀
    - 官殺 (Power): 自律、地位與冒險
    - 印星 (Resource): 思考、安全感與傳統
    """
    
    # 同我者 (比劫) - Self / Peer
    bi_jian: float = Field(..., ge=0.0, le=1.0, description="比肩 (Friend): [Self-Will] 代表獨立自主、意志堅定。高權重影響：降低對促銷的敏感度，提升對產品本質的堅持。")
    jie_cai: float = Field(..., ge=0.0, le=1.0, description="劫財 (Rob Wealth): [Social Impulse] 代表社交競爭、衝動熱情。高權重影響：提升 `impulse_buying` (衝動消費) 機率，易受同儕壓力與熱銷榜單驅動。")
    
    # 我生者 (食傷) - Output / Expression
    shi_shen: float = Field(..., ge=0.0, le=1.0, description="食神 (Eating God): [Sensory Pleasure] 代表感性、美學、享受生活。高權重影響：重視體驗與美感，降低對價格的敏感度，追求舒適。")
    shang_guan: float = Field(..., ge=0.0, le=1.0, description="傷官 (Hurting Officer): [Rebellion/Innovation] 代表創新、叛逆。高權重顯著提升 `impulse_buying` (衝動消費) 與 `novelty_seeking` (追求新奇) 係數。偏好小眾、設計感強的商品。")

    # 我剋者 (財星) - Wealth / Control
    zheng_cai: float = Field(..., ge=0.0, le=1.0, description="正財 (Direct Wealth): [Pragmatism] 代表勤勉、保守。高權重影響：極度重視實用性與耐用度，降低衝動消費機率。")
    pian_cai: float = Field(..., ge=0.0, le=1.0, description="偏財 (Indirect Wealth): [Control/Speculation] 代表大方、投機。高權重影響：提升 `roi_sensitivity` (對高風險高回報的敏感度) 與豪爽消費傾向。")

    # 剋我者 (官殺) - Power / Discipline
    zheng_guan: float = Field(..., ge=0.0, le=1.0, description="正官 (Direct Officer): [Status/Norms] 代表規範、名聲。高權重影響：重視品牌聲譽與社會階級符號，偏好經典款。")
    qi_sha: float = Field(..., ge=0.0, le=1.0, description="七殺 (Seven Killings): [Authority/Risk] 代表魄力、權威。高權重顯著提升 `risk_tolerance` (風險承受度)，偏好高強度、高效率或極限風格的功能性商品。")

    # 生我者 (印星) - Resource / Support
    zheng_yin: float = Field(..., ge=0.0, le=1.0, description="正印 (Direct Resource): [Stability/Knowledge] 代表傳統、慈愛。高權重顯著提升 `trust_threshold` (信任門檻) 與 `brand_loyalty` (品牌忠誠)。偏好大品牌與權威認證。")
    pian_yin: float = Field(..., ge=0.0, le=1.0, description="偏印 (Indirect Resource): [Intuition/Unorthodox] 代表直覺、神秘。高權重影響：消費行為非主流，易受神秘感或特定利基市場 (Niche Market) 吸引。")


class OceanProfile(BaseModel):
    """
    OCEAN (Big Five) 五大人格特質模型
    """
    openness: float = Field(..., ge=0.0, le=1.0, description="開放性 (Openness): 對新經驗的開放程度。")
    conscientiousness: float = Field(..., ge=0.0, le=1.0, description="盡責性 (Conscientiousness): 自律、條理與成就導向。")
    extraversion: float = Field(..., ge=0.0, le=1.0, description="外向性 (Extraversion): 社交、活力與積極情感。")
    agreeableness: float = Field(..., ge=0.0, le=1.0, description="親和性 (Agreeableness): 利他、合作與信任。")
    neuroticism: float = Field(..., ge=0.0, le=1.0, description="神經質 (Neuroticism): 情緒不穩定性與焦慮傾向。")


class AgentProfile(BaseModel):
    """
    Agent 核心檔案 (Profile)
    
    整合了傳統命理學 (BaZi) 與現代心理學 (OCEAN) 的雙重維度，
    建構出立體且具備深層動機的虛擬人格。
    """
    id: str = Field(..., description="Agent 唯一識別碼")
    name: str = Field(..., description="Agent 顯示名稱")
    
    # 核心驅動引擎
    bazi: BaZiWeights = Field(..., description="八字十神權重：決定底層價值觀與消費動機")
    ocean: OceanProfile = Field(..., description="OCEAN 五大人格：決定外顯行為模式與溝通風格")
    
    description: str = Field("", description="人格文字描述")

    class Config:
        schema_extra = {
            "example": {
                "id": "agent_001",
                "name": "CyberMonk",
                "description": "一位融合傳統智慧與科技的修行者",
                "bazi": {
                    "bi_jian": 0.2, "jie_cai": 0.1,
                    "shi_shen": 0.5, "shang_guan": 0.8,
                    "zheng_cai": 0.1, "pian_cai": 0.3,
                    "zheng_guan": 0.2, "qi_sha": 0.4,
                    "zheng_yin": 0.1, "pian_yin": 0.9
                },
                "ocean": {
                    "openness": 0.9,
                    "conscientiousness": 0.5,
                    "extraversion": 0.3,
                    "agreeableness": 0.4,
                    "neuroticism": 0.6
                }
            }
        }

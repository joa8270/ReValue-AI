import random
import uuid
from typing import Dict
from backend.app.schemas.agent_profile import AgentProfile, BaZiWeights, OceanProfile

class AgentFactory:
    """
    Genesis Engine: 用於生成 Agent 實例的核心工廠。
    負責處理從「隨機混沌」到「有序人格」的演化過程。
    """

    @staticmethod
    def _gaussian_clamp(mu: float = 0.5, sigma: float = 0.15) -> float:
        """生成 0.0 ~ 1.0 之間的常態分佈隨機數"""
        val = random.gauss(mu, sigma)
        return max(0.0, min(1.0, val))

    @staticmethod
    def _balance_bazi_weights() -> Dict[str, float]:
        """
        模擬八字能量場的動態平衡 (Energy Conservation Law)
        
        邏輯：
        1. 隨機初始：先給予所有十神一個基礎隨機能量 (Base Potency)。
        2. 相剋相生：模擬真實命理中的「剋制」與「洩秀」關係。
           - 傷官見官 (Hurting Officer vs Direct Officer): 
             傷官代表叛逆，正官代表規則。傷官過旺必剋正官。
           - 財壞印 (Wealth vs Resource):
             對物質過於追求 (財)，往往會損耗精神層次與原則 (印)。
        """
        # 1. 初始混沌能量 (0.0 - 0.8，預留加成空間)
        keys = [
            "bi_jian", "jie_cai", 
            "shi_shen", "shang_guan", 
            "zheng_cai", "pian_cai", 
            "zheng_guan", "qi_sha", 
            "zheng_yin", "pian_yin"
        ]
        weights = {k: random.uniform(0.1, 0.9) for k in keys}

        # 2. 能量物理法則 (Physics of Fate)
        
        # Rule A: 傷官見官 (Clash: Hurting Officer -> Direct Officer)
        # 如果傷官 (Rebellion) 強，則正官 (Discipline) 必定被削弱
        if weights["shang_guan"] > 0.6:
            suppression_factor = weights["shang_guan"]  # 傷官越強，壓制力越大
            weights["zheng_guan"] *= (1.0 - suppression_factor * 0.8) # 強力壓制

        # Rule B: 財壞印 (Clash: Wealth -> Resource)
        # 如果偏財 (Speculation/Materialism) 強，則正印 (Principles/Stability) 被削弱
        if weights["pian_cai"] > 0.6:
            suppression_factor = weights["pian_cai"]
            weights["zheng_yin"] *= (1.0 - suppression_factor * 0.7)

        # Rule C: 比劫奪財 (Clash: Rob Wealth -> Direct Wealth)
        # 劫財 (Impulse/Peer) 強，正財 (Savings/Pragmatism) 保存不易
        if weights["jie_cai"] > 0.6:
            weights["zheng_cai"] *= 0.5

        # 3. 歸一化與修剪 (Normalization / Clamp)
        # 這裡不強求總合為 1，因為人的能量總量可以不同，但單項不能超標
        for k in weights:
            weights[k] = max(0.0, min(1.0, weights[k]))
            
        return weights

    @classmethod
    def create_random_agent(cls, location: str = "Taiwan") -> AgentProfile:
        """
        生成一個隨機 Agent 實例。
        
        Args:
            location: 用於未來擴充地區特定的機率參數 (目前僅作標記)
        """
        agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        
        # 1. 生成 OCEAN (常態分佈)
        ocean_data = {
            "openness": cls._gaussian_clamp(0.6, 0.2),         # 預設略微偏向開放
            "conscientiousness": cls._gaussian_clamp(0.5, 0.2),
            "extraversion": cls._gaussian_clamp(0.5, 0.2),
            "agreeableness": cls._gaussian_clamp(0.5, 0.2),
            "neuroticism": cls._gaussian_clamp(0.4, 0.2)       # 預設情緒稍穩
        }
        
        # 2. 生成 BaZi (能量平衡邏輯)
        bazi_data = cls._balance_bazi_weights()
        
        # 3. 簡單生成一些描述 (未來可接 LLM 生成)
        # 根據顯著特質給予標籤
        dominant_trait = max(bazi_data, key=bazi_data.get)
        bazi_labels = {
            "shang_guan": "由傷官驅動的創新者",
            "zheng_guan": "由正官驅動的守序者",
            "qi_sha": "由七殺驅動的實踐家",
            "pian_cai": "由偏財驅動的冒險家",
            "zheng_yin": "由正印驅動的思想家"
        }
        trait_desc = bazi_labels.get(dominant_trait, "多元價值觀的探索者")
        
        return AgentProfile(
            id=agent_id,
            name=f"SyntheUser_{agent_id[-4:]}",
            description=f"地點: {location} | 類型: {trait_desc}",
            bazi=BaZiWeights(**bazi_data),
            ocean=OceanProfile(**ocean_data)
        )

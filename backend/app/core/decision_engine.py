from typing import Dict, List
from pydantic import BaseModel, Field
from backend.app.schemas.agent_profile import AgentProfile

class DecisionResult(BaseModel):
    """
    決策結果物件
    """
    score: float = Field(..., ge=0.0, le=100.0, description="購買意願分數 (0-100)")
    reasoning: str = Field(..., description="決策背後的邏輯與心理獨白")
    dominant_factors: List[str] = Field(default_factory=list, description="影響決策的主導因子 (如: 'High Hurting Officer', 'Low Direct Resource')")


class DecisionBrain:
    """
    Decision Brain: 模擬 Consumer Agent 的購買決策大腦
    核心算法：映射「八字能量」至「產品特徵」的加權計分系統。
    """

    @staticmethod
    def calculate_purchase_intent(agent: AgentProfile, product_features: Dict[str, bool]) -> DecisionResult:
        """
        計算購買意願 (Purchase Intent)

        Args:
            agent: AgentProfile 實例
            product_features: 產品特徵字典 (e.g., {"is_innovation": True, "has_social_proof": True})

        Returns:
            DecisionResult: 分數與理由
        """
        weights = agent.bazi
        
        # 基礎分數 (Base Score) - 預設 50 分 (中立)
        score = 50.0
        reasons = []
        factors = []

        # --- Logic A: 創新與叛逆 (Innovation vs Tradition) ---
        if product_features.get("is_innovation", False):
            # 正向加分：傷官 (Rebellion) + 偏財 (Speculation)
            boost = (weights.shang_guan * 15) + (weights.pian_cai * 10)
            score += boost
            
            # 負向扣分：正官 (Conformity) + 正印 (Stability) - 保守派不喜歡太新的東西
            penalty = (weights.zheng_guan * 10) + (weights.zheng_yin * 10)
            score -= penalty

            if boost > 15:
                reasons.append(f"傷官({weights.shang_guan:.2f})受到創新特質吸引")
                factors.append("High Hurting Officer")
            if penalty > 15:
                reasons.append(f"正官({weights.zheng_guan:.2f})覺得這產品太過前衛不穩重")
                factors.append("High Direct Officer")

        # --- Logic B: 社會認同與跟風 (Social Proof / FOMO) ---
        if product_features.get("has_social_proof", False):
            # 劫財 (Rob Wealth) 代表容易受同儕影響、羊群效應
            jiecai_impact = weights.jie_cai * 25
            score += jiecai_impact
            
            if jiecai_impact > 15:
                reasons.append(f"劫財({weights.jie_cai:.2f})看到熱銷榜單就忍不住想買")
                factors.append("High Rob Wealth")
            elif weights.bi_jian > 0.7:
                # 比肩 (Self) 強的人，反而可能因為太多人買而不想買 (雖題目未要求，但符合邏輯，此處僅作微調)
                score -= 5
                reasons.append("比肩過強，不喜歡隨波逐流")

        # --- Logic C: 安全感與認證 (Safety & Trust) ---
        if product_features.get("has_certification", False):
            # 正印 (Direct Resource) 極度重視權威與證書
            zhengyin_impact = weights.zheng_yin * 30
            score += zhengyin_impact

            if zhengyin_impact > 15:
                reasons.append(f"正印({weights.zheng_yin:.2f})看到認證感到非常心安")
                factors.append("High Direct Resource")
        
        # --- Logic D: 性價比/CP值 (Pragmatism) --- (額外補充，增強完整性)
        if product_features.get("good_value_for_money", False): # 假設輸入有此欄位
             zhengcai_impact = weights.zheng_cai * 20
             score += zhengcai_impact
             if zhengcai_impact > 12: 
                 reasons.append(f"正財({weights.zheng_cai:.2f})認可此產品的高CP值")

        # 最終分數截斷 (Clamp)
        final_score = max(0.0, min(100.0, score))

        # 產生最終 Reasoning Summary
        if not reasons:
            summary = "對此產品感覺平淡，無特殊動機驅動。"
        else:
            summary = "，".join(reasons) + "。"

        return DecisionResult(
            score=final_score,
            reasoning=summary,
            dominant_factors=factors
        )

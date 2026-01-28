"""
MIRRA ABM Engine V1.0 - 東西方混合方法論模擬引擎

融合架構：
    - 東方元素：八字格局作為Agent基因，五行作為決策偏好，大運作為狀態演化
    - 西方元素：Agent-Based Modeling框架，網絡效應，突現行為分析

理論基礎：
    1. Symbolic Interactionism（象徵互動論）：市民基於產品符號意義互動
    2. Phenomenology（現象學）：市民的主觀體驗影響決策
    3. Five Elements Theory（五行理論）：偏好與相剋關係建模
"""

import random
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime
from dataclasses import dataclass, field


# ===== 五行互動矩陣 =====
ELEMENT_INTERACTION_MATRIX = {
    # 五行相生相剋關係 → 轉換為社交影響力係數
    # influence_weight: 當兩個市民互動時，五行關係影響意見傳播強度
    ("Wood", "Wood"):  {"affinity": 0.6, "influence_weight": 1.0},   # 同類相吸
    ("Wood", "Fire"):  {"affinity": 0.9, "influence_weight": 1.3},   # 木生火（強正向）
    ("Wood", "Earth"): {"affinity": 0.3, "influence_weight": 0.6},   # 木剋土（負向）
    ("Wood", "Metal"): {"affinity": 0.2, "influence_weight": 0.5},   # 金剋木（被剋）
    ("Wood", "Water"): {"affinity": 0.8, "influence_weight": 1.2},   # 水生木（受益）
    
    ("Fire", "Fire"):  {"affinity": 0.6, "influence_weight": 1.0},
    ("Fire", "Earth"): {"affinity": 0.9, "influence_weight": 1.3},   # 火生土
    ("Fire", "Metal"): {"affinity": 0.3, "influence_weight": 0.6},   # 火剋金
    ("Fire", "Water"): {"affinity": 0.2, "influence_weight": 0.5},   # 水剋火
    ("Fire", "Wood"):  {"affinity": 0.8, "influence_weight": 1.2},   # 木生火
    
    ("Earth", "Earth"):  {"affinity": 0.6, "influence_weight": 1.0},
    ("Earth", "Metal"): {"affinity": 0.9, "influence_weight": 1.3},  # 土生金
    ("Earth", "Water"): {"affinity": 0.3, "influence_weight": 0.6},  # 土剋水
    ("Earth", "Wood"):  {"affinity": 0.2, "influence_weight": 0.5},  # 木剋土
    ("Earth", "Fire"):  {"affinity": 0.8, "influence_weight": 1.2},  # 火生土
    
    ("Metal", "Metal"):  {"affinity": 0.6, "influence_weight": 1.0},
    ("Metal", "Water"): {"affinity": 0.9, "influence_weight": 1.3},  # 金生水
    ("Metal", "Wood"):  {"affinity": 0.3, "influence_weight": 0.6},  # 金剋木
    ("Metal", "Fire"):  {"affinity": 0.2, "influence_weight": 0.5},  # 火剋金
    ("Metal", "Earth"): {"affinity": 0.8, "influence_weight": 1.2},  # 土生金
    
    ("Water", "Water"):  {"affinity": 0.6, "influence_weight": 1.0},
    ("Water", "Wood"):  {"affinity": 0.9, "influence_weight": 1.3},  # 水生木
    ("Water", "Fire"):  {"affinity": 0.3, "influence_weight": 0.6},  # 水剋火
    ("Water", "Earth"): {"affinity": 0.2, "influence_weight": 0.5},  # 土剋水
    ("Water", "Metal"): {"affinity": 0.8, "influence_weight": 1.2},  # 金生水
}


# ===== 格局決策傾向 =====
STRUCTURE_DECISION_PROFILE = {
    # 每種八字格局對應不同的消費/決策特質
    "正官格": {
        "risk_tolerance": 0.3,      # 風險承受度（0-1）
        "price_sensitivity": 0.6,   # 價格敏感度
        "brand_loyalty": 0.8,       # 品牌忠誠度
        "innovation_adoption": 0.4, # 創新採納度
        "social_influence": 0.7,    # 受社交影響度
        "decision_speed": 0.5,      # 決策速度（越高越衝動）
    },
    "七殺格": {
        "risk_tolerance": 0.9,
        "price_sensitivity": 0.3,
        "brand_loyalty": 0.4,
        "innovation_adoption": 0.9,
        "social_influence": 0.3,
        "decision_speed": 0.9,
    },
    "正財格": {
        "risk_tolerance": 0.2,
        "price_sensitivity": 0.8,
        "brand_loyalty": 0.7,
        "innovation_adoption": 0.3,
        "social_influence": 0.6,
        "decision_speed": 0.4,
    },
    "偏財格": {
        "risk_tolerance": 0.7,
        "price_sensitivity": 0.4,
        "brand_loyalty": 0.5,
        "innovation_adoption": 0.7,
        "social_influence": 0.8,
        "decision_speed": 0.7,
    },
    "正印格": {
        "risk_tolerance": 0.4,
        "price_sensitivity": 0.5,
        "brand_loyalty": 0.8,
        "innovation_adoption": 0.5,
        "social_influence": 0.7,
        "decision_speed": 0.3,
    },
    "偏印格": {
        "risk_tolerance": 0.6,
        "price_sensitivity": 0.5,
        "brand_loyalty": 0.3,
        "innovation_adoption": 0.9,
        "social_influence": 0.2,
        "decision_speed": 0.6,
    },
    "食神格": {
        "risk_tolerance": 0.5,
        "price_sensitivity": 0.4,
        "brand_loyalty": 0.6,
        "innovation_adoption": 0.6,
        "social_influence": 0.7,
        "decision_speed": 0.6,
    },
    "傷官格": {
        "risk_tolerance": 0.8,
        "price_sensitivity": 0.3,
        "brand_loyalty": 0.3,
        "innovation_adoption": 0.9,
        "social_influence": 0.4,
        "decision_speed": 0.8,
    },
    "建祿格": {
        "risk_tolerance": 0.7,
        "price_sensitivity": 0.5,
        "brand_loyalty": 0.6,
        "innovation_adoption": 0.6,
        "social_influence": 0.4,
        "decision_speed": 0.5,
    },
    "羊刃格": {
        "risk_tolerance": 0.9,
        "price_sensitivity": 0.2,
        "brand_loyalty": 0.4,
        "innovation_adoption": 0.7,
        "social_influence": 0.3,
        "decision_speed": 0.9,
    },
    "從財格": {
        "risk_tolerance": 0.6,
        "price_sensitivity": 0.7,
        "brand_loyalty": 0.5,
        "innovation_adoption": 0.5,
        "social_influence": 0.9,  # 極度受社交影響
        "decision_speed": 0.7,
    },
    "從殺格": {
        "risk_tolerance": 0.8,
        "price_sensitivity": 0.4,
        "brand_loyalty": 0.7,
        "innovation_adoption": 0.6,
        "social_influence": 0.8,
        "decision_speed": 0.6,
    },
    "從兒格": {
        "risk_tolerance": 0.7,
        "price_sensitivity": 0.3,
        "brand_loyalty": 0.4,
        "innovation_adoption": 0.9,
        "social_influence": 0.5,
        "decision_speed": 0.8,
    },
    "專旺格": {
        "risk_tolerance": 0.5,
        "price_sensitivity": 0.6,
        "brand_loyalty": 0.9,
        "innovation_adoption": 0.4,
        "social_influence": 0.3,
        "decision_speed": 0.4,
    },
}


@dataclass
class CitizenAgent:
    """
    虛擬市民Agent（融合八字參數的自主個體）
    
    Attributes:
        id: 市民唯一識別碼
        bazi_profile: 八字命盤資料（東方參數）
        decision_profile: 決策特質（由八字推導）
        current_opinion: 當前對產品的意見分數 (0-100)
        opinion_history: 意見演化歷史
        influenced_by: 受誰影響的記錄
        neighbors: 社交網絡鄰居
    """
    id: str
    name: str
    age: int
    element: str  # 五行屬性
    structure: str  # 八字格局
    bazi_profile: Dict
    gender: str = "unknown" # 新增
    occupation: str = "unknown" # 新增
    
    # ABM核心屬性
    decision_profile: Dict = field(default_factory=dict)
    current_opinion: float = 0.0
    initial_opinion: float = 0.0
    opinion_history: List[float] = field(default_factory=list)
    influenced_by: List[str] = field(default_factory=list)
    neighbors: List[str] = field(default_factory=list)
    
    # 狀態標記
    is_opinion_leader: bool = False
    activation_threshold: float = 0.5  # 意見改變的啟動閾值
    
    def __post_init__(self):
        """初始化決策特質（基於八字格局）"""
        self.decision_profile = STRUCTURE_DECISION_PROFILE.get(
            self.structure, 
            STRUCTURE_DECISION_PROFILE["正官格"]  # 預設
        )
        self.activation_threshold = random.uniform(0.3, 0.7)
    
    def calculate_initial_opinion(self, product_element: str, product_price: float, market_price: float, targeting_bonus: float = 0.0) -> float:
        """
        計算初始意見（基於五行相性 + 價格敏感度 + 定錨加權）
        
        Args:
            product_element: 產品的五行屬性（由AI判斷）
            product_price: 產品售價
            market_price: 市場均價
            targeting_bonus: 定錨加權分數 (Targeting Bonus)
        
        Returns:
            初始意見分數 (0-100)
        """
        # 1. 五行相性影響 (40% weight)
        element_key = (self.element, product_element)
        element_affinity = ELEMENT_INTERACTION_MATRIX.get(element_key, {}).get("affinity", 0.5)
        element_score = element_affinity * 40
        
        # 2. 價格因素 (30% weight)
        price_ratio = product_price / market_price if market_price > 0 else 1.0
        price_sensitivity = self.decision_profile["price_sensitivity"]
        
        if price_ratio > 1.2:  # 貴20%以上
            price_score = (1 - price_sensitivity) * 30  # 價格敏感度高的人給低分
        elif price_ratio < 0.8:  # 便宜20%以上
            price_score = 30  # 便宜大家都喜歡
        else:
            price_score = 25
        
        # 3. 創新採納度 (20% weight)
        innovation_score = self.decision_profile["innovation_adoption"] * 20
        
        # 4. 隨機擾動 (10% weight)
        random_factor = random.uniform(-5, 5)
        
        base_score = element_score + price_score + innovation_score + random_factor + targeting_bonus
        
        # 大運調整（正處於好運期的人更樂觀）
        luck_bonus = self._get_current_luck_modifier()
        
        final_score = max(0, min(100, base_score + luck_bonus))
        
        self.initial_opinion = final_score
        self.current_opinion = final_score
        self.opinion_history.append(final_score)
        
        return final_score
    
    def _get_current_luck_modifier(self) -> float:
        """根據當前大運狀態調整意見（-10 ~ +10）"""
        current_luck = self.bazi_profile.get("current_luck", {})
        luck_desc = current_luck.get("description", "")
        
        # 根據大運描述判斷運勢好壞
        positive_keywords = ["旺", "收穫", "升遷", "機會", "順利", "享受"]
        negative_keywords = ["挑戰", "競爭", "壓力", "沉澱", "困難"]
        
        positive_count = sum(1 for kw in positive_keywords if kw in luck_desc)
        negative_count = sum(1 for kw in negative_keywords if kw in luck_desc)
        
        return (positive_count - negative_count) * 3.0
    
    def update_opinion_via_interaction(self, neighbor_opinions: List[Tuple[str, float, str]], convergence_rate: float = 0.3):
        """
        基於鄰居意見更新自己的意見（象徵互動論核心機制）
        
        Args:
            neighbor_opinions: [(neighbor_id, neighbor_opinion, neighbor_element), ...]
            convergence_rate: 意見收斂速率（0-1）
        """
        if not neighbor_opinions:
            return
        
        # 計算加權平均意見
        weighted_sum = 0.0
        weight_total = 0.0
        
        for neighbor_id, neighbor_opinion, neighbor_element in neighbor_opinions:
            # 五行相性決定影響權重
            element_key = (self.element, neighbor_element)
            influence_weight = ELEMENT_INTERACTION_MATRIX.get(element_key, {}).get("influence_weight", 1.0)
            
            # 社交影響敏感度
            social_weight = self.decision_profile["social_influence"]
            
            final_weight = influence_weight * social_weight
            
            weighted_sum += neighbor_opinion * final_weight
            weight_total += final_weight
            
            # 記錄受影響來源
            if abs(neighbor_opinion - self.current_opinion) > 10:
                self.influenced_by.append(neighbor_id)
        
        if weight_total == 0:
            return
        
        # 計算鄰居平均意見
        neighbor_avg = weighted_sum / weight_total
        
        # 只有差異超過啟動閾值才改變意見
        opinion_diff = abs(neighbor_avg - self.current_opinion)
        if opinion_diff < self.activation_threshold * 10:
            return
        
        # 更新意見（部分收斂）
        new_opinion = self.current_opinion + (neighbor_avg - self.current_opinion) * convergence_rate
        
        self.current_opinion = max(0, min(100, new_opinion))
        self.opinion_history.append(self.current_opinion)
    
    def get_sentiment(self) -> str:
        """根據當前意見判斷情緒"""
        if self.current_opinion >= 70:
            return "positive"
        elif self.current_opinion <= 40:
            return "negative"
        else:
            return "neutral"
    
    def get_opinion_change(self) -> float:
        """計算意見變化幅度"""
        if len(self.opinion_history) < 2:
            return 0.0
        return self.opinion_history[-1] - self.opinion_history[0]


class ABMSimulation:
    """
    Agent-Based Modeling 模擬引擎
    
    模擬流程：
        1. 初始化：每個Agent基於八字計算初始意見
        2. 網絡構建：根據五行相性建立社交網絡
        3. 迭代互動：多輪意見交換與更新
        4. 突現分析：統計群體行為模式
    """
    
    def __init__(self, citizens: List[Dict], product_info: Dict, targeting: Dict = None, expert_mode: bool = False):
        """
        Args:
            citizens: 市民資料列表（來自資料庫）
            product_info: 產品資訊 {"element": "Fire", "price": 500, "market_price": 450}
            targeting: 受眾定錨設定 {"age_range": [20, 60], "gender": "male", ...}
            expert_mode: 是否開啟專家模式 (高難度/嚴格)
        """
        self.agents: List[CitizenAgent] = []
        self.product_info = product_info
        self.targeting = targeting
        self.expert_mode = expert_mode
        self.iteration_count = 0
        self.network_edges = []
        self.history = []  # Record average opinion per round
        self.logs = []     # Record text logs
        
        # 初始化Agents
        for c in citizens:
            # 優先使用 top-level element (已被 database.py 的隨機補丁修正)
            element = c.get("element") or bazi.get("element", "Fire")
            
            agent = CitizenAgent(
                id=str(c["id"]),
                name=c["name"],
                age=c["age"],
                element=element,
                structure=bazi.get("structure", "正官格"),
                bazi_profile=bazi,
                gender=c.get("gender", "unknown"),
                occupation=c.get("occupation", "unknown")
            )
            # Expert Mode: 增加挑戰性
            if self.expert_mode:
                agent.activation_threshold += 0.2  # 更難被說服
                
            self.agents.append(agent)
        
        print(f"🧬 [ABM] 已初始化 {len(self.agents)} 個 Agent (Expert: {expert_mode}, Target: {targeting})")

    def build_social_network(self, network_type: str = "element_based"):
        """
        構建社交網絡（基於五行相性）
        
        Args:
            network_type: "element_based" (五行相性網絡) 或 "random" (隨機網絡)
        """
        if network_type == "element_based":
            # 五行相性網絡：相生關係的Agent互相連接
            for i, agent in enumerate(self.agents):
                potential_neighbors = []
                for j, other in enumerate(self.agents):
                    if i == j:
                        continue
                    
                    element_key = (agent.element, other.element)
                    affinity = ELEMENT_INTERACTION_MATRIX.get(element_key, {}).get("affinity", 0.5)
                    
                    # 親和度高於0.6的才建立連接
                    if affinity > 0.6:
                        potential_neighbors.append(other.id)
                
                # 每個Agent保留3-7個鄰居
                num_neighbors = min(random.randint(3, 7), len(potential_neighbors))
                agent.neighbors = random.sample(potential_neighbors, num_neighbors) if potential_neighbors else []
                
                for neighbor_id in agent.neighbors:
                    self.network_edges.append((agent.id, neighbor_id))
        
        else:
            # 隨機網絡（對照組）
            for agent in self.agents:
                num_neighbors = random.randint(3, 7)
                others = [a.id for a in self.agents if a.id != agent.id]
                agent.neighbors = random.sample(others, min(num_neighbors, len(others)))
        
        avg_degree = np.mean([len(a.neighbors) for a in self.agents])
        print(f"📊 [ABM] 社交網絡已建立，平均度數: {avg_degree:.2f}")

    def initialize_opinions(self):
        """初始化所有Agent的意見 (含 Targeting 與 Expert Mode 邏輯)"""
        product_element = self.product_info.get("element", "Fire")
        product_price = self.product_info.get("price", 100)
        market_price = self.product_info.get("market_price", 100)
        
        for agent in self.agents:
            bonus = 0.0
            
            # 1. Targeting Match Logic
            if self.targeting:
                is_match = True
                
                # Age Check
                if "age_range" in self.targeting:
                    r = self.targeting["age_range"]
                    # r should be [min, max]
                    if isinstance(r, list) and len(r) == 2:
                        if agent.age < r[0] or agent.age > r[1]:
                            is_match = False
                
                # Gender Check
                if is_match and "gender" in self.targeting:
                    g = self.targeting["gender"]
                    if g != "all":
                        # 簡單模糊比對
                        ag_gen = str(agent.gender).lower()
                        if g == "male" and ag_gen not in ["male", "男"]: is_match = False
                        elif g == "female" and ag_gen not in ["female", "女"]: is_match = False
                
                # Occupation Check (MVP: Skip fuzzy match if risk is high, or simple id match)
                if is_match and "occupations" in self.targeting:
                    occs = self.targeting["occupations"]
                    if occs and len(occs) > 0:
                        # 假設 agent.occupation 可能是中文，這裡先不嚴格過濾，避免篩光
                        # 若要嚴格：
                        # if agent.occupation not in occs: is_match = False
                        pass 

                if is_match:
                    bonus += 15.0 # 符合受眾者，初始意圖較高
            
            # 2. Expert Mode Logic
            if self.expert_mode:
                bonus -= 15.0 # 全體初始意願下降 (更殘酷)
            
            agent.calculate_initial_opinion(product_element, product_price, market_price, targeting_bonus=bonus)
        
        avg_opinion = np.mean([a.current_opinion for a in self.agents]) if self.agents else 0.0
        if np.isnan(avg_opinion): avg_opinion = 0.0
        self.history.append(float(avg_opinion)) # Record initial state
        self.logs.append(f"初始化意見分佈：平均 {avg_opinion:.1f}")
        print(f"💭 [ABM] 初始意見分佈：平均 {avg_opinion:.1f}，標準差 {np.std([a.current_opinion for a in self.agents]):.1f}")
    
    def run_iterations(self, num_iterations: int = 5, convergence_rate: float = 0.3):
        """
        執行多輪互動模擬
        
        Args:
            num_iterations: 迭代次數
            convergence_rate: 每輪的意見收斂速率
        """
        agent_map = {a.id: a for a in self.agents}
        
        for iteration in range(num_iterations):
            # 每輪隨機打亂更新順序（避免順序偏差）
            random.shuffle(self.agents)
            
            # 記錄變化
            changed_count = 0
            
            for agent in self.agents:
                # 獲取鄰居意見
                neighbor_opinions = []
                for neighbor_id in agent.neighbors:
                    neighbor = agent_map.get(neighbor_id)
                    if neighbor:
                        neighbor_opinions.append((
                            neighbor.id, 
                            neighbor.current_opinion, 
                            neighbor.element
                        ))
                
                # 更新意見
                old_op = agent.current_opinion
                agent.update_opinion_via_interaction(neighbor_opinions, convergence_rate)
                if abs(agent.current_opinion - old_op) > 1.0:
                    changed_count += 1
            
            self.iteration_count += 1
            avg_opinion = float(np.mean([a.current_opinion for a in self.agents])) if self.agents else 0.0
            if np.isnan(avg_opinion): avg_opinion = 0.0
            self.history.append(avg_opinion)
            
            # Generate log
            log_msg = f"迭代 {self.iteration_count}: 平均意見 {avg_opinion:.1f} (活躍人數: {changed_count})"
            self.logs.append(log_msg)
            print(f"🔄 [ABM] {log_msg}")
    
    def identify_opinion_leaders(self, top_n: int = 5):
        """識別意見領袖（影響力最大的Agent）"""
        # 計算影響力：被影響次數 + 網絡中心度
        influence_scores = {}
        for agent in self.agents:
            times_influenced_others = sum(
                1 for other in self.agents if agent.id in other.influenced_by
            )
            network_centrality = len(agent.neighbors)
            influence_scores[agent.id] = times_influenced_others * 2 + network_centrality
        
        # 排序選出Top N
        sorted_leaders = sorted(influence_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        agent_map = {a.id: a for a in self.agents}
        for agent_id, score in sorted_leaders:
            agent = agent_map[agent_id]
            agent.is_opinion_leader = True
            print(f"👑 [ABM] 意見領袖：{agent.name} (影響力分數: {score})")
    
    def analyze_emergence(self) -> Dict:
        """
        分析突現行為（群體層面的模式）
        
        Returns:
            突現行為分析報告
        """
        opinions = [a.current_opinion for a in self.agents]
        opinion_changes = [a.get_opinion_change() for a in self.agents]
        
        # 極化程度（兩極分化）
        polarization = np.std(opinions) / 50  # 標準化到0-1
        
        # 共識程度（大家意見接近）
        consensus = 1 - polarization
        
        # 從眾效應強度（意見變化幅度）
        herding_strength = np.mean([abs(change) for change in opinion_changes])
        
        # 分組統計：五行與格局
        element_groups = {}
        structure_groups = {}
        element_initial_groups = {}
        
        for agent in self.agents:
            # 五行分組
            elem = agent.element
            if elem not in element_groups:
                element_groups[elem] = []
                element_initial_groups[elem] = []
            element_groups[elem].append(agent.current_opinion)
            element_initial_groups[elem].append(agent.initial_opinion)
            
            # 格局分組
            struct = agent.structure
            if struct not in structure_groups:
                structure_groups[struct] = []
            structure_groups[struct].append(agent.current_opinion)
        
        element_avg = {elem: float(np.mean(ops)) for elem, ops in element_groups.items()}
        element_initial_avg = {elem: float(np.mean(ops)) for elem, ops in element_initial_groups.items()}
        structure_avg = {struct: float(np.mean(ops)) for struct, ops in structure_groups.items()}
        
        return {
            "average_opinion": float(np.nan_to_num(np.mean(opinions))),
            "opinion_std": float(np.nan_to_num(np.std(opinions))),
            "polarization": float(np.nan_to_num(polarization)),
            "consensus": float(np.nan_to_num(consensus)),
            "herding_strength": float(np.nan_to_num(herding_strength)),
            "element_preferences": {k: float(np.nan_to_num(v)) for k, v in element_avg.items()},
            "element_initial_preferences": {k: float(np.nan_to_num(v)) for k, v in element_initial_avg.items()},
            "structure_preferences": {k: float(np.nan_to_num(v)) for k, v in structure_avg.items()},
            "total_iterations": self.iteration_count,
            "network_density": len(self.network_edges) / (len(self.agents) * (len(self.agents) - 1) / 2) if len(self.agents) > 1 else 0
        }
    
    def get_final_comments(self, num_comments: int = 10) -> List[Dict]:
        """
        獲取最終評論（選擇代表性Agent）
        
        選擇策略：
            - 意見領袖優先
            - 五行均衡分佈
            - 意見多樣性（正負中性均衡）
        """
        # 1. 優先選擇意見領袖
        leaders = [a for a in self.agents if a.is_opinion_leader]
        selected = leaders[:min(3, len(leaders))]
        
        # 2. 按情緒類型選擇
        remaining_agents = [a for a in self.agents if a not in selected]
        
        positive_agents = [a for a in remaining_agents if a.get_sentiment() == "positive"]
        negative_agents = [a for a in remaining_agents if a.get_sentiment() == "negative"]
        neutral_agents = [a for a in remaining_agents if a.get_sentiment() == "neutral"]
        
        # 均衡選擇
        selected.extend(random.sample(positive_agents, min(3, len(positive_agents))))
        selected.extend(random.sample(negative_agents, min(2, len(negative_agents))))
        selected.extend(random.sample(neutral_agents, min(2, len(neutral_agents))))
        
        # 3. 補足數量
        if len(selected) < num_comments:
            remaining = [a for a in self.agents if a not in selected]
            selected.extend(random.sample(remaining, min(num_comments - len(selected), len(remaining))))
        
        # 4. 生成評論結構
        comments = []
        for agent in selected[:num_comments]:
            comments.append({
                "citizen_id": agent.id,
                "name": agent.name,
                "age": agent.age,
                "gender": agent.gender,
                "occupation": agent.occupation,
                "element": agent.element,
                "structure": agent.structure,
                "sentiment": agent.get_sentiment(),
                "opinion_score": round(agent.current_opinion, 1),
                "opinion_change": round(agent.get_opinion_change(), 1),
                "is_leader": agent.is_opinion_leader,
                "influenced_count": len(agent.influenced_by),
                # 評論文本需要由AI生成（基於這些參數）
                "abm_context": {
                    "initial_opinion": agent.initial_opinion,
                    "final_opinion": agent.current_opinion,
                    "neighbors_avg": np.mean([self._get_agent_by_id(nid).current_opinion for nid in agent.neighbors]) if agent.neighbors else agent.current_opinion
                }
            })
        
        return comments
    
    def _get_agent_by_id(self, agent_id: str) -> CitizenAgent:
        """根據ID獲取Agent"""
        for agent in self.agents:
            if agent.id == agent_id:
                return agent
        return self.agents[0]  # 防呆


# ===== 輔助函數：產品五行屬性判斷 =====
def infer_product_element(product_name: str, product_category: str) -> str:
    """
    推斷產品的五行屬性（簡化版，實際應由AI判斷）
    
    Args:
        product_name: 產品名稱
        product_category: 產品類別
    
    Returns:
        五行屬性 ("Fire", "Water", "Metal", "Wood", "Earth")
    """
    # 關鍵字映射
    keyword_map = {
        "Fire": ["電子", "科技", "3C", "燈", "手機", "電腦", "加熱", "紅色"],
        "Water": ["飲料", "水", "清潔", "化妝品", "黑色", "藍色", "流動"],
        "Metal": ["金屬", "工具", "硬體", "白色", "銀色", "精密", "樂器"],
        "Wood": ["木質", "植物", "書", "文具", "綠色", "環保", "生長"],
        "Earth": ["食品", "陶瓷", "建材", "黃色", "褐色", "土", "穩定"]
    }
    
    product_text = product_name + " " + product_category
    
    for element, keywords in keyword_map.items():
        if any(kw in product_text for kw in keywords):
            return element
    
    return "Fire"  # 預設


if __name__ == "__main__":
    # 測試用例
    print("=" * 60)
    print("🧬 MIRRA ABM Engine 測試")
    print("=" * 60)
    
    # 模擬市民資料
    test_citizens = [
        {
            "id": i,
            "name": f"市民{i}",
            "age": 25 + i,
            "bazi_profile": {
                "element": random.choice(["Fire", "Water", "Metal", "Wood", "Earth"]),
                "structure": random.choice(list(STRUCTURE_DECISION_PROFILE.keys())),
                "current_luck": {"description": "財運旺盛"}
            }
        }
        for i in range(30)
    ]
    
    # 產品資訊
    product = {
        "element": "Fire",
        "price": 500,
        "market_price": 450
    }
    
    # 執行模擬
    sim = ABMSimulation(test_citizens, product)
    sim.build_social_network("element_based")
    sim.initialize_opinions()
    sim.run_iterations(num_iterations=5)
    sim.identify_opinion_leaders(top_n=3)
    
    # 分析結果
    emergence = sim.analyze_emergence()
    print("\n📊 突現行為分析：")
    for key, value in emergence.items():
        print(f"  {key}: {value}")
    
    # 獲取評論
    comments = sim.get_final_comments(num_comments=10)
    print(f"\n💬 已生成 {len(comments)} 則評論（需AI填補文字）")

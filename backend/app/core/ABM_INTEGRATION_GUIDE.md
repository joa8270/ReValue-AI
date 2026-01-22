# 🧬 MIRRA ABM 融合架構完全指南

## 📚 理論基礎

### 為什麼需要融合東西方方法論？

#### **問題**：單純使用AI角色扮演的局限性
目前的實現方式：
```
1000位市民 → 隨機抽30人 → AI讀取參數 → AI「假裝」是這30人說話
```

**缺陷**：
- ❌ 市民之間沒有真正互動
- ❌ 無法產生突現行為 (Emergent Behavior)
- ❌ 缺乏時間動態演化
- ❌ 不符合ABM的學術定義

#### **解決方案**：真正的ABM架構
```
1000位市民 → 每個人是獨立Agent → 基於八字參數決策 → 互相影響 → 產生群體現象
```

**優勢**：
- ✅ 符合Agent-Based Modeling學術標準
- ✅ 產生真實的社交動力學 (Social Dynamics)
- ✅ 可觀察到「從眾效應」、「意見領袖」、「兩極分化」等現象
- ✅ 結果更具解釋力與可信度

---

## 🏗️ 融合架構設計

### Layer 1: 八字系統作為「Agent基因」

每個虛擬市民的八字參數 → 轉換為ABM可用的決策特質

```python
八字格局: "正官格"
    ↓ 轉換
ABM決策特質:
    - risk_tolerance: 0.3      (低風險偏好)
    - price_sensitivity: 0.6   (中等價格敏感)
    - social_influence: 0.7    (較易受社交影響)
    - innovation_adoption: 0.4 (保守創新態度)
```

**14種格局 → 14種不同的Agent類型**

### Layer 2: 五行理論作為「互動規則」

五行相生相剋 → 轉換為社交影響力係數

```python
互動矩陣範例:
    木生火: influence_weight = 1.3  (影響力強)
    木剋土: influence_weight = 0.6  (影響力弱)
    火剋金: influence_weight = 0.5  (相斥)
```

**意義**：
- 五行相生的Agent → 容易相互影響意見
- 五行相剋的Agent → 意見衝突、難以說服

### Layer 3: 10年大運作為「狀態修正器」

當前大運 → 調整Agent的決策傾向

```python
正財運: +5分樂觀修正（財運好，心情好）
七殺運: -3分悲觀修正（壓力大，挑剔）
```

### Layer 4: ABM框架提供「動態演化」

```
時間 T0（初始）:
    Agent A: opinion = 60分（基於八字計算）
    Agent B: opinion = 50分
    
時間 T1（第1輪互動）:
    A看到鄰居B的意見 → 受五行影響調整 → opinion = 58分
    
時間 T2（第2輪互動）:
    A再次受鄰居影響 → opinion = 56分
    
...（持續演化）

時間 T5（穩定後）:
    A: opinion = 54分（最終意見）
```

---

## 🔄 完整模擬流程

### 階段1：Agent初始化（東方參數建構）

```python
from app.core.abm_engine import ABMSimulation
from app.core.database import get_random_citizens

# 1. 從資料庫抽取市民
citizens = get_random_citizens(sample_size=30)

# 2. 產品五行屬性判斷（由AI或規則判斷）
product_info = {
    "element": "Fire",  # 例如：3C產品屬火
    "price": 500,
    "market_price": 450
}

# 3. 初始化ABM模擬
sim = ABMSimulation(citizens, product_info)
```

**此時每個市民已被轉換為CitizenAgent：**
- 擁有八字基因
- 擁有決策特質
- 尚未有社交網絡

### 階段2：社交網絡構建（西方結構建模）

```python
# 4. 構建五行相性網絡
sim.build_social_network(network_type="element_based")
```

**網絡構建邏輯**：
```
甲市民（Wood） → 尋找相生對象 → 找到乙市民（Fire）
甲市民 ←→ 乙市民（建立連接）

甲市民（Wood） → 遇到丙市民（Metal）
五行相剋 → 不建立連接
```

**結果**：
- 每個Agent有3-7個「鄰居」
- 鄰居關係基於五行親和度
- 形成小世界網絡 (Small-World Network)

### 階段3：初始意見計算（東西融合）

```python
# 5. 計算每個Agent的初始意見
sim.initialize_opinions()
```

**計算公式**：
```python
初始意見 = 五行相性影響(40%) 
         + 價格因素(30%)          # 基於格局的價格敏感度
         + 創新採納度(20%)        # 基於格局的冒險精神
         + 隨機擾動(10%)
         + 大運加成(-10~+10分)    # 東方時間動態
```

### 階段4：多輪互動模擬（ABM核心）

```python
# 6. 執行5輪意見演化
sim.run_iterations(num_iterations=5, convergence_rate=0.3)
```

**每輪互動發生什麼**：
1. Agent A 檢視所有鄰居的當前意見
2. 計算加權平均（權重由五行相性決定）
3. 如果差異超過啟動閾值 → 調整自己的意見
4. 記錄「被誰影響」

**突現現象**：
- 🔥 **從眾效應**：少數意見領袖帶動群體
- ⚡ **兩極分化**：相剋關係導致意見對立
- 🌊 **級聯傳播**：意見像波浪擴散

### 階段5：意見領袖識別（社會網絡分析）

```python
# 7. 找出影響力最大的Agent
sim.identify_opinion_leaders(top_n=5)
```

**影響力計算**：
```
影響力 = 影響他人次數 × 2 + 網絡中心度
```

**意義**：
- KOL識別
- 病毒式行銷的種子用戶
- 危機公關的關鍵人物

### 階段6：突現行為分析（群體現象）

```python
# 8. 分析群體層面的行為模式
emergence = sim.analyze_emergence()

print(emergence)
# {
#     "average_opinion": 67.2,          # 群體平均分數
#     "opinion_std": 18.5,              # 意見分散度
#     "polarization": 0.37,             # 極化程度（0-1）
#     "consensus": 0.63,                # 共識度（0-1）
#     "herding_strength": 12.3,         # 從眾效應強度
#     "element_preferences": {          # 五行偏好差異
#         "Fire": 72.1,
#         "Water": 58.3,
#         ...
#     }
# }
```

### 階段7：代表性評論提取

```python
# 9. 選擇具代表性的Agent生成評論
comments = sim.get_final_comments(num_comments=10)
```

**選擇策略**：
- ✅ 意見領袖優先（影響力大）
- ✅ 五行均衡（每個元素都要有代表）
- ✅ 情緒多樣（正面、中性、負面均衡）
- ✅ 意見變化顯著者（有故事性）

**輸出結構**：
```python
{
    "citizen_id": "123",
    "sentiment": "positive",
    "opinion_score": 78.5,
    "opinion_change": +15.2,      # 從63.3變成78.5 (受影響)
    "is_leader": True,            # 是意見領袖
    "influenced_count": 8,        # 影響了8個人
    "abm_context": {
        "initial_opinion": 63.3,
        "final_opinion": 78.5,
        "neighbors_avg": 75.0     # 鄰居平均分數
    }
}
```

---

## 🔗 整合到現有系統

### 修改 `line_bot_service.py`

#### 原本的流程（AI角色扮演）：

```python
async def run_simulation_with_image_data(self, image_data, sim_id, text_context):
    # 1. 抽樣市民
    sampled_citizens = await run_in_threadpool(get_random_citizens, sample_size=30)
    
    # 2. 把市民資料塞給AI
    citizens_json = json.dumps(sampled_citizens)
    prompt = f"你是這些市民，請寫評論：{citizens_json}"
    
    # 3. AI一次性生成所有評論
    ai_response = await self._call_gemini_rest(prompt, image_parts)
```

#### 新流程（ABM模擬 + AI生成）：

```python
async def run_simulation_with_image_data(self, image_data, sim_id, text_context):
    # 1. 抽樣市民
    sampled_citizens = await run_in_threadpool(get_random_citizens, sample_size=30)
    
    # 2. 【NEW】執行ABM模擬
    from app.core.abm_engine import ABMSimulation, infer_product_element
    
    # 2.1 先用AI判斷產品五行屬性
    product_element = await self._infer_product_element_with_ai(image_data, text_context)
    
    # 2.2 解析價格資訊
    price_info = self._extract_price_from_context(text_context)
    
    product_info = {
        "element": product_element,
        "price": price_info.get("price", 100),
        "market_price": price_info.get("market_price", 100)
    }
    
    # 2.3 執行ABM模擬
    abm_sim = ABMSimulation(sampled_citizens, product_info)
    abm_sim.build_social_network("element_based")
    abm_sim.initialize_opinions()
    abm_sim.run_iterations(num_iterations=5, convergence_rate=0.3)
    abm_sim.identify_opinion_leaders(top_n=5)
    
    # 2.4 獲取ABM分析結果
    emergence_data = abm_sim.analyze_emergence()
    abm_comments = abm_sim.get_final_comments(num_comments=10)
    
    # 3. 【ENHANCED】用AI生成「有深度」的評論文字
    # 但這次AI不是「扮演」市民，而是「基於ABM結果」解讀市民行為
    prompt = f"""
    以下是ABM模擬的真實結果，請為每個市民生成符合其行為邏輯的評論：
    
    模擬概況：
    - 群體平均分數：{emergence_data['average_opinion']}
    - 從眾效應強度：{emergence_data['herding_strength']}
    
    市民行為詳情：
    {json.dumps(abm_comments, ensure_ascii=False, indent=2)}
    
    請為每個市民生成評論，需符合其：
    1. 最終意見分數 (opinion_score)
    2. 意見變化幅度 (opinion_change)：如果變化大，說明受鄰居影響
    3. 是否為意見領袖 (is_leader)：領袖的評論應更有說服力
    4. 八字格局特質
    
    輸出JSON格式：
    {{
        "comments": [
            {{"citizen_id": "123", "text": "評論內容..."}}
        ]
    }}
    """
    
    ai_response = await self._call_gemini_rest(prompt, image_parts)
    
    # 4. 合併ABM數據與AI生成的文字
    final_comments = self._merge_abm_and_ai_comments(abm_comments, ai_response)
    
    # 5. 組裝最終結果
    result = {
        "score": emergence_data['average_opinion'],
        "summary": f"...[基於ABM突現分析的總結]...",
        "comments": final_comments,
        "abm_analytics": {
            "polarization": emergence_data['polarization'],
            "consensus": emergence_data['consensus'],
            "herding_effect": emergence_data['herding_strength'],
            "element_breakdown": emergence_data['element_preferences']
        }
    }
    
    update_simulation(sim_id, "completed", result)
```

---

## 📊 實際效果對比

### 舊方法（AI角色扮演）：

```
市民A（正官格）說：「這產品符合我的正官格特質，我會買。」  ❌ 模板化
市民B（七殺格）說：「這產品符合我的七殺格特質，我會買。」  ❌ 沒有互動
市民C（正財格）說：「這產品符合我的正財格特質，我會買。」  ❌ 像機器人
```

### 新方法（ABM模擬 + AI詮釋）：

```
市民A（正官格，意見領袖）：
「作為{occupation}，我一開始對這個價格有疑慮（初始63分），但看到同行普遍認可後，
確實發現這款產品的品質值得這個價位（最終78分）。我已推薦給3位朋友。」
✅ 有意見演化過程
✅ 提到受社交影響
✅ 符合領袖身份

市民B（七殺格，被A影響）：
「老實說一開始覺得太貴（初始55分），但{市民A}用了之後極力推薦，
加上我最近運勢不錯（七殺運），就決定試試看（最終68分）。」
✅ 明確提到受誰影響
✅ 結合大運狀態
✅ 有真實決策過程

市民C（正財格，堅持己見）：
「我還是覺得CP值不高（初始45分 → 最終47分），雖然周圍朋友都說好，
但我比較看重實際效益，這價格我寧可選擇其他品牌。」
✅ 意見幾乎沒變（符合正財格務實特質）
✅ 展現獨立思考
✅ 產生意見對立（兩極化）
```

---

## 🎯 關鍵優勢總結

| 面向 | 舊方法（AI角色扮演） | 新方法（ABM融合） |
|------|-------------------|-----------------|
| **學術嚴謹性** | ❌ 不符合ABM定義 | ✅ 符合ABM學術標準 |
| **市民互動** | ❌ 無互動 | ✅ 真實社交動力學 |
| **意見演化** | ❌ 靜態 | ✅ 動態演化過程 |
| **突現行為** | ❌ 無法產生 | ✅ 可觀察從眾、極化等現象 |
| **八字整合** | ⚠️ 僅作為提示詞 | ✅ 深度整合為決策基因 |
| **可解釋性** | ❌ 黑箱 | ✅ 可追溯每個決策步驟 |
| **研究價值** | ⚠️ 工程實作 | ✅ 可發表學術論文 |

---

## 📖 延伸閱讀

### ABM經典參考

1. **Epstein, J. M. (2006)**. *Generative Social Science: Studies in Agent-Based Computational Modeling*
2. **Axelrod, R. (1997)**. *The Complexity of Cooperation: Agent-Based Models of Competition and Collaboration*

### 象徵互動論

3. **Blumer, H. (1969)**. *Symbolic Interactionism: Perspective and Method*

### 可能的學術產出

**論文方向**：
> "Integrating Traditional Chinese Bazi Theory with Agent-Based Modeling: A Novel Approach to Consumer Behavior Simulation"
> 
> 整合中國傳統八字理論與Agent-Based Modeling：消費者行為模擬的創新方法

**創新點**：
- 首次將東方命理系統與西方計算社會科學結合
- 提供文化特定的異質性建模方法
- 五行關係作為社交網絡權重的新範式

---

## 🚀 下一步建議

1. **實作整合**：修改 `line_bot_service.py` 使用ABM引擎
2. **視覺化**：在前端展示「意見演化曲線」、「社交網絡圖」
3. **A/B測試**：對比舊方法vs新方法的用戶滿意度
4. **學術發表**：撰寫論文投稿 CHI / CSCW 等頂會

---

**結論**：這不只是技術升級，而是從「工程實作」邁向「學術創新」的關鍵一步。

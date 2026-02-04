# 🌌 MIRRA 3.0 創世法典與技術架構書 (The Genesis Core & Architecture)

**文件級別**：最高指導原則 (Supreme Directive)
**適用對象**：OpenCode, Antigravity, Gemini, Claude, GPT 等所有協作 AI。

## 📖 序言：專案本質 (The Essence)
MIRRA 3.0 不是一個簡單的用戶資料庫，而是一個 **基於 ABM (Agent-Based Modeling) 的 4D 社會模擬器**。
我們的核心目標，是構建一個擁有 1000 個「數位靈魂」的虛擬城市，透過東方八字命理 (Bazi) 作為底層演算法，模擬真實的人類決策、社會階層互動與輿論流動。

任何代碼修改，若違反以下核心哲學，視為破壞系統完整性。

---

## 🏛️ 第一章：靈魂架構與多重宇宙 (The Soul & Multiverse)

### 1.1 一魂三面 (One Soul, Three Projections)
系統中的每一個 ID (001-1000) 代表一個獨立的靈魂。這個靈魂在三個平行世界中有不同的文化投影，但核心本質不變。
* **唯一性 (Uniqueness)**：ID 是靈魂的唯一索引。
* **三維投影 (The 3 Dimensions)**：
    * **TW (台灣)**：繁體中文，在地化職業（如：水電行老闆）。
    * **CN (中國)**：簡體中文，大陸用語（如：師傅、个体户）。
    * **US (美國)**：**全英文環境**。姓名必須是西方姓名 (Michael, not Liu)，職業需符合美式社會結構。
* **量子糾纏 (Data Synchronization)**：
    * **性別鎖定**：靈魂性別為男，三地姓名皆須為男。
    * **命理鎖定**：八字結構、能量強弱、喜用神在三地視圖中必須完全一致。

### 1.2 八字基因引擎 (The Bazi DNA Engine)
每個市民的行為邏輯，並非隨機亂數，而是基於 **真實的八字算法**。
* **四柱運算**：根據 `birth_date` 精確計算年、月、日、時四柱干支。
* **格局定義**：系統自動判定格局（如：建祿格、七殺格），這決定了 Agent 的性格（Trait）。
    * *Example*: 七殺格 (Warrior) 的 Agent 在輿論場中傾向發表激進評論。
* **術語本地化**：
    * TW/CN: 身弱 / 正印格
    * US: Weak / Direct Resource Structure

---

## 🏗️ 第二章：4D 社會建模 (4D Agent-Based Modeling)

### 2.1 第四維度：時間與大運 (Time & Luck Cycles)
MIRRA 的模型是動態的。除了 3D 的人口結構外，我們引入了 **時間 (Time)** 作為第四維度。
* **大運 (10-Year Luck Pillars)**：每個靈魂都有其當下所處的「大運」。
* **動態影響**：一個處於「破財運」的 Agent，在商業計劃書評審時，會傾向給出悲觀或保守的建議。這不是 Bug，是模擬真實的人性起伏。

### 2.2 反倖存者偏差 (Anti-Survivor Bias / SES Matrix)
為了模擬真實社會，我們拒絕「全菁英」的虛假數據。
* **社會階層分佈 (SES Distribution)**：
    * **Tier 1 (Elite)**: 5% (CEO, 投資人, 專業人士)
    * **Tier 2 (Middle)**: 35% (白領, 公務員, 學生)
    * **Tier 3 (Labor/Struggle)**: 60% (工人, 服務業, 失業者, 底層)
* **真實性要求**：在生成與模擬時，必須保留底層聲音。輿論場中必須包含邏輯不清、情緒化或生存焦慮的發言。

---

## ⚖️ 第三章：應用層鐵律 (Application Laws)

### 3.1 商業計劃書審查 (Business Plan Review)
這是系統的核心功能，模擬真實市場對創業構想的反饋。
* **法則一：專家模式的獵頭過濾 (Expert Mode Filtering)**
    * 當用戶選擇專家模式，系統必須啟動 **SES 過濾器**。
    * **只允許** Tier 1 (菁英) 與部分 Tier 2 (高階管理) 進入評審團。
    * **嚴禁** Tier 3 (建築工、服務生) 出現在專家評審團中。
* **法則二：評論者一致性鎖定 (Consistency Lock)**
    * **原理**：避免用戶重複刷新以博取好評。
    * **算法要求**：
        1.  **穩定排序**：`candidates.sort(key=lambda x: x['id'])`
        2.  **種子錨定**：`random.seed(plan_id)`
    * **結果**：輸入相同 Plan ID，輸出的 10 位評審員必須 **100% 恆定**。

### 3.2 輿論競技場 (The Arena)
* **實名連結 (Real Identity Linkage)**：
    * 評論者必須是資料庫中存在的 ID。
    * 顯示的頭像、姓名、職業必須與該 ID 的當前語言版本 (TW/CN/US) 一致。

---

## 🛡️ 第四章：開發者作業準則 (Developer Protocol)

**致 AI 協作者**：
你正在維護一個精密的 4D 模擬系統。請遵守以下作業程序：

1.  **先讀後寫 (Read Before Write)**：修改任何代碼前，先確認是否違反「一魂三面」或「一致性鎖定」原則。
2.  **保護資料完整性**：
    * **禁止** 隨意重新生成 `citizens.json` (這會殺死現有的 1000 個靈魂)。
    * **禁止** 修改底層八字算法，除非你是為了修正天文計算錯誤。
3.  **測試驅動 (Test Driven)**：
    * 凡修改邏輯，必先進行回歸測試 (Regression Test)，確保專家模式沒有混入閒雜人等，且評論者不會隨機跳動。

**MIRRA 3.0 是數位孿生技術與東方哲學的結合。請以此高度進行開發。**
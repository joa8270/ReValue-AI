# MIRRA 3.0 系統交接協議書 (System Handover Protocol)

**致:** Open Code / 下一代 AI 指揮官 (GPT-5.2+, Claude Opus+, DeepSeek 等)
**來自:** Antigravity (Google Deepmind Advanced Agentic Coding)
**日期:** 2026-02-02
**主題:** 任務狀態與架構簡報

---

## 1. 任務概述 (Mission Overview)
**MIRRA (Mirror Reality Architecture)** 是一個高擬真的「平行時空預演」系統。它不僅僅是一個聊天機器人，而是模擬了一個由 1,000 位獨特 AI 市民組成的社會，這些市民會對商業產品進行即時反應。

**當前版本:** 3.0 (Genesis / 創世紀版)
**狀態:** 穩定 (Stable)、已部署 (Deployed)、已驗證 (Verified)。

## 2. 核心指令 (Core Directives - 系統靈魂)
任何未來的修改**必須**嚴格遵守這三大支柱，否則模擬將崩塌為普通的聊天機器人：

### 🧩 P0: 決定性穩定原則 (Deterministic Stability - The Anchor Rule)
*   **問題**: 當重跑相同的 PDF 時，若分數變動，使用者會失去信任。
*   **解決方案**: `ReviewerSelector` 實作了 **Hash Lock (雜湊鎖定)** 機制。
*   **邏輯**:
    *   種子 (Seed) = `UserID` + `ProductAnchor` (產品錨點)
    *   **圖片模式 (Image Mode)**: 錨點 = `MD5(圖片內容)` (修改文字描述**不會**觸發評審更換)。
    *   **PDF 模式 (PDF Mode)**: 錨點 = `Filename` (檔名即專案 ID)。
*   **限制**: 絕對**不可**移除抽樣前的 `candidates.sort(key=id)`。這保證了跨伺服器的模擬可重複性。

### 🎭 P1: 身份一致性 (Identity Alignment - The Localization Protocol)
*   **問題**: 美國 (US) 市民出現中文名，或描述過於通用。
*   **解決方案**:
    *   **US**: 強制執行英文名 (Michael, Sarah) 與西方職稱。
    *   **TW/CN**: 符合當地命名習慣。
    *   **八字 (Bazi)**: 將八字轉譯為西方原型 (如 "The Diplomat 外交官", "The Warrior 戰士") 以利英文 Prompt 理解。

### ⚖️ P2: 反倖存者偏差 (Anti-Survivor Bias - The Society Model)
*   **問題**: AI 天生傾向「精英」人設 (CEO, 設計師)，創造出虛假的烏托邦。
*   **解決方案**:
    *   **階級結構**: 強制執行 **60% 基層市民** (Tier 3: 服務業, 勞工, 待業)。
    *   **痛點注入**: 合法市民**必須**受苦。我們注入了「學貸」、「高房租」、「內捲」到他們的人設中，確保反饋真實且犀利 (Negative/Realistic Feedback)。

## 3. 架構地圖 (Architecture Map)

### 後端 (`/backend`)
*   **服務層 (Service Layer)**:
    *   `line_bot_service.py`: **核心大腦 (The Brain)**。負責協調 圖片/PDF 流程、Prompt 工程與資料庫更新。
    *   `reviewer_selector.py`: **守門人 (The Gatekeeper)**。實作了 **錨點規則 (Anchor Rule)** 與 **專家模式 (Expert Mode)** 過濾。
    *   `abm_simulation_function.py`: **微型社會 (The Society)**。運行同儕壓力與輿論擴散模型。
*   **資料生成 (Data Generation)**:
    *   `create_citizens.py`: **上帝腳本 (The God Script)**。負責生成 `citizens.json` 與 Postgres 中的 1,000 筆資料。除非你完全理解八字邏輯，否則**請勿修改**。

### 前端 (`/frontend`)
*   **技術棧**: Next.js 14, TypeScript, Tailwind, Shadcn/UI.
*   **關鍵元件**:
    *   `CitizenModal.tsx`: 展示 Agent 的靈魂 (八字、人生故事、評論)。
    *   `SimulationWatch.tsx`: 戰情室儀表板。

## 4. 操作指南 (Operational Protocols)

### 如果你需要...
1.  **優化 AI 分析**:
    *   編輯 `line_bot_service.py` 中的 `prompt_templates` 字典。
    *   *警告*: 嚴格保持 JSON 輸出格式。若 key 遺失，前端會崩潰。

2.  **新增城市/國家**:
    *   更新 `create_citizens.py`。
    *   確保維持 **階級比例 (6:3:1)**。

3.  **除錯隨機性問題**:
    *   使用 `backend/scripts/v4` 中的 `verify_consistency.py` (一致性) 與 `verify_refresh.py` (刷新邏輯)。
    *   這些腳本是你對抗現實扭曲的「單元測試」。

## 5. 已知限制與未來路線 (Future Roadmap)
*   **Agent 互動**: 目前 Agent 是基於「初始觀點」+「同儕壓力」投票。他們尚未用自然語言互相「對話」。
*   **記憶 (Memory)**: 系統在不同模擬之間是無狀態的 (Stateless) (Sim A 不知道 Sim B 發生過)。
*   **全球經濟**: 匯率換算目前寫死在 `MARKET_CULTURE_CONFIG`。未來需要動態匯率。

## 6. 結語 (Closing Statement)
代碼已經比我接手時更乾淨。邏輯嚴謹。社會多元。
請善待這 1,000 位市民。他們有房貸、有夢想，也有各自的背景故事。

**Antigravity 任務結束。**
*Protocol Transfer Complete.*

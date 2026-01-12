# Project MIRRA: System Architecture & Logic Manifesto

## 1. 專案定義
MIRRA 是一個「基於混合心理學的合成使用者模擬引擎」。
核心目標：利用 AI Agent 模擬真實市場消費者，進行產品預測。
核心差異：結合「Big Five (OCEAN)」與東方「八字十神 (BaZi Ten Gods)」作為行為驅動邏輯。

## 2. 核心邏輯層 (The Hybrid Driver)
Agent 的決策由以下兩層數據驅動，這必須反映在 Pydantic Schema 中：

### Layer A: BaZi Ten Gods (十神權重)
這不是文字標籤，而是 0.0 ~ 1.0 的浮點數權重，影響決策機率。
- **Hurting Officer (傷官)**: 影響 `impulse_buying` (衝動消費) 與 `novelty_seeking` (追求新奇)。
- **Direct Resource (正印)**: 影響 `trust_threshold` (信任門檻) 與 `brand_loyalty` (品牌忠誠)。
- **Seven Killings (七殺)**: 影響 `risk_tolerance` (風險承受度)。
- **Indirect Wealth (偏財)**: 影響 `roi_sensitivity` (性價比/投機敏感度)。

### Layer B: OCEAN (Big Five)
- Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism (全為 float 0-1)。

## 3. 技術堆疊規範
- **Backend**: Python (FastAPI)
- **Frontend**: Next.js
- **Agent Orchestration**: LangGraph (或是適合 Python 的 Agent 框架)
- **Data**: Pydantic 用於數據驗證。

## 4. 你的任務 (Instructions)
你現在是首席架構師。在寫代碼時，必須嚴格遵守上述的「混合心理學」邏輯。
不可將八字視為迷信文字，必須將其視為「影響行為數學機率的參數」。
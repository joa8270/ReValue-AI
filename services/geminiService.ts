import { UnifiedSpecs, ValuationResult, GroundingSource } from "../types";

export const analyzeHardwareScreenshot = async (images: string[]): Promise<Partial<UnifiedSpecs>> => {
  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ images }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || response.statusText);
    }

    return await response.json();
  } catch (error: any) {
    throw handleFrontendError(error);
  }
};

export const getRealMarketValuation = async (specs: UnifiedSpecs): Promise<Partial<ValuationResult>> => {
  try {
    const response = await fetch('/api/valuation', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ specs }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || response.statusText);
    }

    const data = await response.json();
    return {
      scrapPrice: (data.marketLow || 500) * 0.4,
      potentialPrice: data.marketHigh || 0,
      finalOffer: data.marketLow || 0,
      marketAnalysis: data.analysis || "Market analysis unavailable",
      sources: []
    };
  } catch (error: any) {
    throw handleFrontendError(error);
  }
};

export const generateAIAdvice = async (specs: UnifiedSpecs, valuation?: Partial<ValuationResult>): Promise<string> => {
  try {
    const response = await fetch('/api/advice', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ specs }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || response.statusText);
    }

    const data = await response.json();
    return data.advice || "AI 暫時無法回應，請稍後再試。";
  } catch (error: any) {
    const err = handleFrontendError(error);
    return err.message || "AI 暫時無法回應，請稍後再試。";
  }
};

const handleFrontendError = (error: any) => {
  const msg = error.message || error.toString();
  if (msg.includes('429')) {
    return new Error("AI 模型使用量已達上限 (429)，請稍待一分鐘後再試。");
  }
  if (msg.includes('404')) {
    return new Error("找不到指定的 AI 模型 (404)，請檢查 API Key 或模型設定。");
  }
  if (msg.includes('500')) {
    return new Error("伺服器連線錯誤 (500)，請檢查後端 API 設定。");
  }
  return new Error(msg);
};

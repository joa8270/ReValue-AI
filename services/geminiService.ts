
// @google/genai Coding Guidelines followed
import { GoogleGenAI } from "@google/genai";
import { HardwareSpecs, ValuationResult, GroundingSource } from "../types";

export const analyzeHardwareScreenshot = async (images: string[]): Promise<Partial<HardwareSpecs & { searchKeywords: string }>> => {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  
  const prompt = `你是一個專業硬體鑑定師。我提供了 ${images.length} 張系統資訊截圖。
請分析所有圖片，從中提取出精確的硬體規格與「產品型號」。如果資訊分散在不同圖片中，請將其整合。

請回傳一個 JSON 物件，包含以下欄位：
1. modelName: 產品型號/名稱
2. cpu: 中央處理器型號
3. ram: 記憶體容量
4. gpu: 圖形處理器型號
5. storageCapacity: 儲存容量
6. storageType: 回傳 "ssd" 或 "hdd"
7. searchKeywords: 專門給電商平台搜尋用的純淨關鍵字，例如 "i7-10700K RTX 3080"。
不要包含任何 Markdown 標籤，只回傳 JSON。`;

  try {
    const imageParts = images.map(base64 => ({
      inlineData: {
        mimeType: "image/jpeg",
        data: base64.split(',')[1]
      }
    }));

    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: {
        parts: [
          { text: prompt },
          ...imageParts
        ]
      },
      config: {
        responseMimeType: "application/json"
      }
    });

    return JSON.parse(response.text || '{}');
  } catch (error) {
    console.error("Vision Analysis Error:", error);
    throw error;
  }
};

export const getRealMarketValuation = async (specs: HardwareSpecs): Promise<Partial<ValuationResult>> => {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  
  const prompt = `你是一位專業的二手電子產品估價師。請針對以下設備進行市場調查：
設備名稱：${specs.modelName}
主要規格：${specs.cpu} / ${specs.gpu} / ${specs.ram}

請回傳一個 JSON 格式的估價結果 (單位 TWD)：
1. marketLow: 市場最低成交價
2. marketHigh: 市場最高成交價
3. analysis: 市場行情分析
不要包含任何 Markdown 標籤，只回傳 JSON。`;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-flash-preview',
      contents: prompt,
      config: {
        tools: [{ googleSearch: {} }],
        responseMimeType: "application/json"
      }
    });

    const data = JSON.parse(response.text || '{}');
    const sources: GroundingSource[] = response.candidates?.[0]?.groundingMetadata?.groundingChunks?.map((chunk: any) => ({
      title: chunk.web?.title || '參考來源',
      uri: chunk.web?.uri || '#'
    })).filter((s: any) => s.uri !== '#' && s.uri.startsWith('http')) || [];

    return {
      scrapPrice: data.marketLow * 0.4,
      potentialPrice: data.marketHigh,
      finalOffer: data.marketLow,
      marketAnalysis: data.analysis,
      sources: sources
    };
  } catch (error) {
    console.error("Valuation Error:", error);
    throw error;
  }
};

export const generateAIAdvice = async (specs: HardwareSpecs, valuation?: Partial<ValuationResult>): Promise<string> => {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  
  const systemPrompt = `針對這台 ${specs.modelName} 提供二手市場分析與高價轉售策略。`;

  const response = await ai.models.generateContent({
    model: 'gemini-3-flash-preview',
    contents: systemPrompt,
  });

  return response.text || "無法生成 AI 內容";
};

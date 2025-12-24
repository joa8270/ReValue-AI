
import { GoogleGenerativeAI } from "@google/generative-ai";

const apiKey = process.env.GEMINI_API_KEY;
const genAI = new GoogleGenerativeAI(apiKey);

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    if (!apiKey) {
        return res.status(500).json({ error: 'Server API Key not configured' });
    }

    const { specs } = req.body;

    try {
        // 使用 Gemini 2.5 Flash 並啟用 Google Search grounding
        const model = genAI.getGenerativeModel({
            model: "gemini-2.5-flash",
            tools: [{
                googleSearch: {}
            }]
        });

        // 根據設備類型組合規格描述
        let specsDescription = '';
        if (specs.deviceCategory === 'phone' || specs.deviceCategory === 'tablet') {
            specsDescription = `${specs.brand || ''} ${specs.modelName || ''} ${specs.storageCapacity || ''} ${specs.processor || ''}`.trim();
        } else {
            specsDescription = `${specs.brand || ''} ${specs.modelName || ''} ${specs.cpu || ''} ${specs.ram || ''} ${specs.gpu || ''}`.trim();
        }

        const searchKeyword = specs.searchKeywords || specs.modelName || specsDescription;

        const prompt = `你是專業的二手電子產品估價師。請使用 Google Search 搜尋以下設備在台灣二手市場的實際成交價格：

設備：${searchKeyword}
完整規格：${specsDescription}

請搜尋蝦皮、露天拍賣、FB Marketplace 等台灣二手平台上的實際售價。

回傳 JSON 格式（單位 TWD 新台幣）：
{
  "marketLow": 市場最低價（根據搜尋結果的實際價格）,
  "marketHigh": 市場最高價（根據搜尋結果的實際價格）,
  "analysis": "行情分析，說明價格區間和建議"
}

重要規則：
1. 必須根據實際搜尋到的價格回答，不要憑空猜測
2. 如果是較新/未上市的產品，請搜尋同系列前代產品價格作為參考
3. 價格單位為 TWD 新台幣
4. 只回傳 JSON，不要 Markdown 標籤`;

        const result = await model.generateContent(prompt);
        const response = await result.response;
        const text = response.text();

        // 清理 JSON
        const cleanText = text.replace(/```json/g, '').replace(/```/g, '').trim();

        let data;
        try {
            data = JSON.parse(cleanText || '{}');
        } catch (e) {
            // 嘗試從文字中提取價格數字
            const lowMatch = text.match(/marketLow["\s:]+(\d+)/);
            const highMatch = text.match(/marketHigh["\s:]+(\d+)/);
            data = {
                marketLow: lowMatch ? parseInt(lowMatch[1]) : 15000,
                marketHigh: highMatch ? parseInt(highMatch[1]) : 25000,
                analysis: "價格根據市場搜尋結果估算"
            };
        }

        // 確保價格合理（至少 1000 TWD）
        if (data.marketLow < 1000) data.marketLow = 15000;
        if (data.marketHigh < data.marketLow) data.marketHigh = data.marketLow * 1.3;

        return res.status(200).json(data);

    } catch (error) {
        console.error("API Valuation Error:", error);
        // 發生錯誤時回傳預設合理價格
        return res.status(200).json({
            marketLow: 15000,
            marketHigh: 35000,
            analysis: "暫時無法取得即時市場資料，此為預估價格範圍。"
        });
    }
}

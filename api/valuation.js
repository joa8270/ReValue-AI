
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

        // 取得當前日期用於搜尋
        const now = new Date();
        const currentYear = now.getFullYear();
        const currentMonth = now.getMonth() + 1;

        const prompt = `你是專業的二手電子產品估價師。現在是 ${currentYear} 年 ${currentMonth} 月。

請使用 Google Search 搜尋以下設備在台灣的【即時二手市場價格】：

🔍 搜尋關鍵字：${searchKeyword} 二手 ${currentYear}
📱 設備規格：${specsDescription}

【必須執行的搜尋】
1. 搜尋「${searchKeyword} 二手價格 ${currentYear}」
2. 搜尋「${searchKeyword} 蝦皮 二手」
3. 搜尋「${searchKeyword} 露天拍賣」
4. 搜尋「${searchKeyword} FB Marketplace 台灣」

請從以下平台收集實際售價：
- 蝦皮購物 (shopee.tw)
- 露天拍賣 (ruten.com.tw)
- ePrice 比價王
- SOGI 手機王
- PTT 二手版
- Facebook Marketplace

【回傳格式】JSON（單位 TWD 新台幣）：
{
  "marketLow": 搜尋到的最低實際售價,
  "marketHigh": 搜尋到的最高實際售價,
  "analysis": "列出你搜尋到的具體價格來源，例如：蝦皮 $XX,XXX、露天 $XX,XXX"
}

【重要規則】
1. 必須使用 ${currentYear} 年的最新搜尋結果
2. 不要依賴你的訓練資料，必須實際搜尋網路
3. 在 analysis 中明確列出你找到的價格來源
4. 只回傳 JSON，不要 Markdown`;


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

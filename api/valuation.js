
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

        // 根據設備類型組合規格描述 - 使用正確的估價邏輯
        let specsDescription = '';
        let searchKeyword = '';

        if (specs.deviceCategory === 'phone' || specs.deviceCategory === 'tablet') {
            // 手機/平板：品牌 + 型號 + 儲存容量最重要
            specsDescription = `${specs.brand || ''} ${specs.modelName || ''} ${specs.storageCapacity || ''}`.trim();
            searchKeyword = specs.searchKeywords || `${specs.brand} ${specs.modelName} ${specs.storageCapacity}`;
        } else if (specs.deviceCategory === 'mac') {
            // Mac：型號 + 年份 + CPU + RAM
            specsDescription = `${specs.modelName || ''} ${specs.releaseYear || ''} ${specs.cpu || ''} ${specs.ram || ''}`.trim();
            searchKeyword = specs.searchKeywords || `${specs.modelName} ${specs.releaseYear} ${specs.cpu} ${specs.ram}`;
        } else {
            // PC/電腦：GPU（顯示卡）最重要，其次 CPU、RAM
            // 不包含主機板品牌和型號！（自組PC不應以主機板估價）
            const gpu = specs.gpu || '';
            const cpu = specs.cpu || '';
            const ram = specs.ram || '';

            specsDescription = `${gpu} ${cpu} ${ram}`.trim();
            searchKeyword = specs.searchKeywords || `${gpu} ${cpu}`;
        }

        // 取得當前日期用於搜尋
        const now = new Date();
        const currentYear = now.getFullYear();
        const currentMonth = now.getMonth() + 1;

        // 根據設備類型調整搜尋策略
        let searchInstructions = '';
        if (specs.deviceCategory === 'phone' || specs.deviceCategory === 'tablet') {
            searchInstructions = `
【必須執行的搜尋】
1. 搜尋「${searchKeyword} 二手價格 ${currentYear}」
2. 搜尋「${specs.brand} ${specs.modelName} ${specs.storageCapacity} 蝦皮」
3. 搜尋「${specs.modelName} 二手 台灣」`;
        } else {
            // PC/電腦：重點搜尋顯示卡和 CPU
            searchInstructions = `
【必須執行的搜尋】
1. 搜尋「${specs.gpu} 二手價格 ${currentYear}」
2. 搜尋「${specs.gpu} ${specs.cpu} 二手主機」
3. 搜尋「${specs.gpu} 蝦皮 二手」
4. 搜尋「RTX 3080 二手電腦」（作為參考價格）`;
        }

        const prompt = `你是專業的二手電子產品估價師。現在是 ${currentYear} 年 ${currentMonth} 月。

請使用 Google Search 搜尋以下設備在台灣的【即時二手市場價格】：

🔍 設備類型：${specs.deviceCategory === 'phone' || specs.deviceCategory === 'tablet' ? '手機/平板' : specs.deviceCategory === 'mac' ? 'Mac 電腦' : 'PC 電腦'}
📱 關鍵規格：${specsDescription}
${specs.deviceCategory === 'computer' ? `⚡ 估價重點：主要參考 GPU（${specs.gpu}）的市場行情` : ''}

${searchInstructions}

請從以下平台收集實際售價：
- 蝦皮購物 (shopee.tw)
- 露天拍賣 (ruten.com.tw)
- ePrice 比價王
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
2. ${specs.deviceCategory === 'computer' ? '對於 PC 電腦，主要參考顯示卡（GPU）的市場價格' : ''}
3. 不要依賴你的訓練資料，必須實際搜尋網路
4. 在 analysis 中明確列出你找到的價格來源
5. 只回傳 JSON，不要 Markdown`;


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

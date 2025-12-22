
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
        const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash" });
        const prompt = `你是一位專業的二手電子產品估價師。請針對以下設備進行市場調查：
設備名稱：${specs.modelName}
主要規格：${specs.cpu} / ${specs.gpu} / ${specs.ram}

請回傳一個 JSON 格式的估價結果 (單位 TWD)：
1. marketLow: 市場最低成交價
2. marketHigh: 市場最高成交價
3. analysis: 市場行情分析
不要包含任何 Markdown 標籤，只回傳 JSON。`;

        const result = await model.generateContent(prompt);
        const response = await result.response;
        const text = response.text();
        const cleanText = text.replace(/```json/g, '').replace(/```/g, '').trim();
        let data;
        try {
            data = JSON.parse(cleanText || '{}');
        } catch (e) {
            data = { marketLow: 0, marketHigh: 0, analysis: "無法解析回傳資料" };
        }

        return res.status(200).json(data);

    } catch (error) {
        console.error("API Valuation Error:", error);
        return res.status(500).json({ error: error.message });
    }
}

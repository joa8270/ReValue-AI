
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

    const { images } = req.body;

    if (!images || !Array.isArray(images) || images.length === 0) {
        return res.status(400).json({ error: 'No images provided' });
    }

    try {
        const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash" });
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

        const imageParts = images.map(base64 => ({
            inlineData: {
                mimeType: "image/jpeg",
                data: base64.split(',')[1]
            }
        }));

        const result = await model.generateContent([prompt, ...imageParts]);
        const response = await result.response;
        const text = response.text();
        const cleanText = text.replace(/```json/g, '').replace(/```/g, '').trim();
        const json = JSON.parse(cleanText || '{}');

        return res.status(200).json(json);

    } catch (error) {
        console.error("API Analyze Error:", error);
        return res.status(500).json({ error: error.message });
    }
}

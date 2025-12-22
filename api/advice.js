
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
        const systemPrompt = `針對這台 ${specs.modelName} 提供二手市場分析與高價轉售策略。`;

        const result = await model.generateContent(systemPrompt);
        const response = await result.response;
        const text = response.text();

        return res.status(200).json({ advice: text });

    } catch (error) {
        console.error("API Advice Error:", error);
        return res.status(500).json({ error: error.message });
    }
}

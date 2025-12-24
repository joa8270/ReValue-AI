
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

        const prompt = `你是一個專業硬體鑑定師。請分析截圖並識別設備資訊。

**步驟 1：判斷設備類型**
根據截圖內容判斷設備類型：
- "phone"：手機（iPhone, Samsung Galaxy, Google Pixel 等）
- "tablet"：平板（iPad, Galaxy Tab 等）
- "computer"：Windows PC / 筆電
- "mac"：MacBook / iMac / Mac mini / Mac Studio

**步驟 2：根據設備類型回傳對應欄位**

若為 phone 或 tablet，回傳以下 JSON：
{
  "deviceCategory": "phone" 或 "tablet",
  "brand": "品牌名稱（Apple/Samsung/Google/Xiaomi 等）",
  "modelName": "完整型號名稱（如 iPhone 17 Pro）",
  "releaseYear": "發布年份（如 2025）",
  "processor": "處理器型號（如 A19 Pro、Snapdragon 8 Gen 3）",
  "storageCapacity": "儲存容量（如 256GB）",
  "screenSize": "螢幕尺寸（如 6.3 吋）",
  "searchKeywords": "電商搜尋關鍵字（如 iPhone 17 Pro 256GB）"
}

若為 computer 或 mac，回傳以下 JSON：
{
  "deviceCategory": "computer" 或 "mac",
  "brand": "品牌名稱（Apple/Dell/ASUS/Lenovo 等）",
  "modelName": "完整型號名稱（如 MacBook Pro 14 吋）",
  "releaseYear": "發布年份（如 2024）",
  "cpu": "CPU 型號（如 Apple M3 Pro、Intel i7-13700K）",
  "ram": "記憶體容量（如 16GB）",
  "gpu": "GPU 型號（如 RTX 4080、Apple GPU 18-core）",
  "storageCapacity": "儲存容量（如 512GB）",
  "storageType": "ssd" 或 "hdd",
  "searchKeywords": "電商搜尋關鍵字"
}

**重要規則：**
1. 若截圖中找不到某欄位資訊，請根據你對該型號的知識填入正確規格
2. 例如：看到 "iPhone 17 Pro"，即使截圖沒顯示處理器，也應填入 "A19 Pro"
3. 不要回傳 "Not specified" 或 "未知"，盡可能填入正確資訊
4. 只回傳純 JSON，不要包含任何 Markdown 標籤`;

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

        // 確保必要欄位存在
        if (!json.deviceCategory) {
            json.deviceCategory = 'computer'; // 預設為電腦
        }

        return res.status(200).json(json);

    } catch (error) {
        console.error("API Analyze Error:", error);
        return res.status(500).json({ error: error.message });
    }
}

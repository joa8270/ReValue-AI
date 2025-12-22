import { GoogleGenerativeAI } from "@google/generative-ai";
import fs from 'fs';
import path from 'path';

// Improved .env parsing
const envPath = path.resolve(process.cwd(), '.env');
let apiKey = '';

try {
    if (fs.existsSync(envPath)) {
        const envContent = fs.readFileSync(envPath, 'utf-8');
        const match = envContent.match(/VITE_GEMINI_API_KEY=(.*)/);
        if (match) {
            apiKey = match[1].trim();
            // Remove comments or quotes if present
            apiKey = apiKey.replace(/#.*/, '').trim().replace(/^['"]|['"]$/g, '');
        }
    }
} catch (e) {
    console.error("Error reading .env:", e);
}

if (!apiKey || apiKey === 'your_api_key_here') {
    console.error("Error: VITE_GEMINI_API_KEY not found or invalid in .env");
    process.exit(1);
}

console.log(`Checking models with API Key (first 5 chars): ${apiKey.substring(0, 5)}...`);

const genAI = new GoogleGenerativeAI(apiKey);

async function listModels() {
    try {
        const candidates = [
            "gemini-2.0-flash-exp",
            "gemini-exp-1206",
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash-001",
            "gemini-1.5-flash-8b",
            "gemini-1.5-pro",
            "gemini-1.5-pro-latest",
            "gemini-1.5-pro-001",
            "gemini-1.0-pro",
            "gemini-pro",
            "gemini-pro-vision"
        ];

        console.log("Testing model availability...");

        for (const modelName of candidates) {
            try {
                const m = genAI.getGenerativeModel({ model: modelName });
                await m.generateContent("Test");
                console.log(`✅ ${modelName} is AVAILABLE`);
            } catch (err) {
                console.log(`❌ ${modelName} failed: ${err.message}`);
                if (err.response) {
                    console.log(`   Status: ${err.response.status}`);
                }
            }
        }

    } catch (error) {
        console.error("Fatal error:", error);
    }
}

listModels();

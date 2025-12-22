
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

const url = `https://generativelanguage.googleapis.com/v1beta/models?key=${apiKey}`;

console.log(`Querying ${url.replace(apiKey, 'HIDDEN_KEY')}...`);

fetch(url)
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            console.error("API Error:", data.error);
        } else if (data.models) {
            console.log("Available Models:");
            data.models.forEach(m => {
                if (m.supportedGenerationMethods.includes('generateContent')) {
                    console.log(`- ${m.name.replace('models/', '')} [${m.supportedGenerationMethods.join(', ')}]`);
                }
            });
        } else {
            console.log("No models found or unexpected response structure:", data);
        }
    })
    .catch(err => console.error("Fetch Error:", err));

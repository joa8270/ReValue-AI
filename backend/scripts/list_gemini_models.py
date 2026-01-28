import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env info
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Error: GOOGLE_API_KEY not found.")
    exit(1)

genai.configure(api_key=api_key)

print("Listing available models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f" - {m.name}")

import google.generativeai as genai
import os

os.environ["GOOGLE_API_KEY"] = "AIzaSyDTDU5szvsGVIowvvMBNAoqXyXe_RrXU7I"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

print("--- 可用的 Gemini 模型列表 ---")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"模型名稱: {m.name}")

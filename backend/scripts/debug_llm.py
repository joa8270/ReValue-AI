
import os
import sys
from dotenv import load_dotenv

# Load env
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, '.env')
print(f"Loading env from: {env_path}")
load_dotenv(env_path)

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ GOOGLE_API_KEY not found in environment!")
    sys.exit(1)
else:
    print(f"✅ GOOGLE_API_KEY found: {api_key[:5]}...")

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    print("✅ Library imported.")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        google_api_key=api_key
    )
    print("🚀 Invoking LLM...")
    res = llm.invoke("Hi")
    print(f"✅ Response: {res.content}")
except Exception as e:
    print(f"❌ LLM Invocation Failed: {e}")

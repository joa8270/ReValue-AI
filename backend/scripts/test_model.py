
import sys
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

if len(sys.argv) < 2:
    print("Usage: python test_model.py <model_name>")
    sys.exit(1)

model_name = sys.argv[1]
print(f"🧪 Testing model: {model_name}")

try:
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    res = llm.invoke("Hello")
    print(f"✅ SUCCESS! Response: {res.content}")
except Exception as e:
    print(f"❌ FAIL: {e}")

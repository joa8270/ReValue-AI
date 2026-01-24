import json
import re

# Simulate the raw Gemini response with leading whitespace
test_raw = '''{
    "simulation_metadata": {
        "product_category": "商業計劃書"
    },
    "result": {
        "score": 75,
        "summary": "Test Summary"
    }
}'''

print("=== Testing JSON Parsing ===")
print("Raw length:", len(test_raw))
print("First 50 chars:", repr(test_raw[:50]))
print("Starts with '{':", test_raw.startswith('{'))
print("After strip starts with '{':", test_raw.strip().startswith('{'))

# Test 1: Direct parse
try:
    data = json.loads(test_raw)
    print("Direct parse SUCCESS:", list(data.keys()))
except Exception as e:
    print("Direct parse FAILED:", e)

# Test 2: Strip then parse
try:
    data = json.loads(test_raw.strip())
    print("Stripped parse SUCCESS:", list(data.keys()))
except Exception as e:
    print("Stripped parse FAILED:", e)

# Test 3: Simulate _clean_and_parse_json logic
clean_text = test_raw.strip()
match = re.search(r"```(?:json)?\s*(.*?)\s*```", test_raw, re.DOTALL)
if match:
    clean_text = match.group(1).strip()
    print("Found code block, extracted")
else:
    print("No code block found")

if not clean_text.startswith('{'):
    first_brace = clean_text.find('{')
    if first_brace != -1:
        clean_text = clean_text[first_brace:]
        print("Found first brace at", first_brace)

try:
    data = json.loads(clean_text)
    print("Final parse SUCCESS:", list(data.keys()))
except Exception as e:
    print("Final parse FAILED:", e)
    print("Problematic content:", repr(clean_text[:200]))

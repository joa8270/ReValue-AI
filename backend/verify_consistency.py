
import asyncio
import json
import hashlib
from app.core.database import get_random_citizens

# Mock filters and content
filters = {"age_min": 40, "age_max": 60, "occupation": ["Executive", "Founder"]}
content_bytes = b"Sample PDF Content for Business Plan"

def calculate_seed(content, filters_dict):
    combined = content
    filter_str = json.dumps(filters_dict, sort_keys=True)
    combined += filter_str.encode('utf-8')
    h_hex = hashlib.sha256(combined).hexdigest()
    return int(h_hex, 16) % (2**32)

async def run_simulation_mock(device_name):
    seed = calculate_seed(content_bytes, filters)
    print(f"[{device_name}] Calculated Seed: {seed}")
    
    citizens = get_random_citizens(sample_size=30, seed=seed, filters=filters)
    ids = [c["id"] for c in citizens[:5]] # Check first 5
    print(f"[{device_name}] First 5 Citizen IDs: {ids}")
    return ids

async def main():
    print("--- Simulating Cross-Device Consistency ---")
    ids_a = await run_simulation_mock("Device A (PC)")
    ids_b = await run_simulation_mock("Device B (Mobile)")
    
    if ids_a == ids_b:
        print("\n✅ SUCCESS: Sampling is Deterministic!")
    else:
        print("\n❌ FAILURE: Sampling is inconsistent.")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())

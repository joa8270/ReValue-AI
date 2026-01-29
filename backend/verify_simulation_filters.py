import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.core.database import get_random_citizens

def test_filters():
    # Test Case 1: Age Filter 20-45
    print("\n--- Testing Age Filter (20-45) ---")
    citizens = get_random_citizens(sample_size=10, stratified=False, filters={"age_min": 20, "age_max": 45})
    for c in citizens:
        status = "✅" if 20 <= c["age"] <= 45 else "❌"
        print(f"{status} Age: {c['age']}")

    # Test Case 2: Occupation Filter "Marketing"
    print("\n--- Testing Occupation Filter ('Marketing') ---")
    citizens = get_random_citizens(sample_size=10, stratified=False, filters={"occupation": "Marketing"})
    for c in citizens:
        status = "✅" if "Marketing" in str(c["occupation"]) or "行銷" in str(c["occupation"]) else "❌"
        print(f"{status} Job: {c['occupation']}")

    # Test Case 3: Fire Element Check with Filters
    print("\n--- Testing Fire Element Availability with Filters ---")
    citizens = get_random_citizens(sample_size=50, stratified=True, filters={"age_min": 20, "age_max": 60})
    fire_count = sum(1 for c in citizens if c["element"] == "Fire")
    print(f"Fire Citizens: {fire_count}")

if __name__ == "__main__":
    test_filters()

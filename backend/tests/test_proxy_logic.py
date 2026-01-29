
import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import get_random_citizens

def test_scene_a_normal():
    print("\n[TEST] Scene A: Normal (20-40)")
    filters = {"age_min": 20, "age_max": 40}
    citizens = get_random_citizens(sample_size=10, filters=filters)
    
    if not citizens:
        print("❌ No citizens returned")
        return

    ages = [c["age"] for c in citizens]
    print(f"Ages: {ages}")
    
    min_a = min(ages)
    max_a = max(ages)
    
    if min_a >= 20 and max_a <= 40:
        print("✅ Age Range Correct")
    else:
        print(f"❌ Age Range Mismatch: {min_a}-{max_a}")

    if any(c.get("proxy_role") for c in citizens):
        print("❌ Proxy Role shouldn't exist")
    else:
        print("✅ Proxy Role is None")

def test_scene_b_infant():
    print("\n[TEST] Scene B: Infant (0-5) -> Proxy Parents (25-45)")
    filters = {"age_min": 0, "age_max": 5}
    citizens = get_random_citizens(sample_size=10, filters=filters)
    
    if not citizens:
        print("❌ No citizens returned")
        return

    ages = [c["age"] for c in citizens]
    roles = [c.get("proxy_role") for c in citizens]
    
    print(f"Ages: {ages}")
    print(f"Roles: {roles}")
    
    min_a = min(ages)
    max_a = max(ages)
    
    # Must be 25-45
    if min_a >= 25 and max_a <= 45:
        print("✅ Proxy Age Range Correct (25-45)")
    else:
        print(f"❌ Proxy Age Range Mismatch: {min_a}-{max_a}")
        
    if all(r == "parent" for r in roles):
        print("✅ All marked as 'parent'")
    else:
        print("❌ Role Mismatch")

def test_scene_c_elderly():
    print("\n[TEST] Scene C: Elderly (80-100) -> Mixed (50% Real + 50% Children)")
    filters = {"age_min": 80, "age_max": 100}
    citizens = get_random_citizens(sample_size=20, filters=filters)
    
    if not citizens:
        print("❌ No citizens returned")
        return

    elderly = [c for c in citizens if c["age"] >= 75]
    children = [c for c in citizens if 40 <= c["age"] <= 60]
    
    print(f"Total: {len(citizens)}")
    print(f"Elderly Count: {len(elderly)} (Role: {elderly[0].get('proxy_role') if elderly else 'None'})")
    print(f"Children Count: {len(children)} (Role: {children[0].get('proxy_role') if children else 'None'})")
    
    if len(citizens) == 20: 
        # Expect roughly 10/10 if stratification doesn't mess it up too much
        print("✅ Sample Size OK")
        
    if elderly and children:
        print("✅ Mixed Group Successful")
        if elderly[0].get("proxy_role") == "elderly_self" and children[0].get("proxy_role") == "elderly_caregiver":
            print("✅ Roles Correct")
        else:
            print("❌ Roles incorrect")


if __name__ == "__main__":
    test_scene_a_normal()
    test_scene_b_infant()
    test_scene_c_elderly()

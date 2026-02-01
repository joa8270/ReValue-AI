
import sys
import os
import random

# Setup Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # backend/
sys.path.append(BASE_DIR)

from app.services.reviewer_selector import select_reviewers

def test_refresh_logic():
    print("🧪 Starting Refresh Logic Verification...")
    
    # 1. Prepare Mock Candidates (Simulate DB Query Result)
    # Pool should be large enough to allow finding different people upon refresh
    mock_candidates = []
    
    # Expert keywords: 'CEO', 'Director', 'Manager', 'Professor'
    # Regular keywords: 'Worker', 'Student', 'Clerk'
    
    for i in range(200): # 200 candidates
        is_expert = i % 2 == 0 # 50% experts for testing
        role = "CEO" if is_expert else "Worker"
        if i % 4 == 0: role = "Director"
        if i % 6 == 0: role = "Professor"
        
        mock_candidates.append({
            "id": str(i),
            "name": f"Citizen {i}",
            "occupation": role,
            "age": random.randint(40, 60), # Simulate Age Filter 40-60 applied upstream
            "social_tier": 1 if is_expert else 3
        })
        
    plan_content = "Project Refresh Test_User123" # Simulating UserID + Anchor
    
    # Step 1: Baseline (Refresh = False)
    print("\n   [Step 1] Baseline Selection (Refresh=False)")
    list_a = select_reviewers(mock_candidates, plan_content, mode="Expert", refresh_flag=False)
    ids_a = [c['id'] for c in list_a]
    names_a = [c['name'] for c in list_a][:2]
    print(f"   >>> List A (Top 2): {names_a}")
    print(f"   >>> IDs: {ids_a}")
    
    # Verify List A Quality
    non_experts_a = [c for c in list_a if c['occupation'] == "Worker"]
    if non_experts_a:
        print(f"   ❌ FAIL: Baseline List contains non-experts! {non_experts_a}")
        sys.exit(1)

    # Step 2: Refresh (Refresh = True)
    print("\n   [Step 2] Refresh Selection (Refresh=True)")
    list_b = select_reviewers(mock_candidates, plan_content, mode="Expert", refresh_flag=True)
    ids_b = [c['id'] for c in list_b]
    names_b = [c['name'] for c in list_b][:2]
    print(f"   >>> List B (Top 2): {names_b}")
    print(f"   >>> IDs: {ids_b}")

    # Verify List B Quality
    non_experts_b = [c for c in list_b if c['occupation'] == "Worker"]
    if non_experts_b:
        print(f"   ❌ FAIL: Refreshed List contains non-experts! {non_experts_b}")
        sys.exit(1)

    # Assertions
    print("\n   [Assertions]")
    
    # 1. Variance Check
    if ids_a != ids_b:
        print("   ✅ PASS: Lists are different.")
    else:
        print("   ❌ FAIL: Lists are identical despite refresh=True!")
        print("   Did you forget to add randomness in refresh branch?")
        sys.exit(1)
        
    # 2. Consistency Check (Expert Only)
    # Already checked above, but mainly ensuring we didn't break filters
    print("   ✅ PASS: Expert criteria maintained in both lists.")
    
    print("\n🎉 [PASS] Refresh successfully changed reviewers.")

if __name__ == "__main__":
    test_refresh_logic()

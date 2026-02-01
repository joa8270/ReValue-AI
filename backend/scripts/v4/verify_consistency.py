
import sys
import os
import json

# Setup Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # backend/
sys.path.append(BASE_DIR)

from app.services.reviewer_selector import select_reviewers

def test_consistency():
    print("🧪 Starting Consistency Test...")
    
    # Mock Candidates
    mock_candidates = []
    for i in range(100):
        mock_candidates.append({
            "id": str(i),
            "name": f"Citizen {i}",
            "occupation": "CEO" if i % 5 == 0 else "Worker", # 20 Experts
            "social_tier": 1 if i % 5 == 0 else 3
        })
        
    plan_id = "test_plan_abc"
    
    # Test 1: Consistency (Normal)
    print("   [1] Testing Normal Mode Consistency...")
    r1 = select_reviewers(mock_candidates, plan_id, "Normal", target_count=10)
    r2 = select_reviewers(mock_candidates, plan_id, "Normal", target_count=10)
    
    ids1 = [c['id'] for c in r1]
    ids2 = [c['id'] for c in r2]
    
    if ids1 == ids2:
        print("   ✅ Normal Mode: PASS (Identical results)")
    else:
        print(f"   ❌ Normal Mode: FAIL (Diff: {ids1} vs {ids2})")
        sys.exit(1)

    # Test 2: Consistency (Expert)
    print("   [2] Testing Expert Mode Consistency...")
    e1 = select_reviewers(mock_candidates, plan_id, "Expert", target_count=10)
    e2 = select_reviewers(mock_candidates, plan_id, "Expert", target_count=10)
    
    ids_e1 = [c['id'] for c in e1]
    ids_e2 = [c['id'] for c in e2]
    
    if ids_e1 == ids_e2:
        print("   ✅ Expert Mode: PASS (Identical results)")
    else:
        print(f"   ❌ Expert Mode: FAIL")
        sys.exit(1)
        
    # Test 3: Expert Quality
    print("   [3] Testing Expert Quality...")
    for c in e1:
        if c['occupation'] != "CEO":
            print(f"   ❌ Expert Quality: FAIL (Found {c['occupation']})")
            sys.exit(1)
    print("   ✅ Expert Quality: PASS")

    print("   ✅ Expert Quality: PASS")

    # Test 4: Anchor Rule (Iteration Consistency)
    print("   [4] Testing Anchor Rule...")
    user_id = "user_123"
    anchor_1 = "Project Alpha"
    anchor_2 = "Project Beta"
    
    # Simulate content string generation: UserID + Anchor
    seed_str_1 = f"{user_id}_{anchor_1}"
    seed_str_1_same = f"{user_id}_{anchor_1}"
    seed_str_2 = f"{user_id}_{anchor_2}"
    seed_str_3_diff_user = f"user_999_{anchor_1}"

    # 4a. Same Anchor -> Same Result
    res_1 = select_reviewers(mock_candidates, seed_str_1, "Normal")
    res_1_same = select_reviewers(mock_candidates, seed_str_1_same, "Normal")
    if [c['id'] for c in res_1] == [c['id'] for c in res_1_same]:
         print("   ✅ Same Anchor: PASS")
    else:
         print("   ❌ Same Anchor: FAIL")
         sys.exit(1)

    # 4b. Different Anchor -> Different Result (High Prob)
    res_2 = select_reviewers(mock_candidates, seed_str_2, "Normal")
    if [c['id'] for c in res_1] != [c['id'] for c in res_2]:
         print("   ✅ Diff Anchor: PASS")
    else:
         print("   ⚠️ Diff Anchor: WARNING (Collision or Bug)") 

    # 4c. Diff User -> Diff Result
    res_3 = select_reviewers(mock_candidates, seed_str_3_diff_user, "Normal")
    if [c['id'] for c in res_1] != [c['id'] for c in res_3]:
         print("   ✅ Diff User: PASS")
    else:
         print("   ⚠️ Diff User: WARNING")

    print("🎉 All Tests Passed!")

if __name__ == "__main__":
    test_consistency()

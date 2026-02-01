
import sys
import os
import hashlib
import random
import time

# Setup Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # backend/
sys.path.append(BASE_DIR)

from app.services.reviewer_selector import select_reviewers

# Mock function simulating the logic in line_bot_service.py
def get_consistent_seed(user_id, anchor_content):
    """
    User ID + Anchor Content -> Stable Seed
    """
    stable_seed_str = f"{user_id}_{anchor_content}"
    return stable_seed_str

def test_iteration_consistency():
    print("🧪 Starting Iteration Consistency Test (Self-Healing Protocol)...")
    
    # Mock Candidates
    mock_candidates = []
    for i in range(100):
        mock_candidates.append({
            "id": str(i),
            "name": f"Citizen {i}",
            "occupation": "CEO" if i % 5 == 0 else "Worker",
            "social_tier": 1 if i % 5 == 0 else 3
        })
        
    user_id = "user_commander"
    
    # Scenario A: Base Case
    # Title: "AI Coffee", Text: "Version 1"
    # Anchor (Image Flow): md5("coffee_img_bytes")
    # Anchor (PDF Flow): "AI_Coffee.pdf"
    
    # Let's simulate Image Flow logic first
    anchor_A = "hash_of_coffee_image_v1" 
    seed_A = get_consistent_seed(user_id, anchor_A)
    
    print("\n   [Scenario A] Base Case (Anchor='AI Coffee Image')")
    list_A = select_reviewers(mock_candidates, seed_A, "Normal")
    ids_A = [c['id'] for c in list_A]
    print(f"   >>> Reviewers A: {ids_A}")

    # Scenario B: Iteration Case
    # Title: "AI Coffee", Text: "Version 2 (Modified)"
    # Anchor: SAME (Image didn't change, or Filename didn't change)
    anchor_B = "hash_of_coffee_image_v1" # Same anchor
    seed_B = get_consistent_seed(user_id, anchor_B)
    
    print("\n   [Scenario B] Iteration Case (Same Anchor, Modified Text)")
    # Note: Text change is IGNORED by seed generation in current logic
    list_B = select_reviewers(mock_candidates, seed_B, "Normal")
    ids_B = [c['id'] for c in list_B]
    print(f"   >>> Reviewers B: {ids_B}")
    
    # Assert A == B
    if ids_A == ids_B:
        print("   ✅ PASS: Iteration maintained same reviewers.")
    else:
        print("   ❌ FAIL: Reviewers changed despite same anchor!")
        sys.exit(1)

    # Scenario C: New Product Case
    # Uploading "AI Tea" -> Different Image/File
    anchor_C = "hash_of_tea_image"
    seed_C = get_consistent_seed(user_id, anchor_C)
    
    print("\n   [Scenario C] New Product Case (Diff Anchor)")
    list_C = select_reviewers(mock_candidates, seed_C, "Normal")
    ids_C = [c['id'] for c in list_C]
    print(f"   >>> Reviewers C: {ids_C}")
    
    # Assert A != C
    if ids_A != ids_C:
        print("   ✅ PASS: New product got different reviewers.")
    else:
        print("   ⚠️ WARNING: Collision (Rare but possible) or Bug.")
        # Unlikely with MD5 but technically possible to collide in small pool sample? 
        # With 1000 candidates and random, very unlikely to get exact same 10.
        
    if ids_A != ids_C and ids_A == ids_B:
        print("\n🎉 [SUCCESS] Iteration Logic Verified.")
        print("   Rule: Seed = UserID + Anchor(ContentHash/Filename)")
    else:
        print("\n❌ [FAIL] Logic check failed.")
        sys.exit(1)

if __name__ == "__main__":
    test_iteration_consistency()

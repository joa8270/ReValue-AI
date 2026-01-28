from app.core.database import get_random_citizens
from collections import Counter
import sys

def verify_consistency():
    print("🧪 Verifying Simulation Consistency & Diversity...")
    
    # Test 1: Consistency (Same Seed)
    seed_a = 12345
    print(f"\n[Test 1] Fetching citizens with Seed={seed_a} (Run 1)...")
    sample_1 = get_random_citizens(sample_size=30, seed=seed_a)
    ids_1 = [c["id"] for c in sample_1]
    
    print(f"[Test 1] Fetching citizens with Seed={seed_a} (Run 2)...")
    sample_2 = get_random_citizens(sample_size=30, seed=seed_a)
    ids_2 = [c["id"] for c in sample_2]
    
    if ids_1 == ids_2:
        print("✅ [Pass] Consistency Check: Samples are identical.")
    else:
        print("❌ [Fail] Consistency Check: Samples differ despite same seed!")
        sys.exit(1)
        
    # Test 2: Diversity (Element Check)
    print(f"\n[Test 2] Checking Element Diversity in Sample 1...")
    elements = [c["element"] for c in sample_1]
    counts = Counter(elements)
    print(f"   Distribution: {dict(counts)}")
    
    if len(counts) >= 5 and all(count > 0 for count in counts.values()):
         print("✅ [Pass] Diversity Check: All 5 elements present.")
    else:
         print(f"⚠️ [Warning] Diversity Check: Only {len(counts)} elements found (Expected 5).")
         # Not strictly a fail if sample size is small, but with 30 it should be diverse
         
    # Test 3: Randomness (Different Seed)
    seed_b = 67890
    print(f"\n[Test 3] Fetching citizens with Seed={seed_b}...")
    sample_3 = get_random_citizens(sample_size=30, seed=seed_b)
    ids_3 = [c["id"] for c in sample_3]
    
    if ids_1 != ids_3:
        print("✅ [Pass] Randomness Check: Different seed produced different sample.")
    else:
        print("❌ [Fail] Randomness Check: Different seed produced IDENTICAL sample!")
        
    print("\n🎉 Verification Complete!")

if __name__ == "__main__":
    verify_consistency()

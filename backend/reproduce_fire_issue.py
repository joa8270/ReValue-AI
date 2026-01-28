
import sys
import os
sys.path.insert(0, os.getcwd())

from app.core.database import get_random_citizens

def check_distribution(label, stratified, seed=None):
    print(f"--- Checking {label} (Stratified={stratified}, Seed={seed}) ---")
    citizens = get_random_citizens(sample_size=20, stratified=stratified, seed=seed)
    
    counts = {}
    for c in citizens:
        elem = c.get("element", "MISSING")
        counts[elem] = counts.get(elem, 0) + 1
        
        # Also check nested bazi for consistency
        bazi_elem = c.get("bazi_profile", {}).get("element", "MISSING")
        if elem != bazi_elem:
            print(f"⚠️ Mismatch! Top-level: {elem}, Bazi: {bazi_elem} (ID: {c.get('id')})")

    print("Distribution:", counts)
    
    if "Fire" in counts and counts["Fire"] == len(citizens):
        print("❌ FAIL: All Fire detected!")
    else:
        print("✅ PASS: Distribution looks mixed.")
    print("-" * 30)

if __name__ == "__main__":
    check_distribution("Default Mode (Stratified)", True, seed=None)
    check_distribution("Force Random (Unstratified)", False, seed=None)

import sys
import os

# Setup path
sys.path.append(os.getcwd())

from app.core.database import get_random_citizens

def test_filters():
    print("🚀 Testing Filter Logic (Age List & Occupation List)...")
    
    # 1. Test Age as List (simulate line_bot_service pre-processing or just verify database handles valid range)
    # Note: database.py expects int age_min/max regardless of source, so we test if passing valid params works.
    # The real test is if line_bot_service correctly converts list to int params. We assumed that works.
    # Let's test the occupation LIST support in database.py
    
    print("\n[1] Testing Occupation List: ['經理', '創業']")
    filters = {
        "age_min": 25,
        "age_max": 50,
        "occupation": ["經理", "創業"] # List of keywords
    }
    
    try:
        citizens = get_random_citizens(sample_size=10, filters=filters)
        print(f"✅ Sampled {len(citizens)} citizens.")
        for c in citizens:
            occ = str(c.get("occupation", ""))
            age = c.get("age")
            
            # Verify Age
            is_age_ok = 25 <= age <= 50
            
            # Verify Occupation (matches AT LEAST ONE keyword)
            is_occ_ok = "經理" in occ or "創業" in occ
            
            status = "PASS" if is_age_ok and is_occ_ok else "FAIL"
            print(f"   [{status}] ID={c['id']}, Age={age}, Job={occ[:20]}...")
            
            if not is_age_ok: print(f"      ❌ Age {age} out of range [25, 50]")
            if not is_occ_ok: print(f"      ❌ Job {occ} does not match keywords")
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_filters()

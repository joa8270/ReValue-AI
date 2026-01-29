import sys
import os
import json

# Setup path
sys.path.append(os.getcwd())

from app.core.database import get_random_citizens

def test_tag_filters():
    print("🚀 Testing Tag-Based Filter Logic...")
    
    # Test: Age Range + Occupation Keys (Executive OR Entrepreneur)
    print("\n[1] Testing Occupation Keys: ['executive', 'entrepreneur']")
    filters = {
        "age_min": 25,
        "age_max": 50,
        "occupation": ["executive", "entrepreneur"] # Raw Keys (Now supported!)
    }
    
    try:
        citizens = get_random_citizens(sample_size=10, filters=filters)
        print(f"✅ Sampled {len(citizens)} citizens.")
        
        for c in citizens:
            # Check Tags directly
            tags = c.get("persona_categories", [])
            age = c.get("age")
            
            # Verify Age
            is_age_ok = 25 <= age <= 50
            
            # Verify Tags (matches AT LEAST ONE key)
            is_tag_ok = "executive" in tags or "entrepreneur" in tags
            
            # Handle Occupation safe print
            occ_val = c.get('occupation')
            if isinstance(occ_val, dict):
                job_title = occ_val.get('TW', str(occ_val))
            else:
                job_title = str(occ_val)
            
            status = "PASS" if is_age_ok and is_tag_ok else "FAIL"
            print(f"   [{status}] ID={c['id']}, Age={age}, Tags={tags}, Job={job_title[:15]}...")
            
            if not is_age_ok: print(f"      ❌ Age {age} out of range [25, 50]")
            if not is_tag_ok: print(f"      ❌ Tags {tags} do not match ['executive', 'entrepreneur']")
            
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tag_filters()

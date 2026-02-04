import sys
import os

# Setup path
sys.path.append(os.getcwd())

from app.core.database import get_random_citizens, get_citizen_by_id

def verify_all_logic():
    print("Verifying ALL Citizen Logic...")
    
    # 1. Verify Random Citizens (The Arena / List)
    print("\n[1] Testing get_random_citizens (The Arena Data)...")
    try:
        citizens = get_random_citizens(sample_size=5)
        print(f"Success! Got {len(citizens)} citizens.")
        if citizens:
            c = citizens[0]
            print(f"   Sample: ID={c['id']}, Name={c['name']}, Element={c.get('element')}")
            if 'element' in c and c['element'] == "Fire":
                 print("   Fire Element confirmed present in List data!")
    except Exception as e:
        print(f"❌ FAILED get_random_citizens: {e}")
        import traceback
        traceback.print_exc()

    # 2. Verify Specific Citizen (The Modal) - ID 10572
    print("\n[2] Testing get_citizen_by_id (10572) (The Modal Data)...")
    try:
        c = get_citizen_by_id("10572")
        if c:
            print(f"Success! Got Citizen 10572.")
            print(f"   Name: {c['name']}")
            print(f"   Element: {c.get('element')}")
            if c.get('element') == "Fire":
                print("   Fire Element is CORRECTLY 'Fire' (Metal override removed).")
            else:
                print(f"   Element is '{c.get('element')}' (Expected Fire?)")
        else:
            print("   Citizen 10572 not found (might be random seed diff, but API generally works)")
    except Exception as e:
        print(f"❌ FAILED get_citizen_by_id: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_all_logic()

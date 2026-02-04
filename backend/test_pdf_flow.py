import requests
import time
import sys
import json

# Create a dummy PDF
def create_dummy_pdf(filename="test.pdf"):
    with open(filename, "wb") as f:
        f.write(b"%PDF-1.4\n%EOF")
    return filename

def test_pdf_upload():
    print("🚀 Starting PDF Upload Test...")
    pdf_path = create_dummy_pdf()
    
    url = "http://localhost:8000/api/web/trigger"
    files = {'files': open(pdf_path, 'rb')}
    data = {
        'sim_id': f'test_pdf_{int(time.time())}',
        'language': 'zh-TW',
        'expert_mode': 'false',
        'force_random': 'false'
    }
    
    try:
        print(f"📡 Sending request to {url}...")
        response = requests.post(url, files=files, data=data)
        response.raise_for_status()
        result = response.json()
        print(f"✅ Upload successful. Sim ID: {result['sim_id']}")
        return result['sim_id']
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        if 'response' in locals():
            print(f"Response: {response.text}")
        sys.exit(1)

def verify_db(sim_id):
    print(f"🔍 Verifying DB for {sim_id}...")
    # Polling DB
    from app.core.database import get_simulation
    
    for i in range(20): # Wait up to 20 seconds
        time.sleep(2)
        sim = get_simulation(sim_id)
        if not sim:
             print("   - Waiting for DB record...")
             continue
             
        status = sim.get("status")
        print(f"   - Status: {status}")
        
        if status == "ready":
             # Check Key Fields
             arena = sim.get("arena_comments", [])
             abm = sim.get("abm_evolution") or sim.get("result_data", {}).get("abm_evolution") # Check root or nested if structure changed
             # Actually locally my code puts it in result_data['abm_evolution'] directly in the service layer update
             # But let's check the dict returned by get_simulation
             
             print(f"   - Arena Comments: {len(arena)}")
             if len(arena) > 0:
                 print(f"     First Comment: {arena[0].get('text', '')[:20]}... (Persona: {bool(arena[0].get('persona'))})")
                 
             print(f"   - ABM Evolution: {bool(abm)}")
             
             if len(arena) > 0 and abm:
                 print("🎉 TEST PASSED: Both Arena and ABM data present!")
                 return True
             else:
                 print("❌ TEST FAILED: Missing data.")
                 print(f"     Arena: {len(arena)}, ABM: {bool(abm)}")
                 return False
                 
    print("⏳ Timeout waiting for simulation to complete.")
    return False

if __name__ == "__main__":
    sim_id = test_pdf_upload()
    success = verify_db(sim_id)
    if not success:
        sys.exit(1)

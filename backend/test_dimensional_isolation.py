import asyncio
import sys
import os
import json

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.services.line_bot_service import LineBotService

async def test_isolation():
    print("🚀 Starting Dimensional Isolation Verification...")
    service = LineBotService()
    
    # Mock data
    sim_id = "test-isolation-uuid"
    language = "zh-TW"
    text_context = "產品名稱：MIRRA 核心分析儀\n售價：TWD 1500\n描述：一款基於八字命理與行為科學的市場預演系統，幫助創業者降低風險。"
    
    # Mock image bytes (dummy)
    dummy_image = b"fake-image-bytes"
    
    print("🧪 Running simulation (Image Flow)...")
    try:
        # We need to mock the Gemini call or just let it run if API key is set
        # Since I'm in the environment, I'll let it run.
        await service.run_simulation_with_image_data([dummy_image], sim_id, text_context, language)
        
        print("✅ Simulation triggered. Checking DB for results...")
        
        # Check database (using get_simulation)
        from app.core.database import get_simulation
        import time
        
        # Poll for 2 minutes
        for _ in range(24):
            data = get_simulation(sim_id)
            if data and data.get("status") == "ready":
                print("🎉 Simulation Ready!")
                methodology = data.get("methodology_data", {})
                metric_advice = methodology.get("metric_advice", {})
                
                print("\n--- DIMENSIONAL ISOLATION RESULTS ---")
                print(f"📈 Market Potential: {metric_advice.get('market_potential', 'MISSING')}")
                print(f"💰 Collection Value: {metric_advice.get('collection_value', 'MISSING')}")
                print(f"✅ Coverage: {metric_advice.get('coverage', 'MISSING')}")
                
                # Check for overlaps
                p = metric_advice.get('market_potential', '').lower()
                c = metric_advice.get('collection_value', '').lower()
                
                if "收藏" in p or "稀缺" in p:
                    print("⚠️ WARNING: Market Potential advice contains Collection keywords!")
                if "需求" in c or "痛點" in c:
                    print("⚠️ WARNING: Collection Value advice contains Market keywords!")
                
                break
            time.sleep(5)
        else:
            print("❌ Simulation timed out.")
            
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_isolation())

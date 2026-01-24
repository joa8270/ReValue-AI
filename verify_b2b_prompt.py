
import asyncio
import sys
import os
import io # Import io module
from unittest.mock import MagicMock, patch

# Set paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

async def test_b2b_prompt_logic():
    print("🧪 Starting B2B Prompt Verification...")
    
    # Mock Environment
    os.environ["GOOGLE_API_KEY"] = "mock_key"
    
    # Import Service
    from app.services.line_bot_service import LineBotService
    service = LineBotService()
    
    # Mock Database get_simulation
    with patch('app.core.database.get_simulation') as mock_get_sim:
        # Simulate B2B Scenario
        mock_get_sim.return_value = {
            "simulation_metadata": {
                "analysis_scenario": "b2b",
                "expert_mode": False
            }
        }
        
        # Mock other dependencies
        with patch('fastapi.concurrency.run_in_threadpool') as mock_thread:
            # Mock citizen data
            mock_thread.return_value = [
                {
                    "id": "1", 
                    "name": "B2B_Citizen", 
                    "age": 35,
                    "occupation": "General",
                    "gender": "male",
                    "bazi_profile": {"element": "Metal", "structure": "Seven Killings"},
                    "traits": ["Rational"],
                    "location": "Taipei"
                }
            ]
            
            # Mock ABM
            service._run_abm_simulation = MagicMock()
            async def async_abm_return(*args, **kwargs):
                return {"evolution_data": {}, "analytics_data": {}, "comments_data": []}
            service._run_abm_simulation.side_effect = async_abm_return
            
            # Mock Gemini Call to intercept prompt
            service._call_gemini_rest = MagicMock()
            async def async_gemini_return(key, prompt, **kwargs):
                print("\n👀 [Captured Prompt Snippet] 👀")
                
                # Write to file for verification
                with open("captured_prompt.txt", "w", encoding="utf-8") as f:
                    f.write(prompt)
                
                # Verification Logic
                is_b2b = "首席商業評測官" in prompt or "CFO" in prompt
                if is_b2b:
                    print("\n✅ Verification PASSED: B2B Keywords found in prompt.")
                    return "{}", "" 
                else:
                    print("\n❌ Verification FAILED: B2B Keywords NOT found.")
                    return None, "Error"
            
            service._call_gemini_rest.side_effect = async_gemini_return
            
            # Run the method
            # Dummy image bytes
            dummy_image = b"fake_image_data"
            await service.run_simulation_with_image_data(dummy_image, "test_sim_id", language="zh-TW")

if __name__ == "__main__":
    asyncio.run(test_b2b_prompt_logic())

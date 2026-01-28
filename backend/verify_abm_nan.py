
import sys
import os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.abm_engine import ABMSimulation

def test_abm_nan_handling():
    print("Testing ABM Engine regarding NaN handling...")
    
    # 1. Create Empty Simulation (Potential Source of NaN)
    citizens = [] # No citizens
    product = {"element": "Fire", "price": 100, "market_price": 100}
    
    sim = ABMSimulation(citizens, product)
    
    # 2. Run Initialize (Should handle empty agents)
    print("   - Running initialize_opinions...")
    try:
        sim.initialize_opinions()
        print("     [OK] initialize_opinions passed")
    except Exception as e:
        print(f"     [FAIL] initialize_opinions error: {e}")

    # 3. Run Iterations
    print("   - Running iterations...")
    try:
        sim.run_iterations(1)
        print("     [OK] run_iterations passed")
    except Exception as e:
        print(f"     [FAIL] run_iterations error: {e}")

    # 4. Analyze Emergence (Critical Step for NaN)
    print("   - Analyzing emergence...")
    try:
        data = sim.analyze_emergence()
        print(f"     Result keys: {list(data.keys())}")
        
        # Check for NaNs
        has_nan = False
        for k, v in data.items():
            if isinstance(v, (float, int)) and np.isnan(v):
                print(f"     [FAIL] Found NaN in {k}")
                has_nan = True
            elif isinstance(v, dict):
                for sub_k, sub_v in v.items():
                    if isinstance(sub_v, (float, int)) and np.isnan(sub_v):
                        print(f"     [FAIL] Found NaN in {k}.{sub_k}")
                        has_nan = True
        
        if not has_nan:
            print("     [PASS] No NaNs found in analysis result!")
        
    except Exception as e:
        print(f"     [FAIL] analyze_emergence error: {e}")

if __name__ == "__main__":
    test_abm_nan_handling()

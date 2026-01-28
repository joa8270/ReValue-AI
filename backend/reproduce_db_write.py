from app.core.database import update_simulation
import json
import random

def reproduce_write():
    # Construct a large mock payload mimicking PDF result
    personas = []
    for i in range(10):
        personas.append({
            "id": str(i),
            "name": f"Citizen_{i}",
            "age": 30,
            "bazi_profile": {"element": "Fire", "structure": "Unknown"},
            "traits": ["Trait1", "Trait2"]
        })

    suggestions = []
    for i in range(3):
        suggestions.append({
            "target": "Target",
            "advice": "Advice " * 50,
            "execution_plan": ["Step 1", "Step 2", "Step 3"]
        })

    data = {
        "status": "ready",
        "score": 85,
        "intent": "Test",
        "summary": "Summary " * 100,
        "genesis": {"personas": personas},
        "suggestions": suggestions,
        "comments": [{"text": "Comment " * 20} for _ in range(10)],
        "simulation_metadata": {"source": "test"}
    }

    print("Attempting to write to DB...")
    success = update_simulation("test_fix_debug_v1", "ready", data)
    print(f"Success: {success}")

if __name__ == "__main__":
    reproduce_write()

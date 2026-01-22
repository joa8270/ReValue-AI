import asyncio
import sys
import os
import json

# Add backend directory to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Mocking the AI response to verify extraction logic
mock_ai_response = {
    "simulation_metadata": {
        "product_category": "tech_electronics",
        "marketing_angle": "AI powered bazi analyzer",
        "bazi_analysis": "Metal and Water dominance..."
    },
    "metric_advice": {
        "market_potential": "PMF focus: Target high-end tech professionals.",
        "collection_value": "Scarcity focus: Limited access keys as NFTs.",
        "coverage": "Reliability focus: Increase sample size by 20%."
    },
    "result": {
        "score": 85,
        "summary": "Report Title\n\n[解析] ...\n\n[優化] ...\n\n[戰略] ...",
        "suggestions": []
    },
    "comments": []
}

from app.services.line_bot_service import _generate_methodology_sidecar

def test_sidecar_integration():
    print("🚀 Verifying Methodology Sidecar Extraction...")
    
    score = mock_ai_response["result"]["score"]
    summary = mock_ai_response["result"]["summary"]
    advice = mock_ai_response["metric_advice"]
    
    sidecar = _generate_methodology_sidecar(score, summary, language="zh-TW", metric_advice=advice)
    
    print(f"✅ Sidecar keys: {list(sidecar.keys())}")
    extracted_advice = sidecar.get("metric_advice", {})
    
    print("\n--- EXTRACTED ADVICE ---")
    print(f"📈 Market Potential: {extracted_advice.get('market_potential')}")
    print(f"💰 Collection Value: {extracted_advice.get('collection_value')}")
    print(f"✅ Coverage: {extracted_advice.get('coverage')}")
    
    assert extracted_advice.get('market_potential') == advice["market_potential"]
    print("\n✅ Verification SUCCESS: Logic is correctly integration and transmitting isolated advice.")

if __name__ == "__main__":
    test_sidecar_integration()

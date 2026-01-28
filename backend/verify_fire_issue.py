from app.core.database import get_random_citizens
from app.core.abm_engine import ABMSimulation
from collections import Counter

def check_random_distribution():
    print("----- 1. Testing Random Sampling -----")
    citizens = get_random_citizens(sample_size=30, stratified=True)
    elements = [c["bazi_profile"].get("element") for c in citizens]
    
    counts = Counter(elements)
    print("Element Distribution in Sample (n=30):")
    print(counts)
    
    # DEBUG: Print first 5 citizens to check data structure
    print("\nDEBUG: First 5 Sampled Citizens:")
    for i, c in enumerate(citizens[:5]):
        print(f"[{i}] {c['name']} - Element: {c.get('element')} | Bazi Profile: {type(c['bazi_profile'])}")
        
    fire_count = counts.get("Fire", 0) + counts.get("火", 0)
    if fire_count > 20: 
        print("❌ ALARM: Over 2/3 are Fire! Random sampling might be broken.")
    else:
        print("✅ Random sampling looks okay.")

    return citizens

def check_abm_selection():
    print("\n----- 2. Testing ABM Simulation Selection -----")
    # Simulate a "Fire" product (which is common)
    product_info = {"element": "Fire", "price": 100, "market_price": 100}
    
    citizens = get_random_citizens(sample_size=30, stratified=True)
    sim = ABMSimulation(citizens, product_info)
    
    sim.initialize_opinions()
    
    # Check if initialization biases Fire people
    opinions = []
    ids = []
    
    for agent in sim.agents:
        ids.append(agent.id)
        opinions.append(agent.current_opinion)
        
    print(f"Initial Avg Opinion: {sum(opinions)/len(opinions):.2f}")
    
    sim.run_iterations(5)
    
    # Check final comments selection logic
    comments = sim.get_final_comments(10)
    
    print("\nFinal Selected 10 Citizens for Comments:")
    selected_elements = []
    for c in comments:
        elem = c.get("element", "Unknown")
        selected_elements.append(elem)
        print(f"- {c['name']}: {elem}")
        
    cnts = Counter(selected_elements)
    print("\nDistribution in Final 10:")
    print(cnts)
    
    if cnts.get("Fire", 0) + cnts.get("火", 0) >= 8:
        print("❌ ALARM: Final selection is heavily biased towards Fire!")
    else:
        print("✅ ABM Selection looks balanced.")

if __name__ == "__main__":
    try:
        check_random_distribution()
        check_abm_selection()
    except Exception as e:
        print(e)
        import traceback
        traceback.print_exc()

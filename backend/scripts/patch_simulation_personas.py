
import sys
import os
import json
import copy
from sqlalchemy.orm.attributes import flag_modified

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.insert(0, backend_dir)

from app.core.database import SessionLocal, Simulation, Citizen

def patch_simulation_personas():
    print("=" * 60)
    print("🔥 MIRRA Simulation Data Hacking - Patching Elements")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        simulations = db.query(Simulation).all()
        print(f"📊 Found {len(simulations)} simulations.")
        
        # Cache citizens to avoid N+1 queries
        # If dataset is huge (e.g. >10k citizens), this might be heavy, 
        # but for 1000 citizens it's fine and much faster.
        print("   Loading citizen cache...")
        citizens_cache = {}
        all_citizens = db.query(Citizen).all()
        for c in all_citizens:
            # Normalize ID to string for lookup
            citizens_cache[str(c.id)] = c
            
        print(f"   Loaded {len(citizens_cache)} citizens into memory.")
        
        updated_sims = 0
        
        for sim in simulations:
            data = sim.data
            if not data:
                continue
                
            comments = data.get("arena_comments", [])
            if not comments:
                continue
                
            needs_update = False
            patched_count = 0
            
            for comment in comments:
                persona = comment.get("persona", {})
                
                # Check if element is missing or generic
                current_element = persona.get("element")
                
                # We want to patch if check is missing
                # or if we just want to ensure consistency.
                
                civ_id = str(persona.get("id"))
                
                if civ_id in citizens_cache:
                    real_civ = citizens_cache[civ_id]
                    real_bazi = real_civ.bazi_profile or {}
                    real_element = real_bazi.get("element")
                    
                    if real_element and real_element != current_element:
                        persona["element"] = real_element
                        # Also patch Bazi Structure if missing
                        if "pattern" not in persona or not persona["pattern"]:
                            persona["pattern"] = real_bazi.get("structure") # structure vs pattern naming
                            
                        needs_update = True
                        patched_count += 1
                else:
                    # Citizen ID in simulation not found in DB (maybe deleted or old ID?)
                    pass

            if needs_update:
                # IMPORTANT: Use deepcopy to ensure a fresh object reference for SQLAlchemy
                sim.data = copy.deepcopy(data)
                flag_modified(sim, "data")
                db.commit() # Commit immediately
                updated_sims += 1
                print(f"   [+] Patched Simulation {sim.sim_id}: Updated {patched_count} comments.")

        print(f"✅ Successfully patched {updated_sims} simulations.")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error during patch: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    patch_simulation_personas()

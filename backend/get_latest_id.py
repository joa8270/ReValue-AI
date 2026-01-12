from sqlalchemy import create_engine, text
engine = create_engine("sqlite:///./test.db")
with engine.connect() as conn:
    result = conn.execute(text("SELECT sim_id FROM simulations ORDER BY rowid DESC LIMIT 1"))
    row = result.fetchone()
    if row:
        print(f"FULL_ID:{row[0]}")
    else:
        print("NONE")

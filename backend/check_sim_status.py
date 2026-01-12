from sqlalchemy import create_engine, text
import json

engine = create_engine("sqlite:///./test.db")

sim_id = "5ef8187e-d459-451f-8717-1f4a9b6c4b88"

with engine.connect() as conn:
    result = conn.execute(text("SELECT status, data FROM simulations WHERE sim_id = :sim_id"), {"sim_id": sim_id})
    row = result.fetchone()
    if row:
        print(f"STATUS: {row[0]}")
        # Print a snippet of data to verify it's not empty
        data_str = str(row[1])
        print(f"DATA_LENGTH: {len(data_str)}")
        print(f"DATA_SNIPPET: {data_str[:100]}")
    else:
        print("NOT_FOUND")

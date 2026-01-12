from sqlalchemy import create_engine
engine = create_engine("sqlite:///./test.db")
# Just creating the db file
conn = engine.connect()
conn.close()
print("Created empty test.db")

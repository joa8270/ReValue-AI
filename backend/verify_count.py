from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='backend/.env')

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    # Try to find local database
    DATABASE_URL = 'sqlite:///./backend/test.db'
    print(f"Using default local DB: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text('SELECT COUNT(*) FROM citizens'))
        count = result.scalar()
        print(f'Total Citizens: {count}')
        
        # Check profiles distribution
        try:
            # For JSONB in Postgres
            result = connection.execute(text("""
                SELECT 
                    COUNT(*) FILTER (WHERE profiles ? 'TW') as tw_count,
                    COUNT(*) FILTER (WHERE profiles ? 'US') as us_count,
                    COUNT(*) FILTER (WHERE profiles ? 'CN') as cn_count
                FROM citizens
            """))
            row = result.fetchone()
            print(f'Profiles - TW: {row[0]}, US: {row[1]}, CN: {row[2]}')
        except Exception as e:
            print(f"Detailed profile count skipped (likely SQLite): {e}")

except Exception as e:
    print(f'Error: {e}')

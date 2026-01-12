"""
更新資料庫結構：添加 occupation 欄位
支援 SQLite 和 PostgreSQL
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from app.core.database import engine, SessionLocal, Citizen, Base
from sqlalchemy import text, inspect

print("連接資料庫...")

# 檢查是否為 SQLite
is_sqlite = 'sqlite' in str(engine.url)
print(f"資料庫類型: {'SQLite' if is_sqlite else 'PostgreSQL'}")

# 檢查 occupation 欄位是否存在
inspector = inspect(engine)
columns = [col['name'] for col in inspector.get_columns('citizens')]
print(f"現有欄位: {columns}")

if 'occupation' not in columns:
    print("添加 occupation 欄位...")
    with engine.connect() as conn:
        if is_sqlite:
            conn.execute(text('ALTER TABLE citizens ADD COLUMN occupation VARCHAR(100)'))
        else:
            conn.execute(text('ALTER TABLE citizens ADD COLUMN IF NOT EXISTS occupation VARCHAR(100)'))
        conn.commit()
    print("✅ occupation 欄位已添加")
else:
    print("✅ occupation 欄位已存在")

# 檢查市民數量
db = SessionLocal()
count = db.query(Citizen).count()
print(f"市民數量: {count}")
db.close()

print("完成!")

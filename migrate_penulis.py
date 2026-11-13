from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE artikel ADD COLUMN IF NOT EXISTS penulis VARCHAR DEFAULT 'Dikya Abidullah'"))
    conn.commit()
    print("Kolom penulis berhasil ditambahkan!")
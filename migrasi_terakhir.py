from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Menambah sekat untuk tabel artikel
    conn.execute(text("ALTER TABLE artikel ADD COLUMN IF NOT EXISTS penulis VARCHAR DEFAULT 'Dikya Abidullah'"))
    # Menambah sekat untuk tabel projects
    conn.execute(text("ALTER TABLE projects ADD COLUMN IF NOT EXISTS url_gambar VARCHAR"))
    conn.commit()
    print("Sekat database berhasil ditambahkan!")
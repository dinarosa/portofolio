from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Mengubah semua status yang NULL menjadi 'Complete'
    conn.execute(text("UPDATE projects SET status_pengerjaan = 'Complete' WHERE status_pengerjaan IS NULL"))
    conn.commit()
    print("Data projects berhasil diperbaiki (NULL -> Complete).")
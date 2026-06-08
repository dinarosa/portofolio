from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Mengubah alamat brankas dari SQLite lokal ke PostgreSQL Cloud
SQLALCHEMY_DATABASE_URL = "postgresql://neondb_owner:npg_i8jabCDth4rN@ep-autumn-smoke-aos048rl-pooler.c-2.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

# 2. Membuat mesin koneksi (connect_args untuk SQLite dihapus karena tidak didukung oleh Postgres)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Fungsi jembatan session database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

# 1. TABEL PROFIL
class Profil(Base):
    __tablename__ = "profil"
    id = Column(Integer, primary_key=True, index=True)
    bagian = Column(String, unique=True, index=True)
    konten = Column(Text)

# 2. TABEL REKAM JEJAK
class RekamJejak(Base):
    __tablename__ = "rekam_jejak"
    id = Column(Integer, primary_key=True, index=True)
    peran = Column(String)
    institusi = Column(String)
    periode_mulai = Column(String)
    periode_selesai = Column(String)
    deskripsi = Column(Text)

# 3. TABEL ARTIKEL
class Artikel(Base):
    __tablename__ = "artikel"
    id = Column(Integer, primary_key=True, index=True)
    kategori = Column(String)
    judul = Column(String, index=True)
    slug = Column(String, unique=True, index=True, nullable=True)  # URL spesifik artikel
    url_gambar = Column(String, nullable=True)                     # Foto kover/thumbnail
    ringkasan = Column(String, nullable=True)                      # Teks preview singkat
    konten = Column(Text)
    tanggal_publikasi = Column(DateTime, default=datetime.utcnow)

# 4. TABEL LENSA (Bug #5 Fixed)
class Lensa(Base):
    __tablename__ = "lensa"
    id = Column(Integer, primary_key=True, index=True)
    url_gambar = Column(String)
    caption = Column(String)

# 5. TABEL PROJECT (Fitur #17 Added)
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    judul = Column(String, index=True)
    tags = Column(String)
    deskripsi = Column(Text)
    status_pengerjaan = Column(String, default="Complete") # Complete / In Progress / Coming Soon
    url_demo = Column(String, nullable=True)     # <--- Tambahkan ini
    url_github = Column(String, nullable=True)

# 6. TABEL PESAN (Bug #6 Data Aligned)
class Pesan(Base):
    __tablename__ = "pesan"
    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String)
    email = Column(String)
    konten = Column(Text)
    tanggal_dikirim = Column(DateTime, default=datetime.utcnow)

 # 7. TABEL DOKUMEN (Menyelesaikan Bug #1 - Tautan Dinamis)
class Dokumen(Base):
    __tablename__ = "dokumen"
    id = Column(Integer, primary_key=True, index=True)
    nama_dokumen = Column(String, unique=True, index=True) # Misal: "Resume", "CV", "Portofolio_PDF"
    url_tautan = Column(String)
    terakhir_diperbarui = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
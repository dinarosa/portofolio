from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

# 1. TABEL PROFIL (Menyimpan teks statis untuk Beranda & Visi)
class Profil(Base):
    __tablename__ = "profil"
    id = Column(Integer, primary_key=True, index=True)
    bagian = Column(String, unique=True, index=True) # Misal: "BERANDA" atau "VISI"
    konten = Column(Text)

# 2. TABEL REKAM JEJAK (Pengalaman profesional & akademis)
class RekamJejak(Base):
    __tablename__ = "rekam_jejak"
    id = Column(Integer, primary_key=True, index=True)
    peran = Column(String) # Misal: "Pengajar" atau "Administrator"
    institusi = Column(String)
    periode_mulai = Column(String)
    periode_selesai = Column(String)
    deskripsi = Column(Text)

# 3. TABEL ARTIKEL (Ruang Aksara)
class Artikel(Base):
    __tablename__ = "artikel"
    id = Column(Integer, primary_key=True, index=True)
    kategori = Column(String)
    judul = Column(String, index=True)
    konten = Column(Text)
    tanggal_publikasi = Column(DateTime, default=datetime.utcnow)

# 4. TABEL LENSA (Galeri Fotografi)
class Lensa(Base):
    __tablename__ = "lensa"
    id = Column(Integer, primary_key=True, index=True)
    url_gambar = Column(String) # Menyimpan jalur gambar, misal: "/images/kereta-airlangga.jpg"
    caption = Column(String)

# 5. TABEL PROJECT (Portofolio Teknis)
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    judul = Column(String, index=True)
    tags = Column(String)
    deskripsi = Column(Text)

# 6. TABEL PESAN (Formulir Kontak)
class Pesan(Base):
    __tablename__ = "pesan"
    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String)
    email = Column(String)
    konten = Column(Text)
    tanggal_dikirim = Column(DateTime, default=datetime.utcnow)
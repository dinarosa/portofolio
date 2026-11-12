import os
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Memuat brankas .env
load_dotenv()

# Kunci server (wajib ada, jika tidak ada beri peringatan)
SERVER_PASSWORD = os.getenv("SERVER_PASSWORD")
if not SERVER_PASSWORD:
    raise RuntimeError("SERVER_PASSWORD tidak ditemukan di file .env! Aplikasi tidak dapat berjalan.")

from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
import models
import schemas

app = FastAPI(
    title="Portfolio Core API",
    description="Infrastruktur data asinkronus dengan proteksi API Key gembok virtual.",
    version="2.0.0"
)

# ==========================================================================
# CORS – Izinkan semua asal (sesuaikan di produksi)
# ==========================================================================
origins = [
    "http://localhost:3000",       # Untuk live server / pengujian lokal
    "http://127.0.0.1:5500",       # Port alternatif lokal
    "https://devaabidya.site",     # Domain produksi utama Anda
    "https://bisnis.devaabidya.site" # Subdomain bisnis Anda
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # Hanya izinkan domain di atas
    allow_credentials=True,        # Izinkan pengiriman kredensial/token
    allow_methods=["*"],           # Izinkan semua metode (GET, POST, PUT, DELETE)
    allow_headers=["*"],           # Izinkan semua jenis header data
)

# ==========================================================================
# KEAMANAN – API Key (SATPAM VIRTUAL)
# ==========================================================================
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    """
    Memeriksa API Key yang dikirim melalui header X-API-Key.
    Menggunakan perbandingan aman (timing-attack safe).
    """
    if api_key and secrets.compare_digest(api_key, SERVER_PASSWORD):
        return api_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Akses ditolak! Kunci keamanan tidak valid atau tidak disediakan."
    )

# ==========================================================================
# FUNGSI NOTIFIKASI EMAIL (Bug #6)
# ==========================================================================
def kirim_notifikasi_email(nama: str, email_pengirim: str, pesan_konten: str):
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    receiver_email = os.getenv("EMAIL_RECEIVER")

    if not sender_email or not sender_password:
        print("SMTP Alert: Kredensial email di .env belum diatur.")
        return

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"💬 Pesan Portofolio: {nama}"

    body = f"Anda menerima pesan baru!\n\nDari: {nama}\nEmail: {email_pengirim}\n\nIsi Pesan:\n{pesan_konten}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"SMTP Gagal: {e}")

# ==========================================================================
# ROOT – Pengecekan status API
# ==========================================================================
@app.get("/", tags=["Root"])
def root():
    return {"status": "online", "message": "Portfolio Core API v2.0.0 siap digunakan."}


# ==========================================================================
# 1. RUTE PROFIL (Beranda & Visi)
# ==========================================================================
@app.get("/api/v1/profil/{bagian}", response_model=schemas.ProfilResponse, tags=["Profil"])
def read_profil(bagian: str, db: Session = Depends(get_db)):
    return db.query(models.Profil).filter(models.Profil.bagian == bagian.upper()).first()

@app.post("/api/v1/profil", response_model=schemas.ProfilResponse, status_code=201, tags=["Profil"])
def create_profil(profil: schemas.ProfilCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_profil = models.Profil(**profil.model_dump())
    db.add(db_profil)
    db.commit()
    db.refresh(db_profil)
    return db_profil

@app.put("/api/v1/profil/{bagian}", response_model=schemas.ProfilResponse, tags=["Profil"])
def update_profil(bagian: str, profil_data: schemas.ProfilCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_profil = db.query(models.Profil).filter(models.Profil.bagian == bagian.upper()).first()
    if not db_profil:
        raise HTTPException(status_code=404, detail="Profil tidak ditemukan")
    db_profil.konten = profil_data.konten
    db.commit()
    db.refresh(db_profil)
    return db_profil


# ==========================================
# 2. RUTE PROJECT (Portofolio Teknis)
# ==========================================
@app.get("/api/v1/projects", response_model=List[schemas.ProjectResponse], tags=["Project"])
def read_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).all()

@app.post("/api/v1/projects", response_model=schemas.ProjectResponse, status_code=201, tags=["Project"])
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.put("/api/v1/projects/{project_id}", response_model=schemas.ProjectResponse, tags=["Project"])
def update_project(project_id: int, project_data: schemas.ProjectCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project tidak ditemukan")
    db_project.judul = project_data.judul
    db_project.tags = project_data.tags
    db_project.deskripsi = project_data.deskripsi
    
    # Update Fitur #17
    if hasattr(project_data, 'status_pengerjaan'):
        db_project.status_pengerjaan = project_data.status_pengerjaan
        
    db.commit()
    db.refresh(db_project)
    return db_project

@app.delete("/api/v1/projects/{project_id}", tags=["Project"])
def delete_project(project_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project tidak ditemukan")
    db.delete(project)
    db.commit()
    return {"message": f"Project dengan ID {project_id} berhasil dihapus"}


# ==========================================
# 3. RUTE ARTIKEL (Ruang Aksara)
# ==========================================
@app.put("/api/v1/artikel/{artikel_id}", response_model=schemas.ArtikelResponse)
def update_artikel(artikel_id: int, artikel_data: schemas.ArtikelCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_artikel = db.query(models.Artikel).filter(models.Artikel.id == artikel_id).first()
    if not db_artikel: raise HTTPException(status_code=404, detail="Artikel tidak ditemukan")
    
    db_artikel.kategori = artikel_data.kategori
    db_artikel.judul = artikel_data.judul
    db_artikel.slug = artikel_data.slug
    db_artikel.url_gambar = artikel_data.url_gambar
    db_artikel.ringkasan = artikel_data.ringkasan
    db_artikel.konten = artikel_data.konten
    
    db.commit()
    db.refresh(db_artikel)
    return db_artikel


# ==========================================
# 4. RUTE REKAM JEJAK
# ==========================================
@app.get("/api/v1/rekam-jejak", response_model=List[schemas.RekamJejakResponse], tags=["Rekam Jejak"])
def read_rekam_jejak(db: Session = Depends(get_db)):
    return db.query(models.RekamJejak).all()

@app.post("/api/v1/rekam-jejak", response_model=schemas.RekamJejakResponse, status_code=201, tags=["Rekam Jejak"])
def create_rekam_jejak(rekam: schemas.RekamJejakCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_rekam = models.RekamJejak(**rekam.model_dump())
    db.add(db_rekam)
    db.commit()
    db.refresh(db_rekam)
    return db_rekam

@app.put("/api/v1/rekam-jejak/{rekam_id}", response_model=schemas.RekamJejakResponse, tags=["Rekam Jejak"])
def update_rekam_jejak(rekam_id: int, rekam_data: schemas.RekamJejakCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_rekam = db.query(models.RekamJejak).filter(models.RekamJejak.id == rekam_id).first()
    if not db_rekam:
        raise HTTPException(status_code=404, detail="Rekam jejak tidak ditemukan")
    db_rekam.peran = rekam_data.peran
    db_rekam.institusi = rekam_data.institusi
    db_rekam.periode_mulai = rekam_data.periode_mulai
    db_rekam.periode_selesai = rekam_data.periode_selesai
    db_rekam.deskripsi = rekam_data.deskripsi
    db.commit()
    db.refresh(db_rekam)
    return db_rekam

@app.delete("/api/v1/rekam-jejak/{rekam_id}", tags=["Rekam Jejak"])
def delete_rekam_jejak(rekam_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    rekam = db.query(models.RekamJejak).filter(models.RekamJejak.id == rekam_id).first()
    if not rekam:
        raise HTTPException(status_code=404, detail="Data rekam jejak tidak ditemukan")
    db.delete(rekam)
    db.commit()
    return {"message": f"Rekam jejak dengan ID {rekam_id} berhasil dihapus"}


# ==========================================
# 5. RUTE LENSA (Galeri Fotografi)
# ==========================================
@app.get("/api/v1/lensa", response_model=List[schemas.LensaResponse], tags=["Lensa"])
def read_lensa(db: Session = Depends(get_db)):
    return db.query(models.Lensa).all()

@app.post("/api/v1/lensa", response_model=schemas.LensaResponse, status_code=201, tags=["Lensa"])
def create_lensa(lensa: schemas.LensaCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_lensa = models.Lensa(**lensa.model_dump())
    db.add(db_lensa)
    db.commit()
    db.refresh(db_lensa)
    return db_lensa

@app.delete("/api/v1/lensa/{lensa_id}", tags=["Lensa"])
def delete_lensa(lensa_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    lensa = db.query(models.Lensa).filter(models.Lensa.id == lensa_id).first()
    if not lensa:
        raise HTTPException(status_code=404, detail="Foto tidak ditemukan")
    db.delete(lensa)
    db.commit()
    return {"message": f"Foto lensa dengan ID {lensa_id} berhasil dihapus"}


# ==========================================
# 6. RUTE KONTAK (Pesan Masuk)
# ==========================================
@app.get("/api/v1/pesan", response_model=List[schemas.PesanResponse], tags=["Kontak"])
def read_pesan(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    return db.query(models.Pesan).all()

@app.post("/api/v1/pesan", response_model=schemas.PesanResponse, status_code=201, tags=["Kontak"])
def create_pesan(pesan: schemas.PesanCreate, db: Session = Depends(get_db)):
    db_pesan = models.Pesan(**pesan.model_dump())
    db.add(db_pesan)
    db.commit()
    db.refresh(db_pesan)
    
    # Trigger Email Notifikasi
    kirim_notifikasi_email(
        nama=db_pesan.nama, 
        email_pengirim=db_pesan.email, 
        pesan_konten=db_pesan.konten
    )
    
    return db_pesan

@app.delete("/api/v1/pesan/{pesan_id}", tags=["Kontak"])
def delete_pesan(pesan_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    pesan = db.query(models.Pesan).filter(models.Pesan.id == pesan_id).first()
    if not pesan:
        raise HTTPException(status_code=404, detail="Pesan tidak ditemukan")
    db.delete(pesan)
    db.commit()
    return {"message": f"Pesan dengan ID {pesan_id} berhasil dihapus"}


# ==========================================
# 7. RUTE DOKUMEN (Bug #1 - Tautan Dinamis)
# ==========================================
@app.get("/api/v1/dokumen", response_model=List[schemas.DokumenResponse], tags=["Dokumen"])
def read_dokumen(db: Session = Depends(get_db)):
    # TERBUKA: Publik bisa melihat tautan untuk mendownload CV/Resume
    return db.query(models.Dokumen).all()

@app.post("/api/v1/dokumen", response_model=schemas.DokumenResponse, status_code=201, tags=["Dokumen"])
def create_atau_update_dokumen(dokumen: schemas.DokumenCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    # DIGEMBOK: Hanya Admin yang bisa memperbarui tautan
    db_dokumen = db.query(models.Dokumen).filter(models.Dokumen.nama_dokumen == dokumen.nama_dokumen).first()
    
    if db_dokumen:
        db_dokumen.url_tautan = dokumen.url_tautan
        db_dokumen.terakhir_diperbarui = datetime.utcnow()
    else:
        db_dokumen = models.Dokumen(**dokumen.model_dump())
        db.add(db_dokumen)
        
    db.commit()
    db.refresh(db_dokumen)
    return db_dokumen
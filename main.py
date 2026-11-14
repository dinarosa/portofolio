import os
import secrets
from dotenv import load_dotenv
from typing import List, Optional
from bs4 import BeautifulSoup
from fastapi.responses import HTMLResponse, FileResponse
from fastapi import FastAPI, Depends, HTTPException, Security, status, Request

# Memuat brankas .env
load_dotenv()

SERVER_PASSWORD = os.getenv("SERVER_PASSWORD")
if not SERVER_PASSWORD:
    raise RuntimeError("SERVER_PASSWORD tidak ditemukan di file .env! Aplikasi tidak dapat berjalan.")

from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
import models
import schemas
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI(
    title="Portfolio Core API",
    description="Infrastruktur data asinkronus dengan proteksi API Key gembok virtual.",
    version="2.0.0"
)

limiter = Limiter(key_func=get_remote_address, default_limits=["200/hour"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ==========================================================================
# CORS
# ==========================================================================
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:5500",
    "https://devaabidya.site",
    "https://www.devaabidya.site",
    "https://bisnis.devaabidya.site",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
    max_age=3600,
)

# ==========================================================================
# KEAMANAN – API Key
# ==========================================================================
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key and secrets.compare_digest(api_key, SERVER_PASSWORD):
        return api_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Akses ditolak! Kunci keamanan tidak valid atau tidak disediakan."
    )

# ==========================================================================
# ROOT
# ==========================================================================
@app.get("/", tags=["Root"])
def root():
    return {"status": "online", "message": "Portfolio Core API v2.0.0 siap digunakan."}

# ==========================================================================
# 1. RUTE PROFIL
# ==========================================================================
@app.get("/api/v1/profil/{bagian}", response_model=schemas.ProfilResponse, tags=["Profil"])
def read_profil(bagian: str, db: Session = Depends(get_db)):
    profil = db.query(models.Profil).filter(models.Profil.bagian == bagian.upper()).first()
    if not profil:
        raise HTTPException(status_code=404, detail="Profil tidak ditemukan")
    return profil

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
# 2. RUTE PROJECT
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
    db_project.status_pengerjaan = project_data.status_pengerjaan
    db_project.url_demo = project_data.url_demo
    db_project.url_github = project_data.url_github
    db_project.url_gambar = project_data.url_gambar # Tambahan
    
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
# 3. RUTE ARTIKEL
# ==========================================
@app.get("/api/v1/artikel", response_model=List[schemas.ArtikelResponse], tags=["Artikel"])
@limiter.limit("60/minute")
def read_artikel(request: Request, kategori: Optional[str] = None, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    query = db.query(models.Artikel)
    if kategori:
        query = query.filter(models.Artikel.kategori == kategori)
    return query.order_by(models.Artikel.tanggal_publikasi.desc()).offset(skip).limit(limit).all()

@app.get("/api/v1/artikel/{artikel_id}", response_model=schemas.ArtikelResponse, tags=["Artikel"])
def read_artikel_detail(artikel_id: int, db: Session = Depends(get_db)):
    artikel = db.query(models.Artikel).filter(models.Artikel.id == artikel_id).first()
    if not artikel:
        raise HTTPException(status_code=404, detail="Artikel tidak ditemukan")
    return artikel

@app.post("/api/v1/artikel", response_model=schemas.ArtikelResponse, status_code=201, tags=["Artikel"])
def create_artikel(artikel: schemas.ArtikelCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    if artikel.slug:
        existing = db.query(models.Artikel).filter(models.Artikel.slug == artikel.slug).first()
        if existing:
            raise HTTPException(status_code=409, detail=f"Slug '{artikel.slug}' sudah dipakai")
    db_artikel = models.Artikel(**artikel.model_dump())
    db.add(db_artikel)
    db.commit()
    db.refresh(db_artikel)
    return db_artikel

@app.put("/api/v1/artikel/{artikel_id}", response_model=schemas.ArtikelResponse, tags=["Artikel"])
def update_artikel(artikel_id: int, artikel_data: schemas.ArtikelCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_artikel = db.query(models.Artikel).filter(models.Artikel.id == artikel_id).first()
    if not db_artikel:
        raise HTTPException(status_code=404, detail="Artikel tidak ditemukan")
    
    db_artikel.kategori = artikel_data.kategori
    db_artikel.judul = artikel_data.judul
    db_artikel.slug = artikel_data.slug
    db_artikel.url_gambar = artikel_data.url_gambar
    db_artikel.ringkasan = artikel_data.ringkasan
    db_artikel.konten = artikel_data.konten
    db_artikel.penulis = artikel_data.penulis # Tambahan
    
    db.commit()
    db.refresh(db_artikel)
    return db_artikel

@app.delete("/api/v1/artikel/{artikel_id}", tags=["Artikel"])
def delete_artikel(artikel_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    artikel = db.query(models.Artikel).filter(models.Artikel.id == artikel_id).first()
    if not artikel:
        raise HTTPException(status_code=404, detail="Artikel tidak ditemukan")
    db.delete(artikel)
    db.commit()
    return {"message": f"Artikel dengan ID {artikel_id} berhasil dihapus"}

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
# 5. RUTE LENSA
# ==========================================
@app.get("/api/v1/lensa", response_model=List[schemas.LensaResponse], tags=["Lensa"])
def read_lensa(kategori: Optional[str] = None, tipe_media: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.Lensa)
    if kategori:
        query = query.filter(models.Lensa.kategori == kategori)
    if tipe_media:
        query = query.filter(models.Lensa.tipe_media == tipe_media)
    return query.order_by(models.Lensa.tanggal.desc()).all()

@app.get("/api/v1/lensa/{lensa_id}", response_model=schemas.LensaResponse, tags=["Lensa"])
def read_lensa_detail(lensa_id: int, db: Session = Depends(get_db)):
    lensa = db.query(models.Lensa).filter(models.Lensa.id == lensa_id).first()
    if not lensa:
        raise HTTPException(status_code=404, detail="Foto tidak ditemukan")
    return lensa

@app.post("/api/v1/lensa", response_model=schemas.LensaResponse, status_code=201, tags=["Lensa"])
def create_lensa(lensa: schemas.LensaCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_lensa = models.Lensa(**lensa.model_dump())
    db.add(db_lensa)
    db.commit()
    db.refresh(db_lensa)
    return db_lensa

@app.put("/api/v1/lensa/{lensa_id}", response_model=schemas.LensaResponse, tags=["Lensa"])
def update_lensa(lensa_id: int, lensa_data: schemas.LensaUpdate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_lensa = db.query(models.Lensa).filter(models.Lensa.id == lensa_id).first()
    if not db_lensa:
        raise HTTPException(status_code=404, detail="Foto tidak ditemukan")
    for field, value in lensa_data.model_dump(exclude_unset=True).items():
        setattr(db_lensa, field, value)
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
# 7. RUTE DOKUMEN
# ==========================================
@app.get("/api/v1/dokumen", response_model=List[schemas.DokumenResponse], tags=["Dokumen"])
def read_dokumen(db: Session = Depends(get_db)):
    return db.query(models.Dokumen).all()

@app.post("/api/v1/dokumen", response_model=schemas.DokumenResponse, status_code=201, tags=["Dokumen"])
def create_atau_update_dokumen(dokumen: schemas.DokumenCreate, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    db_dokumen = db.query(models.Dokumen).filter(models.Dokumen.nama_dokumen == dokumen.nama_dokumen).first()
    
    # Perbaikan: Melengkapi fungsi yang sebelumnya terpotong
    if db_dokumen:
        db_dokumen.url_tautan = dokumen.url_tautan
        db_dokumen.terakhir_diperbarui = datetime.utcnow()
    else:
        db_dokumen = models.Dokumen(**dokumen.model_dump())
        db.add(db_dokumen)
        
    db.commit()
    db.refresh(db_dokumen)
    return db_dokumen

@app.delete("/api/v1/dokumen/{dokumen_id}", tags=["Dokumen"])
def delete_dokumen(dokumen_id: int, db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    dokumen = db.query(models.Dokumen).filter(models.Dokumen.id == dokumen_id).first()
    if not dokumen:
        raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")
    db.delete(dokumen)
    db.commit()
    return {"message": f"Dokumen dengan ID {dokumen_id} berhasil dihapus"}

# ==========================================
# RUTE OPEN GRAPH (HARUS DI ATAS CATCH-ALL)
# ==========================================
@app.get("/artikel/{slug}", response_class=HTMLResponse, tags=["Frontend"])
def serve_artikel_og(slug: str, db: Session = Depends(get_db)):
    # 1. Cari artikel di database
    artikel = db.query(models.Artikel).filter(models.Artikel.slug == slug).first()
    
    # 2. Baca file index.html
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="index.html tidak ditemukan di server")
    
    # 3. Jika artikel ditemukan, suntikkan data ke HTML
    if artikel:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        judul = artikel.judul
        deskripsi = artikel.ringkasan or (artikel.konten[:150] + "...")
        gambar = artikel.url_gambar or "https://devaabidya.site/thumbnail.jpeg"
        url_halaman = f"https://devaabidya.site/artikel/{slug}"
        
        # Ubah <title>
        if soup.title:
            soup.title.string = f"{judul} | Sintesa"
        
        # Fungsi Pembantu: Memaksa Tag Meta untuk dibuat/diperbarui
        def set_meta(property_or_name, content, is_name=False):
            attr = "name" if is_name else "property"
            tag = soup.find("meta", attrs={attr: property_or_name})
            if not tag:
                tag = soup.new_tag("meta")
                tag[attr] = property_or_name
                soup.head.append(tag)
            tag["content"] = content

        # Standard Meta Description
        set_meta("description", deskripsi, is_name=True)
        
        # Open Graph (Wajib untuk Facebook/WhatsApp)
        set_meta("og:title", judul)
        set_meta("og:description", deskripsi)
        set_meta("og:image", gambar)
        set_meta("og:url", url_halaman)
        set_meta("og:type", "article")

        # Twitter Card
        set_meta("twitter:card", "summary_large_image", is_name=True)
        set_meta("twitter:title", judul, is_name=True)
        set_meta("twitter:description", deskripsi, is_name=True)
        set_meta("twitter:image", gambar, is_name=True)

        return HTMLResponse(content=str(soup))
    
    return HTMLResponse(content=html_content)

# ==========================================
# CATCH-ALL ROUTE (PALING BAWAH SEKALI)
# ==========================================
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
        raise HTTPException(status_code=404, detail="Not found")
    
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return FileResponse(full_path)
        
    return FileResponse("index.html")

from fastapi import Response

@app.get("/sitemap.xml", include_in_schema=False)
def sitemap(db: Session = Depends(get_db)):
    base_url = "https://devaabidya.site"
    # Mengambil semua artikel dari database
    articles = db.query(models.Artikel).all()
    
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Tambahkan Halaman Utama
    xml += f'  <url>\n    <loc>{base_url}/</loc>\n    <changefreq>daily</changefreq>\n    <priority>1.0</priority>\n  </url>\n'
    
    # Tambahkan Semua Link Artikel
    for art in articles:
        if art.slug:
            xml += f'  <url>\n    <loc>{base_url}/artikel/{art.slug}</loc>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>\n'
            
    xml += '</urlset>'
    
    return Response(content=xml, media_type="application/xml")
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas

app = FastAPI(title="Portfolio Core API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# 1. RUTE PROFIL (Beranda & Visi)
# ==========================================
@app.get("/api/v1/profil/{bagian}", response_model=schemas.ProfilResponse, tags=["Profil"])
def read_profil(bagian: str, db: Session = Depends(get_db)):
    return db.query(models.Profil).filter(models.Profil.bagian == bagian.upper()).first()

@app.post("/api/v1/profil", response_model=schemas.ProfilResponse, tags=["Profil"])
def create_profil(profil: schemas.ProfilCreate, db: Session = Depends(get_db)):
    db_profil = models.Profil(**profil.model_dump())
    db.add(db_profil)
    db.commit()
    db.refresh(db_profil)
    return db_profil

@app.put("/api/v1/profil/{bagian}", response_model=schemas.ProfilResponse, tags=["Profil"])
def update_profil(bagian: str, profil_data: schemas.ProfilCreate, db: Session = Depends(get_db)):
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

@app.post("/api/v1/projects", response_model=schemas.ProjectResponse, tags=["Project"])
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@app.put("/api/v1/projects/{project_id}", response_model=schemas.ProjectResponse, tags=["Project"])
def update_project(project_id: int, project_data: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project tidak ditemukan")
    db_project.judul = project_data.judul
    db_project.tags = project_data.tags
    db_project.deskripsi = project_data.deskripsi
    db.commit()
    db.refresh(db_project)
    return db_project

@app.delete("/api/v1/projects/{project_id}", tags=["Project"])
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project tidak ditemukan")
    db.delete(project)
    db.commit()
    return {"message": f"Project dengan ID {project_id} berhasil dihapus"}


# ==========================================
# 3. RUTE ARTIKEL (Ruang Aksara)
# ==========================================
@app.get("/api/v1/artikel", response_model=List[schemas.ArtikelResponse], tags=["Artikel"])
def read_artikel(db: Session = Depends(get_db)):
    return db.query(models.Artikel).all()

@app.post("/api/v1/artikel", response_model=schemas.ArtikelResponse, tags=["Artikel"])
def create_artikel(artikel: schemas.ArtikelCreate, db: Session = Depends(get_db)):
    db_artikel = models.Artikel(**artikel.model_dump())
    db.add(db_artikel)
    db.commit()
    db.refresh(db_artikel)
    return db_artikel

@app.put("/api/v1/artikel/{artikel_id}", response_model=schemas.ArtikelResponse, tags=["Artikel"])
def update_artikel(artikel_id: int, artikel_data: schemas.ArtikelCreate, db: Session = Depends(get_db)):
    db_artikel = db.query(models.Artikel).filter(models.Artikel.id == artikel_id).first()
    if not db_artikel:
        raise HTTPException(status_code=404, detail="Artikel tidak ditemukan")
    db_artikel.kategori = artikel_data.kategori
    db_artikel.judul = artikel_data.judul
    db_artikel.konten = artikel_data.konten
    db.commit()
    db.refresh(db_artikel)
    return db_artikel

@app.delete("/api/v1/artikel/{artikel_id}", tags=["Artikel"])
def delete_artikel(artikel_id: int, db: Session = Depends(get_db)):
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

@app.post("/api/v1/rekam-jejak", response_model=schemas.RekamJejakResponse, tags=["Rekam Jejak"])
def create_rekam_jejak(rekam: schemas.RekamJejakCreate, db: Session = Depends(get_db)):
    db_rekam = models.RekamJejak(**rekam.model_dump())
    db.add(db_rekam)
    db.commit()
    db.refresh(db_rekam)
    return db_rekam

@app.put("/api/v1/rekam-jejak/{rekam_id}", response_model=schemas.RekamJejakResponse, tags=["Rekam Jejak"])
def update_rekam_jejak(rekam_id: int, rekam_data: schemas.RekamJejakCreate, db: Session = Depends(get_db)):
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
def delete_rekam_jejak(rekam_id: int, db: Session = Depends(get_db)):
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

@app.post("/api/v1/lensa", response_model=schemas.LensaResponse, tags=["Lensa"])
def create_lensa(lensa: schemas.LensaCreate, db: Session = Depends(get_db)):
    db_lensa = models.Lensa(**lensa.model_dump())
    db.add(db_lensa)
    db.commit()
    db.refresh(db_lensa)
    return db_lensa

@app.delete("/api/v1/lensa/{lensa_id}", tags=["Lensa"])
def delete_lensa(lensa_id: int, db: Session = Depends(get_db)):
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
def read_pesan(db: Session = Depends(get_db)):
    return db.query(models.Pesan).all()

@app.post("/api/v1/pesan", response_model=schemas.PesanResponse, tags=["Kontak"])
def create_pesan(pesan: schemas.PesanCreate, db: Session = Depends(get_db)):
    db_pesan = models.Pesan(**pesan.model_dump())
    db.add(db_pesan)
    db.commit()
    db.refresh(db_pesan)
    return db_pesan

@app.delete("/api/v1/pesan/{pesan_id}", tags=["Kontak"])
def delete_pesan(pesan_id: int, db: Session = Depends(get_db)):
    pesan = db.query(models.Pesan).filter(models.Pesan.id == pesan_id).first()
    if not pesan:
        raise HTTPException(status_code=404, detail="Pesan tidak ditemukan")
    db.delete(pesan)
    db.commit()
    return {"message": f"Pesan dengan ID {pesan_id} berhasil dihapus"}
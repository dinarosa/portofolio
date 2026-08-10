from pydantic import BaseModel, HTTPUrl
from datetime import datetime
from typing import Optional

class ProfilBase(BaseModel):
    bagian: str
    konten: str
class ProfilCreate(ProfilBase): pass
class ProfilResponse(ProfilBase):
    id: int
    class Config: from_attributes = True

    # ==========================================
# SKEMA DOKUMEN TAUTAN (Bug #1)
# ==========================================
class DokumenBase(BaseModel):
    nama_dokumen: str
    url_tautan: str

class DokumenCreate(DokumenBase):
    pass

class DokumenResponse(DokumenBase):
    id: int
    terakhir_diperbarui: datetime
    class Config: from_attributes = True

class RekamJejakBase(BaseModel):
    peran: str
    institusi: str
    periode_mulai: str
    periode_selesai: str
    deskripsi: str
class RekamJejakCreate(RekamJejakBase): pass
class RekamJejakResponse(RekamJejakBase):
    id: int
    class Config: from_attributes = True

class ArtikelBase(BaseModel):
    kategori: str
    judul: str
    konten: str
class ArtikelCreate(ArtikelBase): pass
class ArtikelResponse(ArtikelBase):
    id: int
    tanggal_publikasi: datetime
    class Config: from_attributes = True

class LensaBase(BaseModel):
    judul: str
    deskripsi: Optional[str] = None
    url_gambar: str  # Pastikan nama field ini sama persis di seluruh file
    kategori: Optional[str] = "Fotografi"
class LensaCreate(LensaBase): pass
class LensaResponse(LensaBase):
    id: int
    class Config: from_attributes = True

class ProjectBase(BaseModel):
    judul: str
    tags: str
    deskripsi: str
    status_pengerjaan: Optional[str] = "Complete"
    url_demo: Optional[str] = None     # <--- Tambahkan ini
    url_github: Optional[str] = None   # <--- Tambahkan ini
class ProjectCreate(ProjectBase): pass
class ProjectResponse(ProjectBase):
    id: int
    class Config: from_attributes = True

class PesanBase(BaseModel):
    nama: str
    email: str
    konten: str
class PesanCreate(PesanBase): pass
class PesanResponse(PesanBase):
    id: int
    tanggal_dikirim: datetime
    class Config: from_attributes = True
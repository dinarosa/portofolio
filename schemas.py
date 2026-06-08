from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProfilBase(BaseModel):
    bagian: str
    konten: str
class ProfilCreate(ProfilBase): pass
class ProfilResponse(ProfilBase):
    id: int
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
    url_gambar: str
    caption: str
class LensaCreate(LensaBase): pass
class LensaResponse(LensaBase):
    id: int
    class Config: from_attributes = True

class ProjectBase(BaseModel):
    judul: str
    tags: str
    deskripsi: str
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
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


# ==========================================
# HELPER VALIDATOR
# ==========================================
def _validate_http_url(v: Optional[str], field_name: str) -> Optional[str]:
    if v and not (v.startswith('http://') or v.startswith('https://')):
        raise ValueError(f'{field_name} harus dimulai http:// atau https://')
    return v


# ==========================================
# PROFIL
# ==========================================
class ProfilBase(BaseModel):
    bagian: str = Field(..., min_length=1, max_length=50, pattern=r'^[A-Z0-9_]+$')
    konten: str = Field(..., min_length=1, max_length=20000)

class ProfilCreate(ProfilBase):
    pass

class ProfilResponse(BaseModel):
    id: int
    bagian: str
    konten: str
    class Config: from_attributes = True


# ==========================================
# DOKUMEN (Bug #1)
# ==========================================
class DokumenBase(BaseModel):
    nama_dokumen: str = Field(..., min_length=1, max_length=100)
    url_tautan: str = Field(..., max_length=500)

    @field_validator('url_tautan')
    @classmethod
    def validate_url(cls, v):
        return _validate_http_url(v, 'url_tautan')

class DokumenCreate(DokumenBase):
    pass

class DokumenResponse(BaseModel):
    id: int
    nama_dokumen: str
    url_tautan: str
    terakhir_diperbarui: datetime
    class Config: from_attributes = True


# ==========================================
# REKAM JEJAK
# ==========================================
class RekamJejakBase(BaseModel):
    peran: str = Field(..., min_length=2, max_length=150)
    institusi: str = Field(..., min_length=2, max_length=200)
    periode_mulai: str = Field(..., min_length=4, max_length=20)
    periode_selesai: str = Field(..., min_length=1, max_length=20)
    deskripsi: str = Field(..., min_length=1, max_length=5000)

class RekamJejakCreate(RekamJejakBase):
    pass

class RekamJejakResponse(BaseModel):
    id: int
    peran: str
    institusi: str
    periode_mulai: str
    periode_selesai: str
    deskripsi: str
    class Config: from_attributes = True


# ==========================================
# ARTIKEL (Fitur #18)
# ==========================================
class ArtikelBase(BaseModel):
    kategori: str = Field(..., min_length=1, max_length=50)
    judul: str = Field(..., min_length=3, max_length=200)
    slug: Optional[str] = Field(None, max_length=200, pattern=r'^[a-z0-9-]+$')
    url_gambar: Optional[str] = Field(None, max_length=500)
    ringkasan: Optional[str] = Field(None, max_length=500)
    konten: str = Field(..., min_length=10, max_length=50000)

    @field_validator('url_gambar')
    @classmethod
    def validate_url(cls, v):
        return _validate_http_url(v, 'url_gambar')

class ArtikelCreate(ArtikelBase):
    pass

class ArtikelResponse(BaseModel):
    id: int
    kategori: str
    judul: str
    slug: Optional[str] = None
    url_gambar: Optional[str] = None
    ringkasan: Optional[str] = None
    konten: str
    tanggal_publikasi: datetime
    class Config: from_attributes = True


# ==========================================
# LENSA (Bug #5)
# ==========================================
class LensaBase(BaseModel):
    url_gambar: str = Field(..., max_length=500)
    judul: Optional[str] = Field(None, max_length=200)
    caption: Optional[str] = Field(None, max_length=500)
    kategori: str = Field("Fotografi", max_length=50)
    tipe_media: str = Field("foto", pattern=r'^(foto|video)$')

    @field_validator('url_gambar')
    @classmethod
    def validate_url(cls, v):
        # Boleh berisi pipe (thumbnail|video_url) untuk video
        primary = v.split('|')[0]
        return _validate_http_url(primary, 'url_gambar')

class LensaCreate(LensaBase):
    pass

class LensaUpdate(BaseModel):
    url_gambar: Optional[str] = Field(None, max_length=500)
    judul: Optional[str] = Field(None, max_length=200)
    caption: Optional[str] = Field(None, max_length=500)
    kategori: Optional[str] = Field(None, max_length=50)
    tipe_media: Optional[str] = Field(None, pattern=r'^(foto|video)$')

class LensaResponse(BaseModel):
    id: int
    url_gambar: str
    judul: Optional[str] = None
    caption: Optional[str] = None
    kategori: str
    tipe_media: str
    tanggal: datetime
    class Config: from_attributes = True


# ==========================================
# PROJECT (Fitur #17)
# ==========================================
class ProjectBase(BaseModel):
    judul: str = Field(..., min_length=3, max_length=200)
    tags: str = Field(..., min_length=1, max_length=300)
    deskripsi: str = Field(..., min_length=5, max_length=5000)
    status_pengerjaan: str = Field("Complete", pattern=r'^(Complete|In Progress|Coming Soon)$')
    url_demo: Optional[str] = Field(None, max_length=500)
    url_github: Optional[str] = Field(None, max_length=500)

    @field_validator('url_demo', 'url_github')
    @classmethod
    def validate_urls(cls, v, info):
        return _validate_http_url(v, info.field_name)

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(BaseModel):
    id: int
    judul: str
    tags: str
    deskripsi: str
    status_pengerjaan: Optional[str] = None  # <--- Tambahkan Optional dan = None
    url_demo: Optional[str] = None
    url_github: Optional[str] = None
    class Config: from_attributes = True
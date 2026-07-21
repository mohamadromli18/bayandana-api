from pydantic import BaseModel
from datetime import datetime

# Skema untuk data yang diterima saat membuat Masjid baru
class OrganizationCreate(BaseModel):
    name: str

# Skema untuk format data yang dikembalikan ke pengguna (Response)
class OrganizationResponse(BaseModel):
    id: str
    name: str
    created_at: datetime
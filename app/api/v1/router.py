from fastapi import APIRouter
from app.api.v1.endpoints import accounts, organizations, journals

api_router = APIRouter()

# Endpoint yang sudah ada sebelumnya
api_router.include_router(
    organizations.router, 
    prefix="/organizations", 
    tags=["Organizations"]
)

api_router.include_router(
    accounts.router, 
    prefix="/accounts", 
    tags=["Accounts"]
)

# Daftarkan endpoint jurnal yang baru dibuat
api_router.include_router(journals.router, prefix="/journals", tags=["Journals"])
from fastapi import APIRouter
from fastapi import APIRouter
from app.api.v1.endpoints import (
    accounts, 
    journals, 
    organizations, 
    reports, 
    exports, 
    ledgers,
    dashboard
)

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

# Tambahkan rute untuk Buku Besar
api_router.include_router(ledgers.router, prefix="/ledgers", tags=["Ledgers"])

# Tambahkan ini di bagian bawah
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])

api_router.include_router(exports.router, prefix="/exports", tags=["Exports"])

api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
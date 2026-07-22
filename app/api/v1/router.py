from fastapi import APIRouter
from app.api.v1.endpoints import organizations, accounts

api_router = APIRouter()

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
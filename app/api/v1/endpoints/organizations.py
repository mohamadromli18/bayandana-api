from fastapi import APIRouter, HTTPException
from typing import List
from app.core.database import supabase
from app.schemas.organization import OrganizationCreate, OrganizationResponse

router = APIRouter()

@router.post("/", response_model=OrganizationResponse)
def create_organization(org: OrganizationCreate):
    try:
        # Memasukkan data ke tabel organizations di Supabase
        response = supabase.table("organizations").insert({"name": org.name}).execute()
        
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=400, detail="Gagal menyimpan data masjid.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[OrganizationResponse])
def get_organizations():
    try:
        # Mengambil seluruh data dari tabel organizations
        response = supabase.table("organizations").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
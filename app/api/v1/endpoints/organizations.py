# app/api/v1/endpoints/organizations.py
from fastapi import APIRouter, HTTPException
from typing import List
from app.core.database import supabase
from app.schemas.organization import OrganizationCreate, OrganizationResponse
from app.services.account_seeder import seed_default_accounts

router = APIRouter()

@router.post("/", response_model=OrganizationResponse)
def create_organization(org: OrganizationCreate):
    try:
        # 1. Memasukkan data ke tabel organizations di Supabase
        response = supabase.table("organizations").insert({"name": org.name}).execute()
        
        # 2. Periksa apakah data berhasil disimpan
        if not response.data:
            raise HTTPException(status_code=400, detail="Gagal menyimpan data organisasi.")
            
        # 3. Ekstrak ID organisasi yang baru saja dibuat
        created_org_id = response.data[0]["id"]
        
        # 4. Panggil seeder otomatis
        seeding_result = seed_default_accounts(created_org_id)
        
        if not seeding_result:
            print(f"Peringatan: Gagal menyuntikkan CoA standar PSAK 109 untuk organisasi {created_org_id}")
        
        # 5. Kembalikan data sesuai dengan skema OrganizationResponse
        return response.data[0]
        
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
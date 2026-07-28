# app/api/v1/endpoints/accounts.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.core.database import supabase
from app.schemas.account_schema import AccountCreate, AccountUpdate, AccountResponse
# Pastikan ini adalah satu-satunya sumber get_current_org_id
from app.core.security import get_current_org_id

router = APIRouter()

@router.post("/", response_model=AccountResponse)
def create_account(account: AccountCreate, org_id: str = Depends(get_current_org_id)):
    try:
        data_to_insert = account.model_dump() # Gunakan model_dump() untuk Pydantic v2
        data_to_insert["organization_id"] = org_id
        
        response = supabase.table("accounts").insert(data_to_insert).execute()
        
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=400, detail="Gagal menyimpan data akun.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[AccountResponse])
def get_all_accounts(org_id: str = Depends(get_current_org_id)):
    try:
        response = supabase.table("accounts").select("*").eq("organization_id", org_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: str, org_id: str = Depends(get_current_org_id)):
    try:
        response = supabase.table("accounts").select("*").eq("id", account_id).eq("organization_id", org_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Akun tidak ditemukan atau Anda tidak memiliki akses.")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{account_id}", response_model=AccountResponse)
def update_account(account_id: str, account_update: AccountUpdate, org_id: str = Depends(get_current_org_id)):
    try:
        update_data = account_update.dict(exclude_unset=True) 
        
        if not update_data:
            raise HTTPException(status_code=400, detail="Tidak ada data valid yang dikirim untuk diperbarui.")

        response = supabase.table("accounts").update(update_data).eq("id", account_id).eq("organization_id", org_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Akun tidak ditemukan atau gagal diperbarui.")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{account_id}")
def delete_account(account_id: str, org_id: str = Depends(get_current_org_id)):
    try:
        response = supabase.table("accounts").delete().eq("id", account_id).eq("organization_id", org_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Akun tidak ditemukan atau sudah dihapus.")
        return {"status": "sukses", "message": f"Akun dengan ID {account_id} berhasil dihapus."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
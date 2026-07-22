from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.core.database import supabase
from app.schemas.account_schema import AccountCreate, AccountUpdate, AccountResponse

router = APIRouter()

# CATATAN: Ini adalah fungsi tiruan (mock) sementara untuk mendapatkan ID Organisasi.
# Nantinya, fungsi ini akan diganti dengan ekstraksi dari token JWT JWT (di app/core/security.py)
# agar setiap pembuatan akun otomatis tertaut dengan tenant yang sedang login.
def get_current_org_id() -> str:
    # Ganti string di bawah ini dengan ID dari tabel 'organizations' yang sudah Anda buat di Supabase
    return "123e4567-e89b-12d3-a456-426614174000" 

@router.post("/", response_model=AccountResponse)
def create_account(account: AccountCreate, org_id: str = Depends(get_current_org_id)):
    try:
        # 1. Ubah objek Pydantic menjadi dictionary.
        # Gunakan .dict() jika Anda memakai Pydantic v1, atau .model_dump() untuk Pydantic v2.
        data_to_insert = account.dict() 
        
        # 2. Sisipkan ID organisasi secara otomatis ke dalam payload
        data_to_insert["organization_id"] = org_id
        
        # 3. Eksekusi insert ke Supabase
        response = supabase.table("accounts").insert(data_to_insert).execute()
        
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=400, detail="Gagal menyimpan data akun ke Supabase.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[AccountResponse])
def get_all_accounts(org_id: str = Depends(get_current_org_id)):
    try:
        # Mengambil semua akun. .eq() memastikan tenant hanya melihat akun dari organisasinya sendiri
        response = supabase.table("accounts").select("*").eq("organization_id", org_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: str, org_id: str = Depends(get_current_org_id)):
    try:
        # Mengambil satu akun spesifik berdasarkan ID dan ID Organisasi
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
        # exclude_unset=True memastikan hanya field yang dikirim user yang akan di-update (mencegah field menjadi null)
        update_data = account_update.dict(exclude_unset=True) 
        
        if not update_data:
            raise HTTPException(status_code=400, detail="Tidak ada data valid yang dikirim untuk diperbarui.")

        # Eksekusi pembaruan data
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
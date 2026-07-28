# app/core/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.database import supabase

# Skema keamanan untuk membaca header 'Authorization: Bearer <token>'
security = HTTPBearer()

def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Mengekstrak token mentah dari header"""
    return credentials.credentials

def get_current_user_and_org(token: str = Depends(get_token)) -> dict:
    """
    Memvalidasi token JWT ke Supabase dan mengambil data organisasi pengguna.
    Mengembalikan dictionary berisi 'user_id' dan 'organization_id'.
    """
    try:
        # 1. Verifikasi token langsung ke server Supabase Auth
        auth_response = supabase.auth.get_user(token)
        
        if not auth_response or not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesi tidak valid atau telah berakhir. Silakan login kembali."
            )
            
        user_id = auth_response.user.id
        
        # 2. Ambil organization_id dari tabel public.users
        profile_response = supabase.table("users").select("organization_id").eq("id", user_id).single().execute()
        
        org_id = profile_response.data.get("organization_id")
        if not org_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Akun Anda belum terhubung dengan organisasi manapun."
            )
            
        return {
            "user_id": user_id,
            "organization_id": org_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Kredensial tidak valid: {str(e)}"
        )

def get_current_org_id(user_data: dict = Depends(get_current_user_and_org)) -> str:
    """Dependency khusus jika endpoint hanya membutuhkan organization_id"""
    return user_data["organization_id"]
# schemas.py
from pydantic import BaseModel, Field, constr
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid

# 1. Enum untuk mengunci tipe akun (Strict Validation)
class AccountTypeEnum(str, Enum):
    asset = "Asset"
    liability = "Liability"
    equity = "Equity"
    revenue = "Revenue"
    expense = "Expense"

# 2. Base Schema (Atribut yang sama-sama dipakai saat Create/Read)
class AccountBase(BaseModel):
    account_code: constr(min_length=3, max_length=10) = Field(..., description="Kode akun, misal: 1110")
    account_name: constr(min_length=3, max_length=100) = Field(..., description="Nama akun, misal: Kas Kecil")
    account_type: AccountTypeEnum = Field(..., description="Klasifikasi akun (Asset, Liability, dll)")
    is_active: bool = Field(default=True, description="Status aktif akun")

# 3. Schema untuk Input/Create (Dari Klien ke API)
class AccountCreate(AccountBase):
    # organization_id sengaja tidak dimasukkan di sini karena harus 
    # diekstrak secara otomatis dari Token JWT (keamanan), bukan dari input user.
    pass

# 4. Schema untuk Update
class AccountUpdate(BaseModel):
    account_name: Optional[constr(min_length=3, max_length=100)] = None
    is_active: Optional[bool] = None
    # account_code dan account_type sebaiknya tidak bisa diubah setelah dibuat 
    # untuk menjaga integritas jurnal historis.

# 5. Schema untuk Output/Response (Dari API ke Klien)
class AccountResponse(AccountBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime

    class Config:
        # Mengizinkan Pydantic membaca objek dari ORM/Supabase dict
        orm_mode = True
        from_attributes = True
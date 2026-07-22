# models.py
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid
import enum

Base = declarative_base()

# Mendefinisikan Enum di tingkat Database PostgreSQL
class AccountType(enum.Enum):
    Asset = "Asset"
    Liability = "Liability"
    Equity = "Equity"
    Revenue = "Revenue"
    Expense = "Expense"

class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Foreign Key ke tabel organizations (Penting untuk arsitektur Multi-Tenant)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    
    account_code = Column(String(10), nullable=False)
    account_name = Column(String(100), nullable=False)
    account_type = Column(SQLEnum(AccountType), nullable=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Catatan: Di Supabase, Anda wajib menyalakan RLS (Row Level Security) 
    # untuk tabel ini agar tenant tidak bisa mengintip akun milik tenant lain.
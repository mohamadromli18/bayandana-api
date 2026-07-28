# app/api/v1/endpoints/journals.py
from fastapi import APIRouter, HTTPException
from app.schemas.journal_schema import JournalCreate
from app.core.database import supabase

router = APIRouter()

@router.post("/", response_model=dict, status_code=201)
def create_journal(journal: JournalCreate):
    # 1. Siapkan data untuk tabel induk (journals)
    journal_data = {
        "organization_id": str(journal.organization_id),
        "transaction_date": journal.transaction_date.isoformat(),
        "description": journal.description,
        "reference_number": journal.reference_number
    }
    
    try:
        # 2. Insert ke tabel journals
        journal_res = supabase.table("journals").insert(journal_data).execute()
        
        if not journal_res.data:
            raise HTTPException(status_code=400, detail="Gagal membuat data induk jurnal")
        
        created_journal_id = journal_res.data[0]["id"]
        
        # 3. Siapkan data untuk tabel anak (journal_details)
        details_data = []
        for detail in journal.details:
            details_data.append({
                "journal_id": created_journal_id,
                "account_id": str(detail.account_id),
                "debit": detail.debit,
                "credit": detail.credit
            })
            
        # 4. Insert ke tabel journal_details
        details_res = supabase.table("journal_details").insert(details_data).execute()
        
        return {
            "message": "Jurnal berhasil dicatat",
            "journal_id": created_journal_id,
            "total_lines": len(details_res.data)
        }
        
    except Exception as e:
        # Jika terjadi kegagalan, idealnya Anda menerapkan mekanisme rollback
        # Namun Supabase Python client standar mengeksekusi ini secara terpisah
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan pada server: {str(e)}")
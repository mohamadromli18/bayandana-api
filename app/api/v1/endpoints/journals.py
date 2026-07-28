# app/api/v1/endpoints/journals.py
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.journal_schema import JournalCreate
from app.core.database import supabase
from app.core.security import get_current_org_id

router = APIRouter()

@router.post("/", response_model=dict, status_code=201)
def create_journal(
    journal: JournalCreate, 
    org_id: str = Depends(get_current_org_id) # Tambahkan argumen ini
):
    # 1. Siapkan data untuk tabel induk (journals) dengan org_id dari token JWT
    journal_data = {
        "organization_id": org_id, 
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
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan pada server: {str(e)}")
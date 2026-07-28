# app/api/v1/endpoints/journals.py
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from app.schemas.journal_schema import JournalCreate
from app.core.database import supabase
from app.core.security import get_current_org_id
import uuid

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

@router.post("/{journal_id}/upload-proof", status_code=200)
async def upload_transaction_proof(
    journal_id: str,
    file: UploadFile = File(...),
    org_id: str = Depends(get_current_org_id)
):
    try:
        # 1. Validasi apakah jurnal ini milik organisasi pengguna yang sedang login
        journal_res = supabase.table("journals").select("id").eq("id", journal_id).eq("organization_id", org_id).execute()
        
        if not journal_res.data:
            raise HTTPException(status_code=404, detail="Jurnal tidak ditemukan atau tidak ada akses.")

        # 2. Validasi ekstensi file keamanan dasar
        allowed_extensions = ["jpg", "jpeg", "png", "pdf"]
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Format file tidak didukung. Gunakan JPG, PNG, atau PDF.")

        # 3. Baca konten file ke dalam memori
        file_bytes = await file.read()

        # 4. Buat penamaan file yang unik dan rapi di dalam folder organisasi
        unique_filename = f"{org_id}/{journal_id}_{uuid.uuid4().hex[:8]}.{file_ext}"

        # 5. Unggah file ke Supabase Storage di bucket 'transaction_proofs'
        supabase.storage.from_("transaction_proofs").upload(
            path=unique_filename,
            file=file_bytes,
            file_options={"content-type": file.content_type}
        )

        # 6. Dapatkan URL publik dari file yang baru diunggah
        public_url = supabase.storage.from_("transaction_proofs").get_public_url(unique_filename)

        # 7. Simpan URL tersebut ke tabel journals
        supabase.table("journals").update({"proof_url": public_url}).eq("id", journal_id).execute()

        return {
            "message": "Bukti transaksi berhasil diunggah",
            "proof_url": public_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengunggah file: {str(e)}")
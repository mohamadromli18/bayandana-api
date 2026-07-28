# app/api/v1/endpoints/ledgers.py
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import date
from app.core.database import supabase
from app.core.security import get_current_org_id
from app.schemas.ledger_schema import LedgerResponse, LedgerEntry

router = APIRouter()

@router.get("/{account_id}", response_model=LedgerResponse)
def get_general_ledger(
    account_id: str,
    start_date: date = Query(..., description="Tanggal awal periode (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Tanggal akhir periode (YYYY-MM-DD)"),
    org_id: str = Depends(get_current_org_id)
):
    try:
        # 1. Validasi kepemilikan akun dan ambil tipe akun
        account_res = supabase.table("accounts").select("*").eq("id", account_id).eq("organization_id", org_id).execute()
        
        if not account_res.data:
            raise HTTPException(status_code=404, detail="Akun tidak ditemukan atau bukan milik organisasi Anda.")
            
        account = account_res.data[0]
        account_type = account["account_type"]

        # 2. Ambil data mutasi dengan relasi ke tabel journals
        # Menggunakan inner join agar kita bisa memfilter berdasarkan tanggal dan organisasi di tabel induk
        mutations_res = supabase.table("journal_details").select(
            "debit, credit, journals!inner(transaction_date, reference_number, description)"
        ).eq("account_id", account_id)\
         .eq("journals.organization_id", org_id)\
         .gte("journals.transaction_date", start_date.isoformat())\
         .lte("journals.transaction_date", end_date.isoformat()).execute()
        
        raw_data = mutations_res.data
        
        # Urutkan berdasarkan tanggal transaksi agar berurutan secara kronologis
        raw_data.sort(key=lambda x: x["journals"]["transaction_date"])

        # 3. Kalkulasi saldo berjalan
        # Catatan: Untuk penyederhanaan saat ini, saldo awal sebelum start_date diasumsikan 0.
        # Logika saldo awal historis dapat ditambahkan di pengembangan selanjutnya.
        current_balance = 0.0
        starting_balance = 0.0
        ledger_entries = []

        for row in raw_data:
            debit = float(row["debit"])
            credit = float(row["credit"])
            journal_info = row["journals"]

            # Penentuan perhitungan berdasarkan Saldo Normal
            if account_type in ["Asset", "Expense"]:
                current_balance += (debit - credit)
            else: # Liability, Equity, Revenue
                current_balance += (credit - debit)

            ledger_entries.append(LedgerEntry(
                transaction_date=journal_info["transaction_date"],
                reference_number=journal_info["reference_number"],
                description=journal_info["description"],
                debit=debit,
                credit=credit,
                balance=current_balance
            ))

        return LedgerResponse(
            account_id=account["id"],
            account_code=account["account_code"],
            account_name=account["account_name"],
            starting_balance=starting_balance,
            mutations=ledger_entries,
            ending_balance=current_balance
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# app/api/v1/endpoints/dashboard.py
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import date
from app.schemas.dashboard_schema import DashboardSummary, RecentTransaction
from app.core.security import get_current_org_id
from app.core.database import supabase

router = APIRouter()

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_data(org_id: str = Depends(get_current_org_id)):
    current_month = date.today().month
    current_year = date.today().year

    try:
        # 1. Ambil semua akun untuk membedakan tipe akun
        accounts_res = supabase.table("accounts").select("id, account_code, account_type").eq("organization_id", org_id).execute()
        accounts = {acc["id"]: acc for acc in accounts_res.data}

        # 2. Ambil semua mutasi jurnal untuk organisasi ini
        # Karena keterbatasan agregasi kompleks di REST API Supabase, kita hitung di sisi Python
        mutations_res = supabase.table("journal_details").select(
            "account_id, debit, credit, journals!inner(id, transaction_date, description)"
        ).eq("journals.organization_id", org_id).execute()

        total_saldo_kas = 0.0
        total_penerimaan = 0.0
        total_penyaluran = 0.0
        
        # Dictionary untuk mengelompokkan total transaksi terbaru
        recent_journals_map = {}

        for mut in mutations_res.data:
            acc_id = mut["account_id"]
            debit = float(mut["debit"])
            credit = float(mut["credit"])
            journal_info = mut["journals"]
            tgl_transaksi = date.fromisoformat(journal_info["transaction_date"])

            if acc_id not in accounts:
                continue

            acc_code = accounts[acc_id]["account_code"]
            
            # Hitung Saldo Kas (Kode diawali 11) -> Normal Debit
            if acc_code.startswith("11"):
                total_saldo_kas += (debit - credit)
                
            # Hitung Penerimaan & Penyaluran bulan ini
            if tgl_transaksi.month == current_month and tgl_transaksi.year == current_year:
                # Penerimaan (Kode diawali 4) -> Normal Kredit
                if acc_code.startswith("4"):
                    total_penerimaan += (credit - debit)
                # Penyaluran (Kode diawali 5) -> Normal Debit
                elif acc_code.startswith("5"):
                    total_penyaluran += (debit - credit)

            # Siapkan data untuk transaksi terbaru
            j_id = journal_info["id"]
            if j_id not in recent_journals_map:
                recent_journals_map[j_id] = {
                    "id": str(j_id),
                    "tanggal": tgl_transaksi,
                    "deskripsi": journal_info["description"],
                    "total_debit": 0.0,
                    "total_kredit": 0.0
                }
            recent_journals_map[j_id]["total_debit"] += debit
            recent_journals_map[j_id]["total_kredit"] += credit

        # Urutkan transaksi terbaru dan ambil 5 teratas
        sorted_recent = sorted(recent_journals_map.values(), key=lambda x: x["tanggal"], reverse=True)[:5]
        transaksi_terbaru = [RecentTransaction(**item) for item in sorted_recent]

        return DashboardSummary(
            total_saldo_kas=total_saldo_kas,
            penerimaan_bulan_ini=total_penerimaan,
            penyaluran_bulan_ini=total_penyaluran,
            transaksi_terbaru=transaksi_terbaru
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Terjadi kesalahan saat memproses data dashboard: {str(e)}"
        )
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract
from datetime import date

# Import Pydantic Schemas
from app.schemas.dashboard_schema import DashboardSummary, RecentTransaction

# Import Security & Database core
from app.core.security import get_current_user
from app.core.database import get_db

# Import SQLAlchemy Models
# Pastikan nama model dan file sesuai dengan struktur proyek Anda
from app.models.account_model import Account
from app.models.journal_model import Journal, JournalDetail 

router = APIRouter()

@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_data(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Ekstrak organization_id dari token JWT Supabase pengguna yang sedang login
    organization_id = current_user.get("organization_id")
    if not organization_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Organization ID tidak valid atau tidak ditemukan di token"
        )

    current_month = date.today().month
    current_year = date.today().year

    try:
        # ---------------------------------------------------------
        # 1. Total Saldo Kas & Bank (Akun Aset diawali '11')
        # Saldo Normal Debit = (Total Debit - Total Kredit)
        # ---------------------------------------------------------
        stmt_kas = (
            select(
                func.coalesce(func.sum(JournalDetail.debit) - func.sum(JournalDetail.credit), 0)
            )
            .select_from(JournalDetail)
            .join(Journal, Journal.id == JournalDetail.journal_id)
            .join(Account, Account.id == JournalDetail.account_id)
            .where(
                Journal.organization_id == organization_id,
                Account.code.like("11%"),
                Journal.is_posted == True
            )
        )
        result_kas = await db.execute(stmt_kas)
        total_saldo_kas = float(result_kas.scalar() or 0.0)

        # ---------------------------------------------------------
        # 2. Total Penerimaan Bulan Ini (Akun Pendapatan Dana diawali '4')
        # Saldo Normal Kredit = (Total Kredit - Total Debit)
        # ---------------------------------------------------------
        stmt_penerimaan = (
            select(
                func.coalesce(func.sum(JournalDetail.credit) - func.sum(JournalDetail.debit), 0)
            )
            .select_from(JournalDetail)
            .join(Journal, Journal.id == JournalDetail.journal_id)
            .join(Account, Account.id == JournalDetail.account_id)
            .where(
                Journal.organization_id == organization_id,
                Account.code.like("4%"), 
                extract('month', Journal.date) == current_month,
                extract('year', Journal.date) == current_year,
                Journal.is_posted == True
            )
        )
        result_penerimaan = await db.execute(stmt_penerimaan)
        total_penerimaan = float(result_penerimaan.scalar() or 0.0)

        # ---------------------------------------------------------
        # 3. Total Penyaluran Bulan Ini (Akun Beban/Penyaluran diawali '5')
        # Saldo Normal Debit = (Total Debit - Total Kredit)
        # ---------------------------------------------------------
        stmt_penyaluran = (
            select(
                func.coalesce(func.sum(JournalDetail.debit) - func.sum(JournalDetail.credit), 0)
            )
            .select_from(JournalDetail)
            .join(Journal, Journal.id == JournalDetail.journal_id)
            .join(Account, Account.id == JournalDetail.account_id)
            .where(
                Journal.organization_id == organization_id,
                Account.code.like("5%"), 
                extract('month', Journal.date) == current_month,
                extract('year', Journal.date) == current_year,
                Journal.is_posted == True
            )
        )
        result_penyaluran = await db.execute(stmt_penyaluran)
        total_penyaluran = float(result_penyaluran.scalar() or 0.0)

        # ---------------------------------------------------------
        # 4. Ambil 5 Transaksi Jurnal Terbaru
        # ---------------------------------------------------------
        stmt_recent = (
            select(Journal)
            .where(Journal.organization_id == organization_id)
            .order_by(Journal.date.desc())
            .limit(5)
        )
        result_recent = await db.execute(stmt_recent)
        recent_journals = result_recent.scalars().all()

        transaksi_terbaru = []
        for journal in recent_journals:
            # Hitung total debit per jurnal untuk ditampilkan di dashboard
            stmt_journal_total = (
                select(func.coalesce(func.sum(JournalDetail.debit), 0))
                .where(JournalDetail.journal_id == journal.id)
            )
            res_total = await db.execute(stmt_journal_total)
            journal_total = float(res_total.scalar() or 0.0)

            transaksi_terbaru.append(
                RecentTransaction(
                    id=str(journal.id),
                    tanggal=journal.date,
                    deskripsi=journal.description, # Sesuaikan jika kolom Anda bernama 'memo' atau 'keterangan'
                    total_debit=journal_total,
                    total_kredit=journal_total # Karena balance, total kredit diasumsikan sama
                )
            )

        # Mengembalikan data sesuai Pydantic Schema
        return DashboardSummary(
            total_saldo_kas=total_saldo_kas,
            penerimaan_bulan_ini=total_penerimaan,
            penyaluran_bulan_ini=total_penyaluran,
            transaksi_terbaru=transaksi_terbaru
        )

    except Exception as e:
        # Menangkap error database dan menampilkannya sebagai internal server error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Terjadi kesalahan saat memproses data dashboard: {str(e)}"
        )
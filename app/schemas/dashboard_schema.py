from pydantic import BaseModel
from typing import List
from datetime import date

class RecentTransaction(BaseModel):
    id: str
    tanggal: date
    deskripsi: str
    total_debit: float
    total_kredit: float

class DashboardSummary(BaseModel):
    total_saldo_kas: float
    penerimaan_bulan_ini: float
    penyaluran_bulan_ini: float
    transaksi_terbaru: List[RecentTransaction]
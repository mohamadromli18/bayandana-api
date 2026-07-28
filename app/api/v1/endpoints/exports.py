# app/api/v1/endpoints/exports.py
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from datetime import date
import io
import openpyxl
from openpyxl.styles import Font, Alignment
from app.core.database import supabase
from app.core.security import get_current_org_id

router = APIRouter()

@router.get("/financial-position/excel")
def export_financial_position_excel(
    as_of_date: date = Query(..., description="Tanggal akhir posisi keuangan (YYYY-MM-DD)"),
    org_id: str = Depends(get_current_org_id)
):
    try:
        # 1. Ambil data akun dan mutasi (Logika yang sama dengan reports.py)
        accounts_res = supabase.table("accounts").select("id, account_code, account_name, account_type")\
            .eq("organization_id", org_id)\
            .in_("account_type", ["Asset", "Liability", "Equity"]).execute()
            
        accounts = accounts_res.data
        if not accounts:
            raise HTTPException(status_code=404, detail="Tidak ada data akun.")

        mutations_res = supabase.table("journal_details").select(
            "account_id, debit, credit, journals!inner(transaction_date)"
        ).eq("journals.organization_id", org_id)\
         .lte("journals.transaction_date", as_of_date.isoformat()).execute()
         
        account_balances = {acc["id"]: 0.0 for acc in accounts}
        account_types = {acc["id"]: acc["account_type"] for acc in accounts}
        
        for mut in mutations_res.data:
            acc_id = mut["account_id"]
            if acc_id in account_balances:
                debit = float(mut["debit"])
                credit = float(mut["credit"])
                if account_types[acc_id] == "Asset":
                    account_balances[acc_id] += (debit - credit)
                else:
                    account_balances[acc_id] += (credit - debit)

        # 2. Inisialisasi Workbook Excel
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Posisi Keuangan"

        # 3. Styling Dasar
        bold_font = Font(bold=True)
        center_align = Alignment(horizontal="center")

        # 4. Tulis Header Dokumen
        ws.append(["LAPORAN POSISI KEUANGAN (NERACA)"])
        ws["A1"].font = bold_font
        ws.append([f"Per Tanggal: {as_of_date.isoformat()}"])
        ws.append([]) # Baris kosong

        # Header Tabel
        headers = ["Kode Akun", "Nama Akun", "Saldo (Rp)"]
        ws.append(headers)
        for col in range(1, 4):
            ws.cell(row=4, column=col).font = bold_font

        # 5. Tulis Data Aset
        ws.append(["ASET"])
        ws.cell(row=ws.max_row, column=1).font = bold_font
        total_assets = 0.0
        for acc in accounts:
            if acc["account_type"] == "Asset":
                balance = account_balances[acc["id"]]
                ws.append([acc["account_code"], acc["account_name"], balance])
                total_assets += balance
        ws.append(["Total Aset", "", total_assets])
        ws.cell(row=ws.max_row, column=1).font = bold_font
        ws.cell(row=ws.max_row, column=3).font = bold_font
        ws.append([])

        # 6. Tulis Data Kewajiban
        ws.append(["KEWAJIBAN"])
        ws.cell(row=ws.max_row, column=1).font = bold_font
        total_liabilities = 0.0
        for acc in accounts:
            if acc["account_type"] == "Liability":
                balance = account_balances[acc["id"]]
                ws.append([acc["account_code"], acc["account_name"], balance])
                total_liabilities += balance
        ws.append(["Total Kewajiban", "", total_liabilities])
        ws.cell(row=ws.max_row, column=1).font = bold_font
        ws.cell(row=ws.max_row, column=3).font = bold_font
        ws.append([])

        # 7. Tulis Data Saldo Dana (Ekuitas)
        ws.append(["SALDO DANA (EKUITAS)"])
        ws.cell(row=ws.max_row, column=1).font = bold_font
        total_equities = 0.0
        for acc in accounts:
            if acc["account_type"] == "Equity":
                balance = account_balances[acc["id"]]
                ws.append([acc["account_code"], acc["account_name"], balance])
                total_equities += balance
        ws.append(["Total Saldo Dana", "", total_equities])
        ws.cell(row=ws.max_row, column=1).font = bold_font
        ws.cell(row=ws.max_row, column=3).font = bold_font
        ws.append([])

        # Total Kewajiban & Saldo Dana
        ws.append(["Total Kewajiban & Saldo Dana", "", total_liabilities + total_equities])
        ws.cell(row=ws.max_row, column=1).font = bold_font
        ws.cell(row=ws.max_row, column=3).font = bold_font

        # 8. Lebarkan kolom agar rapi
        ws.column_dimensions['A'].width = 15
        ws.column_dimensions['B'].width = 40
        ws.column_dimensions['C'].width = 20

        # 9. Simpan ke dalam format Byte Stream
        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)

        # 10. Kembalikan sebagai File Unduhan
        filename = f"Neraca_{as_of_date.isoformat()}.xlsx"
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"'
        }
        return StreamingResponse(
            stream, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            headers=headers
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
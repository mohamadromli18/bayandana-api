# app/api/v1/endpoints/reports.py
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import date
from app.core.database import supabase
from app.core.security import get_current_org_id
from app.schemas.report_schema import FinancialPositionResponse, AccountBalance

router = APIRouter()

@router.get("/financial-position", response_model=FinancialPositionResponse)
def get_financial_position(
    as_of_date: date = Query(..., description="Tanggal akhir posisi keuangan (YYYY-MM-DD)"),
    org_id: str = Depends(get_current_org_id)
):
    try:
        # 1. Ambil semua akun Aset, Kewajiban, dan Ekuitas (Saldo Dana) milik organisasi
        accounts_res = supabase.table("accounts").select("id, account_code, account_name, account_type")\
            .eq("organization_id", org_id)\
            .in_("account_type", ["Asset", "Liability", "Equity"]).execute()
            
        accounts = accounts_res.data
        if not accounts:
            raise HTTPException(status_code=404, detail="Tidak ada data akun yang ditemukan.")

        # 2. Ambil seluruh mutasi jurnal hingga as_of_date
        mutations_res = supabase.table("journal_details").select(
            "account_id, debit, credit, journals!inner(transaction_date)"
        ).eq("journals.organization_id", org_id)\
         .lte("journals.transaction_date", as_of_date.isoformat()).execute()
         
        mutations = mutations_res.data

        # 3. Kelompokkan mutasi berdasarkan ID Akun
        account_balances = {acc["id"]: 0.0 for acc in accounts}
        account_types = {acc["id"]: acc["account_type"] for acc in accounts}
        
        for mut in mutations:
            acc_id = mut["account_id"]
            if acc_id in account_balances:
                debit = float(mut["debit"])
                credit = float(mut["credit"])
                
                # Kalkulasi berdasarkan Saldo Normal
                if account_types[acc_id] == "Asset":
                    account_balances[acc_id] += (debit - credit)
                else: # Liability & Equity
                    account_balances[acc_id] += (credit - debit)

        # 4. Susun respons berdasarkan kategori
        assets, liabilities, equities = [], [], []
        total_assets = total_liabilities = total_equities = 0.0

        for acc in accounts:
            balance = account_balances[acc["id"]]
            acc_data = AccountBalance(
                account_code=acc["account_code"],
                account_name=acc["account_name"],
                balance=balance
            )
            
            if acc["account_type"] == "Asset":
                assets.append(acc_data)
                total_assets += balance
            elif acc["account_type"] == "Liability":
                liabilities.append(acc_data)
                total_liabilities += balance
            elif acc["account_type"] == "Equity":
                equities.append(acc_data)
                total_equities += balance

        total_liabilities_and_funds = total_liabilities + total_equities
        
        # Toleransi pembulatan float saat pengecekan balance
        is_balanced = abs(total_assets - total_liabilities_and_funds) < 0.01

        return FinancialPositionResponse(
            organization_id=org_id,
            as_of_date=as_of_date.isoformat(),
            assets=assets,
            total_assets=total_assets,
            liabilities=liabilities,
            total_liabilities=total_liabilities,
            fund_balances=equities,
            total_fund_balances=total_equities,
            total_liabilities_and_funds=total_liabilities_and_funds,
            is_balanced=is_balanced
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
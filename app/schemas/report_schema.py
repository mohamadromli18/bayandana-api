# app/schemas/report_schema.py
from pydantic import BaseModel
from typing import List, Dict

class AccountBalance(BaseModel):
    account_code: str
    account_name: str
    balance: float

class FinancialPositionResponse(BaseModel):
    organization_id: str
    as_of_date: str
    assets: List[AccountBalance]
    total_assets: float
    liabilities: List[AccountBalance]
    total_liabilities: float
    fund_balances: List[AccountBalance]
    total_fund_balances: float
    total_liabilities_and_funds: float
    is_balanced: bool
    
class FundChangeItem(BaseModel):
    account_code: str
    account_name: str
    amount: float

class FundChangesResponse(BaseModel):
    organization_id: str
    start_date: str
    end_date: str
    revenues: List[FundChangeItem]
    total_revenue: float
    expenses: List[FundChangeItem]
    total_expense: float
    net_surplus_deficit: float
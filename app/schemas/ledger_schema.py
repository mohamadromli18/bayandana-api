# app/schemas/ledger_schema.py
from pydantic import BaseModel
from typing import List
from datetime import date

class LedgerEntry(BaseModel):
    transaction_date: date
    reference_number: str
    description: str
    debit: float
    credit: float
    balance: float

class LedgerResponse(BaseModel):
    account_id: str
    account_code: str
    account_name: str
    starting_balance: float
    mutations: List[LedgerEntry]
    ending_balance: float
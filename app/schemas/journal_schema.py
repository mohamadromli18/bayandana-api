# app/schemas/journal_schema.py
from pydantic import BaseModel, Field, model_validator
from typing import List, Optional
from datetime import date
from uuid import UUID

class JournalDetailBase(BaseModel):
    account_id: UUID
    debit: float = Field(default=0.0, ge=0)
    credit: float = Field(default=0.0, ge=0)

class JournalCreate(BaseModel):
    organization_id: UUID
    transaction_date: date
    description: str
    reference_number: Optional[str] = None
    details: List[JournalDetailBase]

    @model_validator(mode='after')
    def check_balance(self):
        total_debit = sum(detail.debit for detail in self.details)
        total_credit = sum(detail.credit for detail in self.details)
        
        if total_debit != total_credit:
            raise ValueError(f"Jurnal tidak seimbang. Total Debit: {total_debit}, Total Kredit: {total_credit}")
        return self
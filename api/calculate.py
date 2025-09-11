from datetime import date
from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal

# --- Domain models ---
class Party(BaseModel):
    country_code: str = Field(..., min_length=2, max_length=2, description="ISO-3166-1 alpha-2")
    vat_number: Optional[str] = Field(None, description="Für B2B/VIES-Check")

class CalcRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Eingabebetrag (net oder gross)")
    basis: Literal["net", "gross"] = "net"
    rate_type: Literal["standard", "reduced", "super_reduced", "parking", "zero"] = "standard"
    supply_date: date = Field(default_factory=date.today)
    supplier: Party
    customer: Party
    supply_type: Literal["goods", "services"] = "goods"
    b2x: Literal["B2C", "B2B"] = "B2C"
    category_hint: Optional[str] = Field(None, description="z.B. ebooks, hospitality, food")

class CalcResult(BaseModel):
    country_code: str
    applied_rate: float
    net: float
    vat: float
    gross: float
    mechanism: Literal["normal", "reverse_charge", "zero_rated", "out_of_scope"]
    messages: list[str] = []
    vat_check_status: Optional[Literal["validated","unavailable","n/a"]] = None

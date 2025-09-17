# app/routes/rates.py
from datetime import date
from typing import List, Optional, Dict, Literal
from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field

router = APIRouter(prefix="/rates", tags=["rates"])

class ReducedRate(BaseModel):
    rate: float = Field(..., ge=0)
    label: str

class CountryRates(BaseModel):
    country: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2")
    standard_rate: float = Field(..., ge=0)
    reduced_rates: List[ReducedRate] = []
    currency: Literal["EUR", "GBP", "DKK", "SEK", "NOK", "CHF", "PLN", "CZK", "HUF", "RON", "BGN", "HRK"] = "EUR"
    valid_on: date
    source: str = "VATify/static"

# --- Minimaler Datenspeicher (kann später aus einer DB/EU-Quelle gespeist werden) ---
# Struktur erlaubt versions-/datumsabhängige Sätze
_VAT_RATES: Dict[str, Dict[date, Dict]] = {
    "DE": {
        date(2021, 1, 1): {
            "standard_rate": 19.0,
            "reduced_rates": [{"rate": 7.0, "label": "reduced"}, {"rate": 0.0, "label": "zero"}],
            "currency": "EUR",
        }
    },
    "FR": {
        date(2021, 1, 1): {
            "standard_rate": 20.0,
            "reduced_rates": [{"rate": 10.0, "label": "reduced"}, {"rate": 5.5, "label": "reduced2"}],
            "currency": "EUR",
        }
    },
    # weitere Länder hier …
}

def _pick_effective_date(rates_by_date: Dict[date, Dict], wanted: date) -> Optional[date]:
    # nimmt den jüngsten Eintrag <= wanted
    candidates = [d for d in rates_by_date.keys() if d <= wanted]
    return max(candidates) if candidates else None

@router.get("/{country}", response_model=CountryRates)
def get_rates(
    country: str = Path(..., description="ISO-3166-1 Alpha-2, e.. g. DE"),
    date_param: Optional[date] = Query(None, alias="date", description="YYYY-MM-DD; Standard: heute"),
):
    key = country.upper()
    if len(key) != 2 or not key.isalpha():
        raise HTTPException(status_code=400, error="country must be a 2-character ISO Alpha-2 code (e.g. DE).")

    today = date.today()
    wanted = date_param or today

    country_data = _VAT_RATES.get(key)
    if not country_data:
        raise HTTPException(status_code=404, error=f"Unknown Country Key: {key}")

    eff = _pick_effective_date(country_data, wanted)
    if eff is None:
        raise HTTPException(status_code=404, error=f"No rates found for {key} on {wanted.isoformat()}.")

    payload = country_data[eff]
    return CountryRates(
        country=key,
        standard_rate=payload["standard_rate"],
        reduced_rates=[ReducedRate(**r) for r in payload.get("reduced_rates", [])],
        currency=payload.get("currency", "EUR"),
        valid_on=eff,
        source="VATify/static",
    )

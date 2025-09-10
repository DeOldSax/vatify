from datetime import date
import re
from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field

# SOAP client (official EU VIES service is SOAP)
# ⇨ Ergänzungen ganz oben
from datetime import date, datetime
import logging

logger = logging.getLogger("vatify")

def coerce_request_date(value) -> date | None:
    """
    VIES liefert teils:
      - datetime.date
      - datetime.datetime
      - 'YYYY-MM-DD'
      - 'YYYY-MM-DD+HH:MM'  (fehlerhaftes Datumsformat mit Offset)
    Diese Funktion normalisiert robust auf datetime.date.
    """
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        s = value.strip()
        # Abschneiden bekannter Offset-/Zeit-Anteile
        # Beispiele: '2025-09-10+02:00', '2025-09-10Z', '2025-09-10T00:00:00Z'
        # 1) Wenn es wie ein reines Datum beginnt, nimm die ersten 10 Zeichen
        if len(s) >= 10 and s[4] == '-' and s[7] == '-':
            try:
                return date.fromisoformat(s[:10])
            except Exception:
                pass
        # 2) Fallback: Versuche generisch zu parsen
        for sep in ('T', ' ', '+', 'Z'):
            if sep in s:
                try:
                    return datetime.fromisoformat(s.split(sep, 1)[0]).date()
                except Exception:
                    # weiter versuchen
                    pass
        # 3) Letzter Versuch: direkt
        try:
            return date.fromisoformat(s)
        except Exception as e:
            logger.warning(f"Unparseable VIES requestDate: {s!r} ({e})")
            return None
    # Unerwarteter Typ
    logger.warning(f"Unexpected requestDate type: {type(value)} -> {value!r}")
    return None


# --- Config ---
VIES_WSDL = "https://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl"
EU_COUNTRY_CODES = {
    "AT","BE","BG","CY","CZ","DE","DK","EE","EL","ES","FI","FR","HR","HU",
    "IE","IT","LT","LU","LV","MT","NL","PL","PT","RO","SE","SI","SK","XI"
}
# Note: "EL" = Griechenland (nicht GR). "XI" = Nordirland (UK-Teil für EU-USt).

# --- Schemas ---
class ValidateRequest(BaseModel):
    vat_number: Optional[str] = Field(
        None, example="DE123456789",
        description="Komplette USt-ID inkl. Länderpräfix, z. B. 'DE123456789'."
    )
    country_code: Optional[str] = Field(
        None, min_length=2, max_length=2, example="DE",
        description="Optional, wenn 'vat_number' ohne Präfix übergeben wird."
    )
    number: Optional[str] = Field(
        None, example="123456789",
        description="Optional, wenn 'country_code' separat übergeben wird."
    )

class ValidateResponse(BaseModel):
    valid: bool
    country_code: str
    vat_number: str
     # VIES-Datum als Rohstring, ohne Parsing
    vies_request_date_raw: Optional[str] = None
    # Dein UTC-Timestamp für die Prüfung (immer gesetzt)
    checked_at: datetime
    name: Optional[str] = None
    address: Optional[str] = None

# --- Helpers ---
_clean_non_alnum = re.compile(r"[^A-Za-z0-9]")

def normalize_inputs(vat_number: Optional[str], country_code: Optional[str], number: Optional[str]):
    """
    Akzeptiert entweder:
      - vat_number="DE123456789"
      - country_code="DE", number="123456789"
    Normalisiert, prüft Country-Code und entfernt Trennzeichen/Leerzeichen.
    """
    if vat_number:
        raw = _clean_non_alnum.sub("", vat_number).upper()
        if len(raw) < 3:
            raise HTTPException(status_code=400, detail="USt-ID zu kurz.")
        cc = raw[:2]
        num = raw[2:]
    else:
        if not (country_code and number):
            raise HTTPException(
                status_code=400,
                detail="Entweder 'vat_number' ODER ('country_code' UND 'number') angeben."
            )
        cc = _clean_non_alnum.sub("", country_code).upper()
        num = _clean_non_alnum.sub("", number)

    if cc not in EU_COUNTRY_CODES:
        raise HTTPException(status_code=400, detail=f"Ungültiger EU-Ländercode: {cc}")

    if not num or not num.isalnum():
        raise HTTPException(status_code=400, detail="USt-Nummer fehlt oder hat ungültige Zeichen.")
    return cc, num

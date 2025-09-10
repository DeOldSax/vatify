from datetime import date
import re
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

# SOAP client (official EU VIES service is SOAP)
from zeep import Client, Settings
from zeep.transports import Transport
from zeep.exceptions import Fault, TransportError

# ⇨ Ergänzungen ganz oben
from datetime import date, datetime, timezone
import logging

from validate_vat import ValidateRequest, ValidateResponse, normalize_inputs

logger = logging.getLogger("vatify")



# --- Config ---
VIES_WSDL = "https://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl"
EU_COUNTRY_CODES = {
    "AT","BE","BG","CY","CZ","DE","DK","EE","EL","ES","FI","FR","HR","HU",
    "IE","IT","LT","LU","LV","MT","NL","PL","PT","RO","SE","SI","SK","XI"
}
# Note: "EL" = Griechenland (nicht GR). "XI" = Nordirland (UK-Teil für EU-USt).
from routes import rates

# --- FastAPI app ---
app = FastAPI(title="VATify MVP", version="0.1.0")
app.include_router(rates.router)

# Create a single zeep client (thread-safe calls via threadpool)
_transport = Transport(timeout=10)  # seconds
_settings  = Settings(strict=False, raw_response=True)  # <- hier!
_zeep_client = Client(wsdl=VIES_WSDL, transport=_transport, settings=_settings)



def call_vies_check_vat(country_code: str, number: str):
    """
    Ruft VIES checkVat(countryCode, vatNumber) auf.
    Läuft synchron; wird vom Endpoint im Threadpool ausgeführt.
    """
    service = _zeep_client.service
    # VIES gibt Felder: countryCode, vatNumber, requestDate, valid, name, address
    return service.checkVat(countryCode=country_code, vatNumber=number)

def call_vies_check_vat_raw(country_code: str, number: str):
    resp = _zeep_client.service.checkVat(countryCode=country_code, vatNumber=number)
    # raw_response=True => resp.content ist das SOAP-XML (bytes)
    from lxml import etree
    root = etree.fromstring(resp.content)

    def text_of(root: etree._Element, local_name: str):
        """
        Sucht ein Element unabhängig vom Namespace via XPath + local-name().
        Gibt den getrimmten Text des ersten Treffers zurück oder None.
        """
        nodes = root.xpath(f"//*[local-name()='{local_name}']")
        if not nodes:
            return None
        text = nodes[0].text
        return text.strip() if text else None
    
    return {
        "countryCode": text_of(root, "countryCode"),
        "vatNumber":   text_of(root, "vatNumber"),
        "requestDate": text_of(root, "requestDate"),  # Rohstring lassen
        "valid":       (text_of(root, "valid") or "").lower() == "true",
        "name":        text_of(root, "name"),
        "address":     text_of(root, "address"),
    }

# 

# --- Endpoint ---
@app.post("/validate-vat", response_model=ValidateResponse, tags=["vat"])
async def validate_vat(payload: ValidateRequest):
    cc, num = normalize_inputs(payload.vat_number, payload.country_code, payload.number)
    try:
        result = await run_in_threadpool(call_vies_check_vat_raw, cc, num)
        print(result)
    except Fault as e:
        raise HTTPException(status_code=502, detail=f"VIES Fault: {getattr(e, 'message', str(e))}")
    except TransportError:
        raise HTTPException(status_code=503, detail="VIES-Dienst derzeit nicht erreichbar. Bitte später erneut versuchen.")
    except Exception:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unerwarteter Fehler beim VIES-Check.")

    return ValidateResponse(
        valid=bool(result["valid"]),
        country_code=str(result["countryCode"]) or cc,
        vat_number=str(result["vatNumber"]) or num,
        vies_request_date_raw=str(result["requestDate"]),      # einfach Rohstring übernehmen
        checked_at=datetime.now(timezone.utc),                 # dein UTC Timestamp
        name=(str(result["name"]).strip() or None),
        address=(str(result["address"]).strip() or None),
    )

VAT_RATES: Dict[str, Dict[str, Any]] = {
    "DE": {"standard_rate": 19.0, "reduced_rates": [{"rate": 7.0, "label": "reduced"}], "currency": "EUR"},
    "FR": {"standard_rate": 20.0, "reduced_rates": [{"rate": 10.0, "label": "reduced"}, {"rate": 5.5, "label": "reduced2"}], "currency": "EUR"},
    # … weitere Länder
}

@app.get("/rates/{country}")
def get_rates(country: str):
    key = country.upper()
    data = VAT_RATES.get(key)
    if not data:
        raise HTTPException(status_code=404, detail=f"Unknown country: {key}")
    return {"country": key, **data, "source": "EU/VATify"}
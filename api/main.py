import asyncio
from datetime import date
import re
from typing import Any, Dict, Literal, Optional

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

from calculate import CalcRequest, CalcResult, Party
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


@app.get("/rates/{country}")
def get_rates(country: str):
    country = country.upper()

    if country not in EU_COUNTRY_CODES:
        raise HTTPException(status_code=400, detail=f"Invalid country code: {country}")

    with open(f"scripts/data/{country}.json", "r", encoding="utf-8") as f:
        import json
        data = json.load(f)

    return {"country": country, **data, "source": "EU/VATify"}


def get_rate(country_code: str, rate_type: str, supply_date: date, category_hint: Optional[str]) -> float:
    cc = country_code.upper()
    if cc not in EU_COUNTRY_CODES:
        raise HTTPException(status_code=400, detail=f"Invalid country code: {cc}")
    
    with open(f"scripts/data/{cc}.json", "r", encoding="utf-8") as f:
        import json
        data = json.load(f)
   
    found_rate = None
    if category_hint:
        # Suche nach einem reduced_rate-Eintrag mit Kategorie
        for rr in data.get("reduced_rates", []):
            if rr["label"].endswith(f":{category_hint}"):
                found_rate = rr["rate"]
                break
        
    if found_rate:
        return found_rate
    else:
        if rate_type == "standard":
            return data["standard_rate"]
        else:
            raise HTTPException(status_code=404, detail="Rate not found for country/rate_type")

def is_valid_vat(country_code: str, vat_number: Optional[str]) -> bool:
    vatResponse = asyncio.run(validate_vat(payload=ValidateRequest(country_code=country_code, vat_number=vat_number)))
    return vatResponse.valid
    
    """TODO: Replace by VIES SOAP. Für MVP: wenn format vorhanden, true."""
    return bool(vat_number and len(vat_number) >= 8)

def should_reverse_charge(supplier: Party, customer: Party, b2x: str) -> bool:
    """
    Minimal-Logik:
    - B2B
    - innergemeinschaftliche Lieferung/Leistung (verschiedene EU-Länder)
    - gültige USt-IdNr. beim Kunden
    """
    if b2x != "B2B":
        return False
    if supplier.country_code.upper() == customer.country_code.upper():
        return False
    return is_valid_vat(customer.country_code, customer.vat_number)



# --- Endpoint ---
@app.post("/calculate", response_model=CalcResult)
def calculate_vat(payload: CalcRequest):
    # 1) Sonderfall: Reverse Charge
    should_rc = should_reverse_charge(payload.supplier, payload.customer, payload.b2x)
    if should_rc:
        amount = payload.amount
        if payload.basis == "gross":
            # unter RC gibt es keine inländische VAT im Preis; Brutto==Netto
            net = amount
        else:
            net = amount
        return CalcResult(
            country_code=payload.customer.country_code.upper(),
            applied_rate=0.0,
            net=net,
            vat=0.0,
            gross=net,
            mechanism="reverse_charge",
            message="Reverse Charge angewendet; keine USt. berechnet. VAT Nr. des Kunden wurde geprüft.",
        )

    # 2) Normale Besteuerung im Land des Kunden (vereinfachte Fernverkaufs-/B2C-Logik)
    target_country = payload.customer.country_code.upper()

    rate = get_rate(
        country_code=target_country,
        rate_type=payload.rate_type,
        supply_date=payload.supply_date,
        category_hint=payload.category_hint,
    )

    # 3) Rechnen
    if payload.basis == "net":
        net = payload.amount
        vat = round(net * rate, 2)
        gross = round(net + vat, 2)
    else:
        gross = payload.amount
        net = round(gross / (1 + rate), 2)
        vat = round(gross - net, 2)

    mechanism: Literal["normal", "reverse_charge", "zero_rated", "out_of_scope"] = "normal"
    if rate == 0.0:
        mechanism = "zero_rated"

    return CalcResult(
        country_code=target_country,
        applied_rate=rate,
        net=net,
        vat=vat,
        gross=gross,
        mechanism=mechanism,
        message="Reverse nicht Charge angewendet; VAT Nr. des Kunden ist nicht valide.",
    )
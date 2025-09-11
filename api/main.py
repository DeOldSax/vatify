import asyncio
from datetime import date
import re
from typing import Any, Dict, Literal, Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

# SOAP client (official EU VIES service is SOAP)
from zeep import Client, Settings
from zeep.transports import Transport
from zeep.exceptions import Fault, TransportError

# ⇨ Ergänzungen ganz oben
from datetime import date, datetime, timezone
import logging

from deps import check_and_increment_user_quota, get_current_user
from calculate import CalcRequest, CalcResult, Party
from validate_vat import ValidateRequest, ValidateResponse, normalize_inputs

from routers import auth, users, apikeys
from middleware.quota import APIKeyAuthQuotaMiddleware

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
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="VATify MVP", version="0.1.0")
from middleware.csrf import CSRFMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://deine-spa-domain.tld", "http://localhost:5173"],
    allow_credentials=True,            # wichtig für Cookies
    allow_methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],
    allow_headers=["*"]
)
app.add_middleware(CSRFMiddleware)
app.add_middleware(APIKeyAuthQuotaMiddleware, protected_prefixes=["/v1/"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/me", tags=["me"])
app.include_router(apikeys.router, prefix="/apikeys", tags=["api-keys"])

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

def is_valid_vat(country_code: str, vat_number: Optional[str]) -> tuple[bool, str]:
    try:
        resp = asyncio.run(validate_vat(payload=ValidateRequest(country_code=country_code, vat_number=vat_number)))
        return bool(resp.valid), "validated"
    except Exception:
        # konservativ: kein RC, aber deklarieren
        return False, "unavailable"


def should_reverse_charge(supplier: Party, customer: Party, b2x: str) -> tuple[bool, str, list[str]]:
    notes = []
    if b2x != "B2B":
        return False, "n/a", notes
    if supplier.country_code.upper() == customer.country_code.upper():
        return False, "n/a", notes
    if supplier.country_code.upper() not in EU_COUNTRY_CODES or customer.country_code.upper() not in EU_COUNTRY_CODES:
        notes.append("No EU intra-community supply → no reverse charge.")
        return False, "n/a", notes
    valid, status = is_valid_vat(customer.country_code, customer.vat_number)
    if not valid:
        notes.append("Customer VAT number invalid or unavailable → Reverse Charge not applied.")
    return valid, status, notes


async def handle_validate_vat(payload: ValidateRequest) -> ValidateResponse:
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

def handle_get_rates(country: str) -> Dict[str, Any]:
    country = country.upper()

    if country not in EU_COUNTRY_CODES:
        raise HTTPException(status_code=400, detail=f"Invalid country code: {country}")

    with open(f"scripts/data/{country}.json", "r", encoding="utf-8") as f:
        import json
        data = json.load(f)

    return {"country": country, **data, "source": "EU/VATify"}


def handle_calculate_vat(payload: CalcRequest) -> CalcResult:
    messages: list[str] = []
    should_rc, vat_status, rc_notes = should_reverse_charge(payload.supplier, payload.customer, payload.b2x)
    messages += rc_notes

    if should_rc:
        net = payload.amount  # unabhängig von basis, unter RC gibt's keine inländische VAT
        return CalcResult(
            country_code=payload.customer.country_code.upper(),
            applied_rate=0.0,
            net=net,
            vat=0.0,
            gross=net,
            mechanism="reverse_charge",
            messages=messages + ["Reverse Charge applied; invoice net without VAT."],
            vat_check_status=vat_status,
        )

    target_country = payload.customer.country_code.upper()
    rate = get_rate(
        country_code=target_country,
        rate_type=payload.rate_type,
        supply_date=payload.supply_date,
        category_hint=payload.category_hint,
    )

    if payload.basis == "net":
        net = round(payload.amount, 2)
        vat = round(net * rate, 2)
        gross = round(net + vat, 2)
    else:
        gross = round(payload.amount, 2)
        net = round(gross / (1 + rate), 2)
        vat = round(gross - net, 2)

    mechanism: Literal["normal","reverse_charge","zero_rated","out_of_scope"] = "normal"
    if rate == 0.0:
        mechanism = "zero_rated"

    # Wenn B2B aber kein RC möglich war, Hinweise mitgeben
    if payload.b2x == "B2B" and payload.supplier.country_code.upper() != payload.customer.country_code.upper():
        messages.append("No Reverse Charge applied; VAT charged normally.")

    return CalcResult(
        country_code=target_country,
        applied_rate=rate,
        net=net,
        vat=vat,
        gross=gross,
        mechanism=mechanism,
        messages=messages,
        vat_check_status=vat_status if vat_status != "n/a" else None,
    )

# Endpoints - all secured by middleware

# API-Endpunkte (API-Key-basiert)
@app.post("/v1/calculate", response_model=CalcResult)
def calculate_vat(payload: CalcRequest):
    return handle_calculate_vat(payload)

@app.post("/v1/validate-vat", response_model=ValidateResponse, tags=["vat"])
async def validate_vat(payload: ValidateRequest):
    return await handle_validate_vat(payload)

@app.get("/v1/rates/{country}")
def get_rates(country: str):
    return handle_get_rates(country)

# --- App-Endpunkte (auth + user-basiert) ---
@app.post("/app/calculate", response_model=CalcResult)
async def endpoint_a_app(payload: dict, user=Depends(get_current_user), _=Depends(check_and_increment_user_quota)):
    return  handle_calculate_vat(payload)

@app.post("/app/validate-vat", response_model=ValidateResponse)
async def endpoint_b_app(payload: dict, user=Depends(get_current_user), _=Depends(check_and_increment_user_quota)):
    return await handle_validate_vat(payload)

@app.post("/app/rates/{country}")
async def endpoint_c_app(country: str, user=Depends(get_current_user), _=Depends(check_and_increment_user_quota)):
    return await handle_get_rates(country)
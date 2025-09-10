# pip install zeep requests lxml
from datetime import date, datetime
from typing import Dict, Any, List, Optional
import requests
from lxml import etree
from zeep import Client, Settings
from zeep.transports import Transport

WSDL_URL = "https://ec.europa.eu/taxation_customs/tedb/ws/VatRetrievalService.wsdl"

def _safe_iso_date_str(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    s = s.strip()
    if "T" in s:
        s = s.split("T", 1)[0]
    if len(s) >= 11 and s[10] in ("Z", "+", "-"):
        s = s[:10]
    return s if len(s) >= 10 else None

def _date_key(s: Optional[str]) -> date:
    try:
        return date.fromisoformat(s) if s else date.min
    except Exception:
        return date.min

def build_client() -> Client:
    settings = Settings(strict=True, xml_huge_tree=True)
    transport = Transport(session=requests.Session(), timeout=30)
    return Client(wsdl=WSDL_URL, settings=settings, transport=transport)

def retrieve_vat_rates_raw(country_iso: str,
                           situation_on: Optional[date] = None,
                           period_from: Optional[date] = None,
                           period_to: Optional[date] = None) -> List[Dict[str, Any]]:
    client = build_client()
    memberStates = {"isoCode": [country_iso.upper()]}

    with client.settings(raw_response=True):
        if period_from and period_to:
            resp = client.service.retrieveVatRates(
                memberStates=memberStates,
                from_=period_from.isoformat(),
                to_=period_to.isoformat(),
            )
        else:
            resp = client.service.retrieveVatRates(
                memberStates=memberStates,
                situationOn=(situation_on or date.today()).isoformat(),
            )

    root = etree.fromstring(resp.content)

    # Fault detection
    fault = root.xpath("//*[local-name()='Fault']/*[local-name()='faultstring']/text()")
    if fault:
        raise RuntimeError(f"TEDB SOAP Fault: {fault[0]}")

    # Accept both singular and plural element names
    item_nodes = root.xpath("//*[local-name()='vatRateResult'] | //*[local-name()='vatRateResults']")

    results = []
    for it in item_nodes:
        def find_txt(node, name):
            el = node.xpath(f"./*[local-name()='{name}']")
            return el[0].text.strip() if el and el[0].text else None

        member_state = find_txt(it, "memberState")
        typ = find_txt(it, "type")
        situation_on_txt = _safe_iso_date_str(find_txt(it, "situationOn"))

        # rate
        rate_node = it.xpath("./*[local-name()='rate']")
        rate_value = None
        rate_kind = None
        if rate_node:
            rate_value_txt = (rate_node[0].xpath("./*[local-name()='value']/text()") or [None])[0]
            rate_kind = (rate_node[0].xpath("./*[local-name()='type']/text()") or [None])[0]
            if rate_value_txt:
                try:
                    rate_value = float(rate_value_txt.replace(",", "."))
                except ValueError:
                    rate_value = None

        # category (optional)
        cat_node = it.xpath("./*[local-name()='category']")
        cat_id = (cat_node[0].xpath("./*[local-name()='identifier']/text()") or [None])[0] if cat_node else None

        results.append({
            "memberState": member_state,
            "type": typ,  # 'STANDARD' | 'REDUCED'
            "situationOn": situation_on_txt,  # normalized 'YYYY-MM-DD'
            "rate": {"value": rate_value, "type": rate_kind},  # rate.type like 'DEFAULT', 'EXEMPTED', ...
            "categoryId": cat_id,
        })

    return results

# ---------- Mapper auf dein API-JSON (/rates/{country}) ----------
def map_results_to_api_json(country_iso: str,
                            results: List[Dict[str, Any]],
                            default_valid_on: Optional[date] = None,
                            currency: str = "EUR") -> Dict[str, Any]:
    # Jüngsten STANDARD-Eintrag mit numerischem Wert nehmen
    std_candidates = [
        r for r in results
        if r.get("type") == "STANDARD" and isinstance(r.get("rate", {}).get("value"), (int, float))
    ]
    std = max(std_candidates, key=lambda r: _date_key(r.get("situationOn"))) if std_candidates else None

    # REDUCED-Einträge (inkl. EXEMPTED/0.0) sammeln
    reduced_rates: List[Dict[str, Any]] = []
    for r in results:
        if r.get("type") != "REDUCED":
            continue
        val = r.get("rate", {}).get("value")
        if val is None:
            continue
        label = (r.get("rate", {}).get("type") or "REDUCED_RATE").lower()
        # Kategorie optional anhängen, damit unterschiedliche reduzierte Sätze unterscheidbar sind
        cat_id = r.get("categoryId")
        if cat_id:
            label = f"{label}:{cat_id}"
        reduced_rates.append({"rate": float(val), "label": label})

    # Deduplizieren + sortieren
    seen = set()
    unique_reduced = []
    for rr in reduced_rates:
        key = (rr["rate"], rr["label"])
        if key in seen:
            continue
        seen.add(key)
        unique_reduced.append(rr)
    unique_reduced.sort(key=lambda x: (x["rate"], x["label"]))

    # valid_on wählen
    valid_on = (std.get("situationOn") if std else None) \
               or (default_valid_on.isoformat() if default_valid_on else date.today().isoformat())

    return {
        "country": country_iso.upper(),
        "standard_rate": float(std["rate"]["value"]) if std else None,
        "reduced_rates": unique_reduced,
        "currency": currency,
        "valid_on": valid_on,
        "source": "TEDB SOAP VatRetrievalService",
    }

# ---------- Beispielnutzung ----------
if __name__ == "__main__":
    EU_COUNTRY_CODES = {
        "AT","BE","BG","CY","CZ","DE","DK","EE","EL","ES","FI","FR","HR","HU",
        "IE","IT","LT","LU","LV","MT","NL","PL","PT","RO","SE","SI","SK","XI"
    }
    for cc in sorted(EU_COUNTRY_CODES):
        print(f"--- {cc} ---")
        raw = retrieve_vat_rates_raw(cc)
        api_json = map_results_to_api_json(cc, raw)

        with open(f"data/{cc}.json", "w", encoding="utf-8") as f:
            import json
            json.dump(api_json, f, ensure_ascii=False, indent=2)

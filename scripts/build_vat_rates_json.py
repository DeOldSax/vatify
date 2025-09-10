# scripts/build_vat_rates_json.py
import json, requests
from bs4 import BeautifulSoup
from datetime import date

URL = "https://europa.eu/youreurope/business/taxation/vat/vat-rules-rates/index_en.htm"

def scrape():
    html = requests.get(URL, timeout=30).text
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    rows = table.find_all("tr")[1:]  # skip header

    rates = []
    for tr in rows:
        tds = [td.get_text(strip=True) for td in tr.find_all(["td","th"])]
        if len(tds) < 5:
            continue
        # Columns: Country code, Member State, Standard, Reduced, Super-reduced, Parking (variiert je nach Layout)
        code = tds[0]
        print(tds)
        standard = tds[2].replace("%","").replace(",",".")
        reduced = tds[3]
        super_reduced = (tds[4] if len(tds) > 4 else "").strip()
        parking = (tds[5] if len(tds) > 5 else "").strip()

        def parse_rates(cell, labels_hint):
            out = []
            if not cell or cell in ("-","–"):
                return out
            # Beispiele wie "5.5 / 10" → mehrere Raten
            parts = [p.strip() for p in cell.replace("%","").replace(",",".").split("/")]
            for i, p in enumerate(parts):
                try:
                    out.append({"rate": float(p), "label": labels_hint[i] if i < len(labels_hint) else "reduced"})
                except ValueError:
                    pass
            return out

        reduced_rates = parse_rates(reduced, ["reduced","reduced2","reduced3"])
        if super_reduced not in ("","-","–"):
            try:
                reduced_rates.append({"rate": float(super_reduced.replace("%","").replace(",", ".")), "label": "super_reduced"})
            except ValueError:
                pass
        if parking not in ("","-","–"):
            try:
                reduced_rates.append({"rate": float(parking.replace("%","").replace(",", ".")), "label": "parking"})
            except ValueError:
                pass
        print(standard)
        rates.append({
            "country": code,
            "currency": "EUR",
            "standard_rate": float(standard),
            "reduced_rates": reduced_rates,
            "valid_from": None,
            "notes": []
        })

    return {
        "version": date.today().isoformat(),
        "source": "EU Commission (Youreurope table)",
        "rates": rates
    }

if __name__ == "__main__":
    data = scrape()
    with open("data/vat_rates.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Wrote data/vat_rates.json")

curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.0,
    "basis": "net",
    "rate_type": "standard",
    "supplier": {"country_code": "DE"},
    "customer": {"country_code": "FR"},
    "b2x": "B2C",
    "supply_type": "goods"
  }' | jq .

curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.0,
    "basis": "net",
    "rate_type": "standard",
    "supplier": {"country_code": "DE"},
    "customer": {"country_code": "FR", "vat_number": "FR12345678901"},
    "b2x": "B2B",
    "supply_type": "services"
  }'  | jq .

curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.0,
    "basis": "net",
    "rate_type": "standard",
    "supplier": {"country_code": "DE"},
    "customer": {"country_code": "IT", "vat_number": "IT00743110157"},
    "b2x": "B2B",
    "supply_type": "services"
  }'  | jq .



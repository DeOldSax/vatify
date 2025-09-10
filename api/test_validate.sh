# 1) Komplette USt-ID
curl -s http://localhost:8000/validate-vat \
  -H "Content-Type: application/json" \
  -d '{"vat_number":"IT00743110157"}' | jq

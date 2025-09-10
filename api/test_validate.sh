# 1) Komplette USt-ID
curl -s http://localhost:8000/validate-vat \
  -H "Content-Type: application/json" \
  -d '{"vat_number":"DE811907980"}' | jq

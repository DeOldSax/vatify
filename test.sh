curl -s https://api.vatifytax.app/v1/validate-vat \
  -H "Authorization: Bearer vk_live_whI6VGS-bmhat1_-evUUnjtKvX3LxB0BOuwx63QrtPU" \
  -H "Content-Type: application/json" \
  -d '{"vat_number":"DE811907980"}' | jq

curl -s https://api.vatifytax.app/v1/calculate \
  -H "Authorization: Bearer vk_live_whI6VGS-bmhat1_-evUUnjtKvX3LxB0BOuwx63QrtPU" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.0,
    "basis": "net",
    "rate_type": "reduced",
    "supply_date": "2025-09-12",
    "supplier": { "country_code": "DE", "vat_number": "DE123456789" },
    "customer": { "country_code": "FR", "vat_number": "FR12345678901" },
    "supply_type": "services",
    "b2x": "B2B",
    "category_hint": "ACCOMMODATION"
  }' | jq


 curl -s https://api.vatifytax.app/v1/rates/DE \
  -H "Authorization: Bearer vk_live_whI6VGS-bmhat1_-evUUnjtKvX3LxB0BOuwx63QrtPU" \
  -H "Content-Type: application/json" | jq

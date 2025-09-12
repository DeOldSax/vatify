curl -vk https://localhost:8000/v1/validate-vat \
  -H "Authorization: Bearer vk_live_mjFwhbNOQgWSPhjnKZLrIQHgfYEShOQ2TZRpB5Dxf5c" \
  -H "Content-Type: application/json" \
  -d '{"vat_number":"DE811907980"}' | jq

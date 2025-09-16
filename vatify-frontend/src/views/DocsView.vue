<template>
  <div class="grid gap-6">
    <!-- HEADER / INTRO -->
    <section class="rounded-2xl shadow-card border border-gray-200 bg-white p-6">
      <h2 class="text-xl font-bold text-slate-900">Vatify API Documentation</h2>
      <p class="mt-2 text-slate-600">
        Base URL: <code class="px-1 py-0.5 rounded bg-slate-100 text-slate-800">{{ baseUrl }}</code>
      </p>
      <p class="mt-2 text-slate-600">
        Authentication: <span class="font-medium">Bearer token</span> in the <code>Authorization</code> header.
      </p>
      <div class="mt-3 text-xs text-slate-500">
        Example header: <code>Authorization: Bearer &lt;YOUR_API_KEY&gt;</code>
      </div>
    </section>

    <!-- VALIDATE -->
    <section class="rounded-2xl shadow-card border border-gray-200 bg-white p-6">
      <div class="mb-2 flex items-center justify-between">
        <h3 class="text-lg font-semibold text-slate-800">Validate VAT</h3>
      </div>

      <div class="text-sm text-slate-600 space-y-4">
        <div>
          <div class="font-medium text-slate-700">Endpoint</div>
            <Snippet :code="validate_vat_endpoint"></Snippet>
        </div>

        <div>
          <div class="font-medium text-slate-700">Headers</div>
           <Snippet code="Authorization: Bearer &lt;API_KEY&gt;
Content-Type: application/json"></Snippet>
        </div>

        <div>
          <div class="font-medium text-slate-700">Request Body</div>
           <Snippet code="{'vat_number': 'IT00743110157'}"></Snippet>
          <p class="mt-2 text-xs text-slate-500">
            <span class="font-medium">vat_number</span> — string, includes country prefix (ISO-2) like <code>DE</code>, <code>FR</code>, <code>IT</code>.
          </p>
        </div>
        

        <div>
          <div class="font-medium text-slate-700">Response (200)</div>
          <Snippet :code="validate_vat_response"></Snippet>
          

          <details class="mt-2">
            <summary class="cursor-pointer text-slate-700 font-medium">Field reference (possible values)</summary>
            <div class="mt-2 text-xs leading-6 text-slate-600 space-y-1">
              <div><span class="font-medium">valid</span>: boolean — VAT is syntactically and registry-valid. Checked by VIES.</div>
              <div><span class="font-medium">country_code</span>: ISO-3166-1 alpha-2 (e.g., DE, FR, IT, ES, NL, BE, AT, PL, SE, DK, IE, PT, FI, CZ, SK, HU, RO, BG, SI, HR, LT, LV, EE, LU, CY, MT, GR).</div>
              <div><span class="font-medium">vat_number</span>: string — Canonical representation without country prefix.</div>
              <div><span class="font-medium">vies_request_date_raw</span>: optional, Date set by VIES.</div>
              <div><span class="font-medium">checked_at</span>: RFC3339 datetime (UTC).</div>
              <div><span class="font-medium">name</span>: string | null (optional when VIES doesn’t return the name).</div>
              <div><span class="font-medium">address</span>: string | null (optional / may be empty).</div>
            </div>
          </details>
        </div>

        <div>
          <div class="font-medium text-slate-700">Errors</div>
          <Snippet code='// 400 Bad Request
{ "detail": Detailed Description }

// 401 Unauthorized
{ "error": Error Message }

// 429 Too Many Requests
{ "error": "Free Monthly quota exceeded" }

// 500 Unexpected Error from VIES
{ "error": "Unexpected Error while checking with VIES." }

// 502 VIES FAULT
{ "error": "VIES Fault: Error Message" }

// 503 Service Unavailable
{ "error": "VIES temporarily unavailable." }'></Snippet>
        </div>

        <div>
          <div class="font-medium text-slate-700">Example cURL</div>
          <Snippet :code=validate_vat_example_curl></Snippet>
        </div>
      </div>
    </section>

    <!-- CALCULATE -->
    <section class="rounded-2xl shadow-card border border-gray-200 bg-white p-6">
      <div class="mb-2 flex items-center justify-between">
        <h3 class="text-lg font-semibold text-slate-800">Calculate VAT</h3>
      </div>

      <div class="text-sm text-slate-600 space-y-4">
        <div>
          <div class="font-medium text-slate-700">Endpoint</div>
          <pre class="mt-1 bg-slate-50 border rounded p-3 overflow-x-auto"><code>POST {{ baseUrl }}/v1/calculate</code></pre>
        </div>

        <div>
          <div class="font-medium text-slate-700">Headers</div>
          <pre class="mt-1 bg-slate-50 border rounded p-3 overflow-x-auto"><code>Authorization: Bearer &lt;API_KEY&gt;
Content-Type: application/json</code></pre>
        </div>

        <div>
          <div class="font-medium text-slate-700">Request Body</div>
          <pre class="mt-1 bg-slate-50 border rounded p-3 overflow-x-auto"><code>{
  "country_code": "DE",
  "rate_type": "standard",
  "supply_date": "2025-09-16",
  "amount_type": "net",
  "amount": 100.00,
  "currency": "EUR",
  "b2b": true,
  "reverse_charge": false,
  "origin_country": "DE",
  "service_type": "digital_services"
}</code></pre>
          <details class="mt-2">
            <summary class="cursor-pointer text-slate-700 font-medium">Field reference & enums</summary>
            <div class="mt-2 text-xs leading-6 text-slate-600 space-y-1">
              <div><span class="font-medium">country_code</span>: ISO-2; destination country for VAT.</div>
              <div><span class="font-medium">rate_type</span>: one of <code>standard</code>, <code>reduced</code>, <code>super_reduced</code>, <code>zero</code>, <code>parking</code> (availability varies per country).</div>
              <div><span class="font-medium">supply_date</span>: YYYY-MM-DD — used for historic rate changes.</div>
              <div><span class="font-medium">amount_type</span>: <code>net</code> | <code>gross</code>.</div>
              <div><span class="font-medium">amount</span>: number — base amount in <span class="font-medium">currency</span>.</div>
              <div><span class="font-medium">currency</span>: ISO-4217 (default <code>EUR</code>).</div>
              <div><span class="font-medium">b2b</span>: boolean — affects rules (e.g., place of supply).</div>
              <div><span class="font-medium">reverse_charge</span>: boolean — if true, VAT due by customer (result VAT 0 and rule explanation).</div>
              <div><span class="font-medium">origin_country</span>: ISO-2 (optional; for intra-EU goods rules).</div>
              <div><span class="font-medium">service_type</span>: string — e.g., <code>digital_services</code>, <code>telecom</code>, <code>saas</code>, <code>goods</code> (optional, clarifies rule set).</div>
            </div>
          </details>
        </div>

        <div>
          <div class="font-medium text-slate-700">Response (200)</div>
          <pre class="mt-1 bg-slate-50 border rounded p-3 overflow-x-auto"><code>{
  "country_code": "DE",
  "rate": 19.0,
  "rate_type": "standard",
  "rate_label": "Standard rate",
  "taxable_amount": 100.00,
  "vat_amount": 19.00,
  "total_amount": 119.00,
  "currency": "EUR",
  "rule_applied": "standard_domestic",
  "reverse_charge": false,
  "notes": "Standard domestic VAT applied for B2B supply.",
  "effective_from": "2007-01-01",
  "effective_to": null,
  "meta": { "request_id": "req_01J...ABC" }
}</code></pre>

          <details class="mt-2">
            <summary class="cursor-pointer text-slate-700 font-medium">Field reference</summary>
            <div class="mt-2 text-xs leading-6 text-slate-600 space-y-1">
              <div><span class="font-medium">rate</span>: number (percent).</div>
              <div><span class="font-medium">rate_type</span> / <span class="font-medium">rate_label</span>: selected rate.</div>
              <div><span class="font-medium">taxable_amount</span>, <span class="font-medium">vat_amount</span>, <span class="font-medium">total_amount</span>: numbers in response <span class="font-medium">currency</span>.</div>
              <div><span class="font-medium">rule_applied</span>: string — e.g., <code>reverse_charge</code>, <code>standard_domestic</code>, <code>intra_eu_b2b</code>, <code>distance_sale</code>, <code>digital_moss</code> (adjust to your rules).</div>
              <div><span class="font-medium">effective_from</span>/<span class="font-medium">effective_to</span>: rate validity window.</div>
            </div>
          </details>
        </div>

        <div>
          <div class="font-medium text-slate-700">Errors</div>
          <pre class="mt-1 bg-slate-50 border rounded p-3 overflow-x-auto"><code>// 400 Bad Request
{ "error": "unsupported_rate_type", "message": "Rate type not available in country." }

// 422 Unprocessable Entity
{ "error": "validation_error", "message": "amount must be > 0" }</code></pre>
        </div>

        <div>
          <div class="font-medium text-slate-700">Example cURL</div>
          <pre class="mt-1 bg-slate-50 border rounded p-3 overflow-x-auto"><code>curl -s {{ baseUrl }}/v1/calculate \
  -H "Authorization: Bearer {{ exampleKey }}" \
  -H "Content-Type: application/json" \
  -d '{
    "country_code":"DE",
    "rate_type":"standard",
    "supply_date":"2025-09-16",
    "amount_type":"net",
    "amount":100.0,
    "currency":"EUR",
    "b2b":true,
    "reverse_charge":false
  }'</code></pre>
        </div>
      </div>
    </section>

    <!-- RATES -->
    <section class="rounded-2xl shadow-card border border-gray-200 bg-white p-6">
      <div class="mb-2 flex items-center justify-between">
        <h3 class="text-lg font-semibold text-slate-800">Rates</h3>
      </div>

      <div class="text-sm text-slate-600 space-y-4">
        <div>
          <div class="font-medium text-slate-700">Endpoint</div>
          <pre class="mt-1 bg-slate-50 border rounded p-3 overflow-x-auto"><code>GET {{ baseUrl }}/v1/rates/{country_code}</code></pre>
          <p class="mt-2 text-xs text-slate-500">Path param <code>country_code</code> is ISO-2 (e.g., <code>DE</code>).</p>
        </div>

        <div>
          <div class="font-medium text-slate-700">Headers</div>
          <pre class="mt-1 bg-slate-50 border rounded p-3 overflow-x-auto"><code>Authorization: Bearer &lt;API_KEY&gt;</code></pre>
        </div>

        <div>
          <div class="font-medium text-slate-700">Response (200)</div>
          <pre class="mt-1 bg-slate-50 border rounded p-3 overflow-x-auto"><code>{
  "country_code": "DE",
  "currency": "EUR",
  "rates": [
    { "type": "standard", "rate": 19.0, "label": "Standard", "effective_from": "2007-01-01", "effective_to": null },
    { "type": "reduced", "rate": 7.0, "label": "Reduced", "effective_from": "2007-01-01", "effective_to": null },
    { "type": "zero", "rate": 0.0, "label": "Zero", "effective_from": null, "effective_to": null }
  ],
  "meta": { "request_id": "req_01J...RATES" }
}</code></pre>

          <details class="mt-2">
            <summary class="cursor-pointer text-slate-700 font-medium">Field reference & enums</summary>
            <div class="mt-2 text-xs leading-6 text-slate-600 space-y-1">
              <div><span class="font-medium">rates[].type</span>: <code>standard</code> | <code>reduced</code> | <code>super_reduced</code> | <code>zero</code> | <code>parking</code> (subset depends on country).</div>
              <div><span class="font-medium">rates[].rate</span>: number (percent).</div>
              <div><span class="font-medium">effective_from</span>/<span class="font-medium">effective_to</span>: date strings or null.</div>
            </div>
          </details>
        </div>

        <div>
          <div class="font-medium text-slate-700">Errors</div>
          <pre class="mt-1 bg-slate-50 border rounded p-3 overflow-x-auto"><code>// 404 Not Found
{ "error": "country_not_supported", "message": "No rates for country_code=XX" }</code></pre>
        </div>

        <div>
          <div class="font-medium text-slate-700">Example cURL</div>
          <pre class="mt-1 bg-slate-50 border rounded p-3 overflow-x-auto"><code>curl -s {{ baseUrl }}/v1/rates/DE \
  -H "Authorization: Bearer {{ exampleKey }}"</code></pre>
        </div>
      </div>
    </section>

    <!-- GENERAL NOTES -->
    <section class="rounded-2xl shadow-card border border-gray-200 bg-white p-6">
      <h4 class="text-base font-semibold text-slate-800">General</h4>
      <ul class="mt-2 list-disc pl-5 text-sm text-slate-600 space-y-1">
        <li>All responses are JSON. Datetimes are RFC3339 (UTC).</li>
        <li>Idempotency: reads are idempotent; calculations are deterministic for given inputs.</li>
        <li>Rate limits: per-plan quotas; 429 returned when exceeded.</li>
        <li>Error schema: <code>{ "error": string, "message": string, "details"?: object }</code>.</li>
      </ul>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSession } from '@/composables/useSession'
import Snippet from '@/components/Snippet.vue'

// Adjust if you expose a different env var in your app:
const baseUrl = import.meta.env.VITE_API_BASE_URL || 'https://api.vatifytax.app'
const { user } = useSession()

// Show a masked example key if user is logged in (purely cosmetic for docs)
const exampleKey = computed(() => {
  const raw = (user?.value as any)?.apiKey || 'sk_live_xxx'
  return raw.length > 10 ? raw.slice(0, 6) + '…' + raw.slice(-4) : raw
})

const validate_vat_endpoint = `${baseUrl}/v1/validate-vat`

const validate_vat_response = `{
  "valid": true,
  "country_code": "IT",
  "vat_number": "00743110157",
  "vies_request_date_raw": "2025-09-16+02:00",
  "checked_at": "2025-09-16T17:06:38.508986Z",
  "name": "MOTOROLA SOLUTIONS ITALIA SRL",
  "address": "LARGO FRANCESCO RICHINI 6 20122 MILANO MI"
}`

const validate_vat_example_curl = `curl -s ${validate_vat_endpoint}
  -H "Authorization: Bearer ${exampleKey}"
  -H "Content-Type: application/json"
  -d '{"vat_number":"DE811907980"}'`

</script>

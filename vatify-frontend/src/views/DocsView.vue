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
            <span class="font-medium">vat_number</span> — string, includes country prefix (ISO-2) like   <code>AT</code>, <code>BE</code>, <code>BG</code>, <code>CY</code>, <code>CZ</code>, <code>DE</code>, <code>DK</code>, <code>EE</code>, <code>EL</code>, <code>ES</code>, <code>FI</code>, <code>FR</code>, <code>HR</code>, <code>HU</code>,
        <code>IE</code>, <code>IT</code>, <code>LT</code>, <code>LU</code>, <code>LV</code>, <code>MT</code>, <code>NL</code>, <code>PL</code>, <code>PT</code>, <code>RO</code>, <code>SE</code>, <code>SI</code>, <code>SK</code>, <code>XI</code> like <code>DE</code>, <code>FR</code>, <code>IT</code>.
          </p>
        </div>
        

        <div>
          <div class="font-medium text-slate-700">Response (200)</div>
          <Snippet :code="validate_vat_response"></Snippet>
          

          <details class="mt-2">
            <summary class="cursor-pointer text-slate-700 font-medium">Field reference (possible values)</summary>
            <div class="mt-2 text-xs leading-6 text-slate-600 space-y-1">
              <div><span class="font-medium">valid</span>: boolean — VAT is syntactically and registry-valid. Checked by VIES.</div>
              <div><span class="font-medium">country_code</span>: ISO-3166-1 alpha-2 (e.g.,   <code>AT</code>, <code>BE</code>, <code>BG</code>, <code>CY</code>, <code>CZ</code>, <code>DE</code>, <code>DK</code>, <code>EE</code>, <code>EL</code>, <code>ES</code>, <code>FI</code>, <code>FR</code>, <code>HR</code>, <code>HU</code>,
        <code>IE</code>, <code>IT</code>, <code>LT</code>, <code>LU</code>, <code>LV</code>, <code>MT</code>, <code>NL</code>, <code>PL</code>, <code>PT</code>, <code>RO</code>, <code>SE</code>, <code>SI</code>, <code>SK</code>, <code>XI</code> like <code>DE</code>, <code>FR</code>, <code>IT</code>.
              )</div>
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
{ "error": Detailed Description }

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
          <Snippet :code="calculate_endpoint"></Snippet>
        </div>

        <div>
          <div class="font-medium text-slate-700">Headers</div>
          <Snippet :code="calculate_headers"></Snippet>
        </div>

        <div>
          <div class="font-medium text-slate-700">Request Body</div>
          <Snippet :code="calculate_request_example"></Snippet>
          
          <details class="mt-2">
  <summary class="cursor-pointer text-slate-700 font-medium">Field reference & enums</summary>
  <div class="mt-2 text-xs leading-6 text-slate-600 space-y-1">
    <div><span class="font-medium">amount</span>: number — base amount in request currency.</div>
    <div><span class="font-medium">basis</span>: <code>net</code> | <code>gross</code> — whether <code>amount</code> is before or after VAT.</div>
    <div>
      <span class="font-medium">rate_type</span>: one of 
      <code>standard</code>, <code>reduced</code>, <code>super_reduced</code>, <code>zero</code>, <code>parking</code> 
      (availability varies by country).
    </div>
    <div><span class="font-medium">supply_date</span>: YYYY-MM-DD — used to apply historic or future rate changes.</div>

    <div>
      <span class="font-medium">supplier</span>: object with supplier details:
      <ul class="list-disc ml-5">
        <li><span class="font-medium">country_code</span>: ISO-2 country code.</li>
        <li><span class="font-medium">vat_number</span>: optional VAT ID string.</li>
      </ul>
    </div>

    <div>
      <span class="font-medium">customer</span>: object with customer details:
      <ul class="list-disc ml-5">
        <li><span class="font-medium">country_code</span>: ISO-2 country code.</li>
        <li><span class="font-medium">vat_number</span>: optional VAT ID string.</li>
      </ul>
    </div>

    <div><span class="font-medium">supply_type</span>: string — e.g. <code>goods</code>, <code>services</code>, <code>digital</code> (determines rule set).</div>
    <div><span class="font-medium">b2x</span>: <code>B2B</code> | <code>B2C</code> — defines business/customer relation.</div>
    <div><span class="font-medium">category_hint</span>: optional string to refine rate selection (e.g. <code>ACCOMMODATION</code>, <code>CULTURAL_EVENTS</code>).</div>
  </div>
</details>

        </div>

        <div>
  <div class="font-medium text-slate-700">Response (200)</div>
  <Snippet :code="calculate_response_example"></Snippet>

  <details class="mt-2">
    <summary class="cursor-pointer text-slate-700 font-medium">Field reference</summary>
    <div class="mt-2 text-xs leading-6 text-slate-600 space-y-1">
      <div><span class="font-medium">country_code</span>: ISO 2-letter country code used for the calculation (e.g. <code>FR</code>).</div>
      <div><span class="font-medium">applied_rate</span>: number (percent) actually applied to the calculation (e.g. <code>10.0</code>).</div>

      <div><span class="font-medium">net</span>: number — taxable amount before VAT.</div>
      <div><span class="font-medium">vat</span>: number — VAT amount charged.</div>
      <div><span class="font-medium">gross</span>: number — total amount (net + vat).</div>

      <div>
        <span class="font-medium">mechanism</span>: string indicating the tax mechanism applied.<br>
        Possible values include e.g. <code>normal</code>, <code>reverse_charge</code>, <code>intra_eu_b2b</code>, <code>exempt</code> (varies by rule set).
      </div>

      <div>
        <span class="font-medium">messages[]</span>: array of human-readable notes explaining decisions or checks performed
        (e.g. validation results, why reverse charge was/wasn’t applied).
      </div>

      <div>
        <span class="font-medium">vat_check_status</span>: string summarizing VAT ID verification result, if performed.<br>
        Examples: <code>validated</code>, <code>invalid</code>, <code>unknown</code>, <code>not_provided</code>.
      </div>
    </div>
  </details>
</div>


        <div>
          <div class="font-medium text-slate-700">Errors</div>
          <Snippet code='// 400 Bad Request
{ "error": "Error Message" }

// 422 Unprocessable Entity
{ "error": "Error Message" }'></Snippet>
        </div>

        <div>
          <div class="font-medium text-slate-700">Example cURL</div>
          <Snippet :code="calculate_curl_example"></Snippet>
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
          <Snippet :code="`${baseUrl}/v1/rates/{country_code}`"></Snippet>
          <p class="mt-2 text-xs text-slate-500">Path param <code>country_code</code> is ISO-2 (e.g.,  <code>AT</code>, <code>BE</code>, <code>BG</code>, <code>CY</code>, <code>CZ</code>, <code>DE</code>, <code>DK</code>, <code>EE</code>, <code>EL</code>, <code>ES</code>, <code>FI</code>, <code>FR</code>, <code>HR</code>, <code>HU</code>,
        <code>IE</code>, <code>IT</code>, <code>LT</code>, <code>LU</code>, <code>LV</code>, <code>MT</code>, <code>NL</code>, <code>PL</code>, <code>PT</code>, <code>RO</code>, <code>SE</code>, <code>SI</code>, <code>SK</code>, <code>XI</code> like <code>DE</code>, <code>FR</code>, <code>IT</code>.
          )</p>
        </div>

        <div>
          <div class="font-medium text-slate-700">Headers</div>
          <Snippet code="Authorization: Bearer <API_KEY>" />
        </div>

        <div>
          <div class="font-medium text-slate-700">Response (200)</div>

          <Snippet :code="rates_api_response"></Snippet>

         <details class="mt-2">
  <summary class="cursor-pointer text-slate-700 font-medium">Field reference & enums</summary>
  <div class="mt-2 text-xs leading-6 text-slate-600 space-y-1">
    <div><span class="font-medium">country</span>: ISO 2-letter code (e.g.  <code>AT</code>, <code>BE</code>, <code>BG</code>, <code>CY</code>, <code>CZ</code>, <code>DE</code>, <code>DK</code>, <code>EE</code>, <code>EL</code>, <code>ES</code>, <code>FI</code>, <code>FR</code>, <code>HR</code>, <code>HU</code>,
        <code>IE</code>, <code>IT</code>, <code>LT</code>, <code>LU</code>, <code>LV</code>, <code>MT</code>, <code>NL</code>, <code>PL</code>, <code>PT</code>, <code>RO</code>, <code>SE</code>, <code>SI</code>, <code>SK</code>, <code>XI</code> like <code>DE</code>, <code>FR</code>, <code>IT</code>).</div>
    <div><span class="font-medium">standard_rate</span>: number (percent).</div>
    <div>
      <span class="font-medium">reduced_rates[]</span>: list of objects:
      <ul class="list-disc ml-5">
        <li><span class="font-medium">rate</span>: number (percent).</li>
        <li>
          <span class="font-medium">label</span>: string.<br>
          Possible values:
          <code>reduced_rate:ACCOMMODATION</code>,
          <code>reduced_rate:CULTURAL_EVENTS</code>,
          <code>reduced_rate:ZOOLOGICAL</code>, … (varies by country).
        </li>
      </ul>
    </div>
    <div><span class="font-medium">currency</span>: ISO currency code (e.g. <code>EUR</code>).</div>
    <div><span class="font-medium">valid_on</span>: date string (rates valid on this date).</div>
    <div><span class="font-medium">source</span>: string (e.g. <code>EU/VATify</code>).</div>
  </div>
</details>

        </div>

        <div>
          <div class="font-medium text-slate-700">Errors</div>
          <Snippet code='// 400 Bad Request
{  "error": "Error Message" }

// 404 Not Found
{  "error": "Error Message" }' />
        </div>

        <div>
          <div class="font-medium text-slate-700">Example cURL</div>
          <Snippet :code="rates_curl_example" />
        </div>
      </div>
    </section>

    <!-- GENERAL NOTES -->
    <section class="rounded-2xl shadow-card border border-gray-200 bg-white p-6">
      <h4 class="text-base font-semibold text-slate-800">General</h4>
      <ul class="mt-2 list-disc pl-5 text-sm text-slate-600 space-y-1">
        <li>All responses are JSON. Datetimes are RFC3339 (UTC).</li>
        <li>Rate limits: per-plan quotas; 429 returned when exceeded.</li>
        <li>Error schema: <code>{ "error": string }</code>.</li>
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
  const raw = (user?.value as any)?.apiKey || 'vk_live_xxx'
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
  -H "Authorization: Bearer ${exampleKey.value}"
  -H "Content-Type: application/json"
  -d '{"vat_number":"DE811907980"}'`


const rates_api_response = `{
  "country": "DE",
  "standard_rate": 19.0,
  "reduced_rates": [
   ...
    {
      "rate": 7.0,
      "label": "reduced_rate:ACCOMMODATION"
    },
    {
      "rate": 7.0,
      "label": "reduced_rate:CULTURAL_EVENTS"
    },
   ...
    {
      "rate": 7.0,
      "label": "reduced_rate:ZOOLOGICAL"
    }
  ],
  "currency": "EUR",
  "valid_on": "2025-07-01",
  "source": "EU/VATify"
}`

const rates_curl_example = `curl -s ${baseUrl}/v1/rates/DE
  -H "Authorization: Bearer ${exampleKey.value}"`


const calculate_endpoint = `POST ${baseUrl}/v1/calculate`
const calculate_headers = `Authorization: Bearer ${exampleKey.value}
Content-Type: application/json`

const calculate_request_example = `{
    "amount": 100.0,
    "basis": "net",
    "rate_type": "reduced",
    "supply_date": "2025-09-12",
    "supplier": { "country_code": "DE", "vat_number": "DE123456789" },
    "customer": { "country_code": "FR", "vat_number": "FR12345678901" },
    "supply_type": "services",
    "b2x": "B2B",
    "category_hint": "ACCOMMODATION"
  }`

const calculate_response_example = `{
  "country_code": "FR",
  "applied_rate": 10.0,
  "net": 100.0,
  "vat": 1000.0,
  "gross": 1100.0,
  "mechanism": "normal",
  "messages": [
    "Customer VAT number invalid or unavailable → Reverse Charge not applied.",
    "No Reverse Charge applied; VAT charged normally."
  ],
  "vat_check_status": "validated"
}`

const calculate_curl_example = `curl -s ${baseUrl}/v1/calculate
  -H "Authorization: Bearer ${exampleKey.value}"
  -H "Content-Type: application/json"
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
  }`
</script>

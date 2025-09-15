<!-- src/views/DashboardView.vue -->
<template>
  <div class="grid gap-6">
    <!-- User Card -->
    <section class="rounded-2xl shadow-card border border-gray-200 bg-white p-6">
      <div class="mb-2 flex items-center justify-between">
        <h3 class="text-lg font-semibold text-slate-800">Account</h3>
        <span v-if="user" class="text-xs text-slate-500">ID: {{ user.id }}</span>
      </div>
      <div v-if="user" class="text-sm text-slate-500">
        <div><span class="font-medium">E-Mail:</span> {{ user.email }}</div>
        <div v-if="user.username"><span class="font-medium">Name:</span> {{ user.username }}</div>
      </div>
      <div v-else class="text-sm text-slate-500">Lade…</div>
    </section>
   <BillingView v-if="user" :user="user" />
    <!-- Usage Card -->
     <section class="rounded-2xl shadow-card border border-gray-200 bg-white p-6">
     
      <div class="mb-2 flex items-center justify-between">
        <h3 class="text-lg font-semibold">Usage</h3>
        <button
    @click="loadUsage"
    :disabled="usageLoading"
    class="p-2 rounded-lg hover:bg-slate-100 disabled:opacity-50"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      stroke-width="1.5"
      stroke="currentColor"
      class="w-5 h-5 text-brand-600 "
      :class="{ 'animate-spin': usageLoading }"
    >
      <path stroke-linecap="round" stroke-linejoin="round"
        d="M16.023 9.348h4.992V4.356M21.015 12a9 9 0 11-3.108-6.873l3.108 3.108"/>
    </svg>
  </button>
      </div>

      <div v-if="usageLoading" class="text-sm text-gray-500">Lade Usage…</div>
      <div v-else-if="usage" class="space-y-2">
        <div class="flex items-center justify-between text-sm">
          <span>Used App and API calls</span>
          <span class="font-medium">{{ usage.data.total }} / {{ usage.data.max_quota }}</span>
        </div>
        <div class="h-2 w-full rounded bg-gray-100">
          <div
            class="h-2 bg-brand-500 rounded bg-black"
            :style="{ width: Math.min(100, Math.round((usage.data.total / usage.data.max_quota) * 100)) + '%' }"
          />
        </div>
        <p v-if="usage.period" class="text-xs text-gray-500">Periode: {{ usage.period }}</p>
      </div>
      <div v-else class="text-sm text-gray-500">Keine Daten.</div>
    </section>

    <!-- API Keys -->
    <section class="rounded-2xl shadow-card border border-gray-200 bg-white p-6">
      <div class="mb-3 flex items-center justify-between">
        <h3 class="text-lg font-semibold">API-Keys</h3>
        <div class="flex items-center gap-2">
          <input
            v-model="newLabel"
            class="w-44 rounded-md border px-3 py-1.5 text-sm outline-none focus:ring"
            placeholder="Name"
          />
          <button
            class="bg-brand-600 hover:bg-brand-700 text-white rounded-md px-3 py-1.5 text-sm disabled:opacity-50"
            :disabled="keysLoading"
            @click="createKey"
          >
            {{ keysLoading ? 'Create...' : 'Create New Key' }}
          </button>
        </div>
      </div>

      <div v-if="keysLoading && keys.data && keys.data.length.length === 0" class="text-sm text-gray-500">Lade Keys…</div>

      <ul v-else class="divide-y">
        <li v-for="k in sortedKeys" :key="k.id" class="py-3 flex items-center justify-between">
          <div class="text-sm">
            <div class="font-medium">
              {{ k.name || 'Ohne Label' }}
            </div>
            <div class="text-gray-500">
              {{ k.secret ? k.secret : "sk_live_" + '••••••••' + k.last4 }}
            </div>
          </div>
          <div class="text-xs text-gray-500">
            {{ k.created_at ? new Date(k.created_at).toLocaleString() : '' }}
          </div>
        </li>
      </ul>
    </section>

     <section class="rounded-2xl shadow-card border border-gray-200 bg-white p-6">
    <div class="flex items-center justify-between mb-3">
      <h3 class="font-semibold">Example Request with API Key</h3>

      <!-- Toggle Buttons -->
      <div class="inline-flex rounded-lg border border-slate-200 overflow-hidden">
        <button
          v-for="id in ['validate','calculate','rates']"
          :key="id"
          type="button"
          @click="active = id"
          class="px-3 py-1.5 text-sm font-medium transition-colors"
          :class="active === id
            ? 'bg-brand-600 text-white'
            : 'bg-white text-slate-600 hover:bg-slate-50'"
        >
          {{ id }}
        </button>
      </div>
    </div>

    <!-- Code Snippet -->
    <div class="bg-slate-900 text-slate-100 rounded-xl p-4 font-mono text-sm relative">
      <pre><code>{{ curlSnippet }}</code></pre>
      <button
        @click="copy"
        class="absolute top-2 right-2 text-slate-400 hover:text-slate-100"
      >
        Copy
      </button>
    </div>
    <!-- Validate VAT – neues Design -->
    <section v-if="active =='validate'" class="rounded-2xl mt-4 bg-white space-y-3">
      <label class="text-sm font-medium text-slate-700">VAT Number</label>

      <div class="flex gap-2 mt-2">
        <input
          v-model="validateVat"
          placeholder="e.g. DE811907980"
          class="flex-1 rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-brand-500"
        />
        <button
          class="px-4 py-2 rounded-lg bg-brand-600 text-white font-medium shadow-soft hover:bg-brand-700 disabled:opacity-50"
          @click="onValidate"
          :disabled="validateLoading"
        >
          <svg v-if="validateLoading" class="w-4 h-4 mr-1 inline animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 4v2m0 12v2m8-8h-2M6 12H4m12.364-6.364l-1.414 1.414M7.05 16.95l-1.414 1.414m12.728 0l-1.414-1.414M7.05 7.05 5.636 5.636"/>
    </svg>
    <span v-else>Check</span>

        </button>
      </div>

      <div class="flex items-center gap-2 text-sm">
        <span class="text-slate-500">Status:</span>
        <span v-if="validateStatus"
              class="inline-flex items-center rounded-full px-2 py-0.5 text-xs"
              :class="validateStatus.startsWith('2')
                ? 'bg-green-500/10 text-green-700'
                : 'bg-danger-500/10 text-danger-700'">
          {{ validateStatus }}
        </span>
        <span v-else class="text-slate-400">—</span>
      </div>

    <pre class="bg-slate-900 text-slate-100 rounded-xl p-4 font-mono text-sm overflow-auto">
       {{ validateResult || '{}' }}
      </pre>
    </section>
<!--
     <section v-if="active =='calculate'" class="rounded-2xl mt-4 bg-white space-y-3">
    <section class="border rounded p-4 space-y-3">
      <h3 class="font-medium">Rate berechnen</h3>
      <div class="grid sm:grid-cols-4 gap-2">
        <div class="sm:col-span-1">
          <label class="text-sm">Country</label>
          <input v-model="rateCountry" class="w-full rounded border px-3 py-2" placeholder="DE" />
        </div>
        <div class="sm:col-span-1">
          <label class="text-sm">Rate Type</label>
          <select v-model="rateType" class="w-full rounded border px-3 py-2">
            <option value="standard">standard</option>
            <option value="reduced">reduced</option>
          </select>
        </div>
        <div class="sm:col-span-1">
          <label class="text-sm">Date</label>
          <input v-model="rateDate" type="date" class="w-full rounded border px-3 py-2" />
        </div>
        <div class="sm:col-span-1">
          <label class="text-sm">Category (opt.)</label>
          <input v-model="rateCategory" class="w-full rounded border px-3 py-2" placeholder="z.B. books" />
        </div>
      </div>
      <button class="px-4 py-2 rounded bg-indigo-600 text-white" @click="onCalc">Berechnen</button>
      <div class="text-sm text-gray-500">Status: <code>{{ rateStatus || '—' }}</code></div>
      <pre class="bg-gray-50 border rounded p-3 text-sm overflow-auto">{{ rateResult || '(noch keine Antwort)' }}</pre>

      <div class="border rounded">
        <div class="px-3 py-2 border-b bg-gray-50 text-sm font-medium flex items-center justify-between">
          <span>cURL (Bearer)</span>
          <button class="text-xs px-2 py-1 border rounded" @click="navigator.clipboard.writeText(curlCalc)">Copy</button>
        </div>
        <pre class="p-3 bg-black text-white text-sm overflow-auto">{{ curlCalc }}</pre>
      </div>
    </section>
    </section>
    -->

     <section v-if="active =='rates'" class="rounded-2xl mt-4 bg-white space-y-3">
      <label class="text-sm font-medium text-slate-700">Country Code</label>

      <div class="flex gap-2 mt-2">
        <select v-model="selectedCountryCode" class="rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-brand-500">
          <option v-for="countryCode in countries" :key="countryCode" :value="countryCode">{{ countryCode }}</option>
        </select>

        <button
          class="px-4 py-2 rounded-lg bg-brand-600 text-white font-medium shadow-soft hover:bg-brand-700 disabled:opacity-50"
          @click="onLoadCountryRates"
          :disabled="onLoadCountryRatesLoading"
        >
          <svg v-if="onLoadCountryRatesLoading" class="w-4 h-4 mr-1 inline animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 4v2m0 12v2m8-8h-2M6 12H4m12.364-6.364l-1.414 1.414M7.05 16.95l-1.414 1.414m12.728 0l-1.414-1.414M7.05 7.05 5.636 5.636"/>
    </svg>
    <span v-else>Load</span>

        </button>
      </div>

      <div class="flex items-center gap-2 text-sm">
        <span class="text-slate-500">Status:</span>
        <span v-if="loadCountryRatesStatus"
              class="inline-flex items-center rounded-full px-2 py-0.5 text-xs"
              :class="loadCountryRatesStatus.startsWith('2')
                ? 'bg-green-500/10 text-green-700'
                : 'bg-danger-500/10 text-danger-700'">
          {{ loadCountryRatesStatus }}
        </span>
        <span v-else class="text-slate-400">—</span>
      </div>

    <pre class="bg-slate-900 text-slate-100 rounded-xl p-4 font-mono text-sm overflow-auto">
       {{ loadCountryRatesResult || '{}' }}
      </pre>
    </section>

  </section>
  <!--
    <ApiView baseUrl="/app" />
-->
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { useSession, type Usage, type ApiKey } from '@/composables/useSession';
import ApiView from '@/views/ApiView.vue';

const { user, getUsage, listApiKeys, createApiKey } = useSession();

const usage = ref<Usage | null>(null);
const usageLoading = ref(false);

const keys = ref<ApiKey[]>([]);
const keysLoading = ref(false);
const newLabel = ref('');
const countries = [
        "AT","BE","BG","CY","CZ","DE","DK","EE","EL","ES","FI","FR","HR","HU",
        "IE","IT","LT","LU","LV","MT","NL","PL","PT","RO","SE","SI","SK","XI"
    ]
const selectedCountryCode = ref('DE')
  
async function loadUsage() {
  usageLoading.value = true;
  try {
    usage.value = await getUsage();
  } finally {
    usageLoading.value = false;
  }
}

const sortedKeys = computed(() => {
    if (keys.value.length > 0) {
        keys.value.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        return keys.value.data
    } 
    return keys.value.data
})

async function loadKeys() {
  keysLoading.value = true;
  try {
    keys.value = await listApiKeys();
  } finally {
    keysLoading.value = false;
  }
}

async function createKey() {
  keysLoading.value = true;
  try {
    const created = await createApiKey(newLabel.value ? { name: newLabel.value } : {});
    keys.value.data.push(created.data)
    keys.value.data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    // In vielen APIs wird der Key nur einmal komplett zurückgegeben – hier zeigen wir ggf. key_preview
    //keys.value = [created.data, ...keys.value.data];
    //console.log(keys.value)
    newLabel.value = '';
  } finally {
    keysLoading.value = false;
  }
}

async function copy() {
  await navigator.clipboard.writeText(curlSnippet.value)
}

const base_url = import.meta.env.VITE_API_BASE_URL 

const active = ref<'validate' | 'calculate' | 'rates'>('validate')

const snippets: Record<typeof active.value, string> = {
  validate: `curl -s ${base_url}/v1/validate-vat \\
  -H "Authorization: Bearer <API_KEY>" \\
  -H "Content-Type: application/json" \\
  -d '{"vat_number":"DE811907980"}'`,

  calculate: `curl -s ${base_url}/v1/calculate \\
  -H "Authorization: Bearer <API_KEY>" \\
  -H "Content-Type: application/json" \\
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
  }'
`,

  rates: `curl -s ${base_url}/v1/rates/DE \\
  -H "Authorization: Bearer <API_KEY>" \\
  -H "Content-Type: application/json"`,
}

const curlSnippet = computed(() => snippets[active.value])


import { apiFetch } from '@/apiClient';
import BillingView from './BillingView.vue';
const hJson = { 'Content-Type': 'application/json' }
const pretty = (x: unknown) => {
  try { return JSON.stringify(x, null, 2) } catch { return String(x) }
}
async function sendJson(url: string, body: any) {
  const res = await apiFetch(url, {
    method: 'POST',
    headers: hJson,
    body: body,
  })
  
  return { ok: res.ok, status: `Done`, data: res.data }
}

// ---------------------------
// A) VALIDATE VAT (ein Feld)
// ---------------------------
const validateVat = ref("")
const validateStatus = ref('')
const validateResult = ref<string>('')

// Add missing loading ref for validation
const validateLoading = ref(false)

async function onValidate() {
  validateLoading.value = true
  validateStatus.value = 'Loading'
  validateResult.value = ''
  try {
    const { ok, status, data } = await sendJson(`/app/validate-vat`, { vat_number: validateVat.value })
    validateStatus.value = status
    validateResult.value = typeof data === 'string' ? data : pretty(data)
  } catch (error) {
    validateStatus.value = String(error)
    validateResult.value = {} as string
  }
  validateLoading.value = false
}


// ---------------------------
// B) LOAD COUNTRY RATES (ein Feld)
// ---------------------------
const loadCountryRatesStatus = ref('')
const loadCountryRatesResult = ref<string>('')
const onLoadCountryRatesLoading = ref(false)

async function onLoadCountryRates() {
  onLoadCountryRatesLoading.value = true
  loadCountryRatesStatus.value = 'Loading'
  loadCountryRatesResult.value = ''
  try {
    const { ok, status, data } = await sendJson(`/app/rates/${selectedCountryCode.value}`, {})
    loadCountryRatesStatus.value = status
    loadCountryRatesResult.value = typeof data === 'string' ? data : pretty(data)
  } catch (error) {
    loadCountryRatesStatus.value = String(error)
    loadCountryRatesResult.value = {} as string
  }
  onLoadCountryRatesLoading.value = false
}


onMounted(async () => {
  await Promise.all([loadUsage(), loadKeys()]);
});
</script>

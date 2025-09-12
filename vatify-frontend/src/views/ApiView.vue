<!-- src/components/VatifyMiniForms.vue -->
<script setup lang="ts">
// 1) Standard: deinen Helper importieren (Pfad/Name bei dir ggf. anders)
import { apiFetch as importedApiFetch } from '@/apiClient' // <- anpassen, falls nötig
import { computed, ref } from 'vue'

// 2) Props: falls dein Helper woanders liegt, kannst du ihn auch per Prop übergeben
const props = withDefaults(defineProps<{
  baseUrl?: string
  apiFetchFn?: (url: string, init?: RequestInit) => Promise<Response>
  getBearerToken?: () => string | null | undefined
}>(), {
  baseUrl: '/app'
})

// 3) Effektiv genutzter Helper
const apiFetch = props.apiFetchFn ?? importedApiFetch

// 4) Hilfen
const bearer = computed(() => props.getBearerToken?.() || '<YOUR_TOKEN>')
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
const validateVat = ref('DE811907980')
const validateStatus = ref('')
const validateResult = ref<string>('')

async function onValidate() {
  validateStatus.value = '...'
  validateResult.value = ''
  const { ok, status, data } = await sendJson(`${props.baseUrl}/validate-vat`, { vat_number: validateVat.value })
  validateStatus.value = status
  validateResult.value = typeof data === 'string' ? data : pretty(data)
}
const curlValidate = computed(() =>
  `curl -s ${props.baseUrl}/validate-vat \\
  -H "Authorization: Bearer ${bearer.value}" \\
  -H "Content-Type: application/json" \\
  -d ${JSON.stringify(JSON.stringify({ vat_number: validateVat.value }))}`
)

// ---------------------------
// B) CALCULATE RATE (klein)
// ---------------------------
const rateCountry = ref('DE')
const rateType = ref<'standard'|'reduced'>('standard')
const rateDate = ref<string>(new Date().toISOString().slice(0,10)) // YYYY-MM-DD
const rateCategory = ref<string>('') // optional
const rateStatus = ref('')
const rateResult = ref<string>('')

async function onCalc() {
  rateStatus.value = '...'
  rateResult.value = ''
  const payload = {
    country_code: rateCountry.value,
    rate_type: rateType.value,
    supply_date: rateDate.value,
    category_hint: rateCategory.value || null,
  }
  const { ok, status, data } = await sendJson(`${props.baseUrl}/calculate`, payload)
  rateStatus.value = status
  rateResult.value = typeof data === 'string' ? data : pretty(data)
}
const curlCalc = computed(() =>
  `curl -s ${props.baseUrl}/calculate \\
  -H "Authorization: Bearer ${bearer.value}" \\
  -H "Content-Type: application/json" \\
  -d ${JSON.stringify(JSON.stringify({
    country_code: rateCountry.value,
    rate_type: rateType.value,
    supply_date: rateDate.value,
    category_hint: rateCategory.value || null
  }))}`
)

// ---------------------------------
// C) VIES CHECK (ein einziges Feld)
// ---------------------------------
const viesVat = ref('DE811907980') // Eingabe wie "DE811907980"
const viesStatus = ref('')
const viesResult = ref<string>('')

function splitVat(v: string) {
  const t = v.trim()
  const cc = t.slice(0,2).toUpperCase()
  const num = t.slice(2).replace(/\\s+/g,'')
  return { countryCode: cc, vatNumber: num }
}

async function onVies() {
  viesStatus.value = '...'
  viesResult.value = ''
  const payload = splitVat(viesVat.value)
  const { ok, status, data } = await sendJson(`${props.baseUrl}/vies-check`, payload)
  viesStatus.value = status
  viesResult.value = typeof data === 'string' ? data : pretty(data)
}
const curlVies = computed(() => {
  const p = splitVat(viesVat.value)
  return `curl -s ${props.baseUrl}/vies-check \\
  -H "Authorization: Bearer ${bearer.value}" \\
  -H "Content-Type: application/json" \\
  -d ${JSON.stringify(JSON.stringify(p))}`
})
</script>

<template>
  <div class="space-y-8">
    <!-- A) VALIDATE VAT -->
   <section class="rounded-2xl bg-white space-y-3">
  <label class="text-sm font-medium text-slate-700">vat_number</label>

  <div class="flex gap-2">
    <input
      v-model="validateVat"
      placeholder="z.B. DE811907980"
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
{{ validateResult || '(noch keine Antwort)' }}
  </pre>
</section>

    <!-- B) CALCULATE RATE -->
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

    <!-- C) VIES CHECK -->
    <section class="border rounded p-4 space-y-3">
      <h3 class="font-medium">VIES Check</h3>
      <div class="flex gap-2">
        <input v-model="viesVat" class="flex-1 rounded border px-3 py-2" placeholder="z.B. DE811907980" />
        <button class="px-4 py-2 rounded bg-indigo-600 text-white" @click="onVies">Check</button>
      </div>
      <div class="text-sm text-gray-500">Status: <code>{{ viesStatus || '—' }}</code></div>
      <pre class="bg-gray-50 border rounded p-3 text-sm overflow-auto">{{ viesResult || '(noch keine Antwort)' }}</pre>

      <div class="border rounded">
        <div class="px-3 py-2 border-b bg-gray-50 text-sm font-medium flex items-center justify-between">
          <span>cURL (Bearer)</span>
          <button class="text-xs px-2 py-1 border rounded" @click="navigator.clipboard.writeText(curlVies)">Copy</button>
        </div>
        <pre class="p-3 bg-black text-white text-sm overflow-auto">{{ curlVies }}</pre>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* Minimal, nutzt deine globalen Styles / Tailwind falls vorhanden */
</style>

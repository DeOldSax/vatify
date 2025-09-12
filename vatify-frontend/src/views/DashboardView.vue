<!-- src/views/DashboardView.vue -->
<template>
  <div class="grid gap-6">
    <!-- User Card -->
    <section class="rounded-xl border bg-white p-4">
      <div class="mb-2 flex items-center justify-between">
        <h3 class="text-lg font-semibold">Dein Account</h3>
        <span v-if="user" class="text-xs text-gray-500">ID: {{ user.id }}</span>
      </div>
      <div v-if="user" class="text-sm text-gray-700">
        <div><span class="font-medium">E-Mail:</span> {{ user.email }}</div>
        <div v-if="user.username"><span class="font-medium">Name:</span> {{ user.username }}</div>
      </div>
      <div v-else class="text-sm text-gray-500">Lade…</div>
    </section>

    <!-- Usage Card -->
    <section class="rounded-xl border bg-white p-4">
      <div class="mb-2 flex items-center justify-between">
        <h3 class="text-lg font-semibold">Nutzung</h3>
        <button class="text-sm underline" @click="loadUsage" :disabled="usageLoading">
          Aktualisieren
        </button>
      </div>

      <div v-if="usageLoading" class="text-sm text-gray-500">Lade Usage…</div>
      <div v-else-if="usage" class="space-y-2">
        <div class="flex items-center justify-between text-sm">
          <span>Verbraucht</span>
          <span class="font-medium">{{ usage.data.total }} / 30</span>
        </div>
        <div class="h-2 w-full rounded bg-gray-100">
          <div
            class="h-2 rounded bg-black"
            :style="{ width: Math.min(100, Math.round((usage.data.total / 30) * 100)) + '%' }"
          />
        </div>
        <p v-if="usage.period" class="text-xs text-gray-500">Periode: {{ usage.period }}</p>
      </div>
      <div v-else class="text-sm text-gray-500">Keine Daten.</div>
    </section>

    <!-- API Keys -->
    <section class="rounded-xl border bg-white p-4">
      <div class="mb-3 flex items-center justify-between">
        <h3 class="text-lg font-semibold">API-Keys</h3>
        <div class="flex items-center gap-2">
          <input
            v-model="newLabel"
            class="w-44 rounded-md border px-3 py-1.5 text-sm outline-none focus:ring"
            placeholder="Label (optional)"
          />
          <button
            class="rounded-md bg-black px-3 py-1.5 text-sm text-white disabled:opacity-50"
            :disabled="keysLoading"
            @click="createKey"
          >
            {{ keysLoading ? 'Erstelle…' : 'Neuen Key erstellen' }}
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
              {{ k.secret ? k.secret : '••••••••' + k.last4 }}
            </div>
          </div>
          <div class="text-xs text-gray-500">
            {{ k.created_at ? new Date(k.created_at).toLocaleString() : '' }}
          </div>
        </li>
      </ul>
    </section>

     <section class="space-y-4">
    <div class="rounded-xl border p-4">
      <div class="flex items-center justify-between">
        <h3 class="font-semibold">Beispiel-Request mit API-Key</h3>
        <span class="text-sm text-gray-500">sichtbar: {{ masked }}</span>
      </div>

      <pre class="bg-gray-100 rounded p-3 overflow-auto"><code>{{ curlSnippet }}</code></pre>
      <button class="mt-2 px-3 py-1 rounded bg-black text-white"
              @click="copy">Copy</button>
    </div>
  </section>
    <ApiView baseUrl="/app" />
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


const baseUrl = import.meta.env.VITE_API_BASE_URL
const apiKey = ref('sk_live_abcdef1234567890abcdef') // echten Key vom Backend laden

const masked = computed(() => apiKey.value.replace(/^(.{8}).+(.{4})$/, '$1…$2'))

const curlSnippet = computed(() => `curl -s ${baseUrl}/v1/validate-vat \\
  -H "Authorization: Bearer ${apiKey.value}" \\
  -H "Content-Type: application/json" \\
  -d '{"vat_number":"DE811907980"}' | jq`)

async function copy() {
  await navigator.clipboard.writeText(curlSnippet.value)
}

onMounted(async () => {
  await Promise.all([loadUsage(), loadKeys()]);
});
</script>

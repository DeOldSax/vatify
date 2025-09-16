<!-- BillingBasicCard.vue -->
<template>
  
    <section class="rounded-2xl shadow-card border border-gray-200 bg-white p-6">
      <div class="mb-3 flex items-center justify-between">
        <h3 class="text-lg font-semibold">API-Keys <span class="text-gray-500 text-sm">(only just created keys are visible!)</span></h3>
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
              {{ k.secret ? k.secret : "vk_live_" + '••••••••' + k.last4 }}
            </div>
          </div>
          <div class="text-xs text-gray-500">
            {{ k.created_at ? new Date(k.created_at).toLocaleString() : '' }}
          </div>
        </li>
      </ul>
    </section>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { useSession, type Usage, type ApiKey } from '@/composables/useSession';

const { user, getUsage, listApiKeys, createApiKey } = useSession();


const keys = ref<ApiKey[]>([]);
const keysLoading = ref(false);
const newLabel = ref('');


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
    const created = await createApiKey(newLabel.value ? { name: newLabel.value } : { name: 'Vatify Api Key ' + Date.now()});
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

onMounted(async () => {
  await Promise.all([loadKeys()]);
});

</script>

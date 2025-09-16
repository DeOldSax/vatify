<template>
  <div class="grid gap-6">

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


  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { useSession, type Usage, type ApiKey } from '@/composables/useSession';
import BillingView from './BillingView.vue';

const { user, getUsage, listApiKeys, createApiKey } = useSession();

const usage = ref<Usage | null>(null);
const usageLoading = ref(false);


async function loadUsage() {
  usageLoading.value = true;
  try {
    usage.value = await getUsage();
  } finally {
    usageLoading.value = false;
  }
}


onMounted(async () => {
  await Promise.all([loadUsage()]);
});
</script>

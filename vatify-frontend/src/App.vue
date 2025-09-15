<template>
  <div class="min-h-screen bg-slate-50 text-slate-800">
    <!-- Header -->
    <header class="border-b bg-white shadow-soft">
      <div class="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between">
        <!-- Logo / Title -->
        <h1 class="text-xl font-semibold tracking-tight text-brand-700">
          Vatify <span class="text-sm text-gray-600">- EU VAT API for validation & rates</span> 
        </h1>

        <!-- Right Actions -->
        <div class="flex items-center gap-3" v-if="isAuthenticated">
          <button
            class="px-3 py-1.5 rounded-lg border border-gray-300 text-sm font-medium text-slate-700 bg-white hover:bg-gray-50 focus:ring-2 focus:ring-brand-500"
            @click="onLogout"
          >
            Logout
          </button>
        </div>
      </div>
    </header>

    <!-- Main -->
    <main class="mx-auto max-w-6xl px-4 py-6">
      <router-view />
    </main>
  </div>
</template>


<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useSession } from '@/composables/useSession';

const router = useRouter();
const { user, isAuthenticated, logout } = useSession();

async function onLogout() {
  await logout();
  router.replace({ name: 'login' });
}
</script>

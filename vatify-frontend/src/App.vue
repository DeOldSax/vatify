<!-- src/App.vue -->
<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <header class="border-b bg-white">
      <div class="mx-auto max-w-5xl px-4 py-3 flex items-center justify-between">
        <h1 class="text-lg font-semibold">Vatify Dashboard</h1>
        <div class="flex items-center gap-3" v-if="isAuthenticated">
          <span class="text-sm text-gray-600">Eingeloggt als {{ user?.email }}</span>
          <button
            class="rounded-md border px-3 py-1.5 text-sm hover:bg-gray-50"
            @click="onLogout"
          >
            Logout
          </button>
        </div>
      </div>
    </header>

    <main class="mx-auto max-w-5xl px-4 py-6">
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
  router.push({ name: 'login' });
}
</script>

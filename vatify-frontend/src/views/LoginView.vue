<!-- src/views/LoginView.vue -->
<template>
  <div class="mx-auto max-w-md">
    <div class="mb-6 text-center">
      <h2 class="text-2xl font-bold">Willkommen</h2>
      <p class="text-sm text-gray-600">Melde dich an oder registriere dich</p>
    </div>

    <div class="mb-4 grid grid-cols-2 rounded-lg border bg-white p-1">
      <button
        :class="tab === 'login' ? activeTab : inactiveTab"
        @click="tab = 'login'"
      >
        Login
      </button>
      <button
        :class="tab === 'register' ? activeTab : inactiveTab"
        @click="tab = 'register'"
      >
        Registrieren
      </button>
    </div>

    <form
      v-if="tab === 'login'"
      class="space-y-4 rounded-xl border bg-white p-4"
      @submit.prevent="handleLogin"
    >
      <div>
        <label class="mb-1 block text-sm">E-Mail</label>
        <input v-model="loginForm.email_or_username" type="email" required class="w-full rounded-md border px-3 py-2 outline-none focus:ring"/>
      </div>
      <div>
        <label class="mb-1 block text-sm">Passwort</label>
        <input v-model="loginForm.password" type="password" required class="w-full rounded-md border px-3 py-2 outline-none focus:ring"/>
      </div>

      <button
        class="w-full rounded-md bg-black px-3 py-2 text-white disabled:opacity-50"
        :disabled="loading"
      >
        {{ loading ? 'Einloggen…' : 'Einloggen' }}
      </button>
      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
    </form>

    <form
      v-else
      class="space-y-4 rounded-xl border bg-white p-4"
      @submit.prevent="handleRegister"
    >
      <div>
        <label class="mb-1 block text-sm">Name (optional)</label>
        <input v-model="registerForm.username" type="text" class="w-full rounded-md border px-3 py-2 outline-none focus:ring"/>
      </div>
      <div>
        <label class="mb-1 block text-sm">E-Mail</label>
        <input v-model="registerForm.email" type="email" required class="w-full rounded-md border px-3 py-2 outline-none focus:ring"/>
      </div>
      <div>
        <label class="mb-1 block text-sm">Passwort</label>
        <input v-model="registerForm.password" type="password" required minlength="8" class="w-full rounded-md border px-3 py-2 outline-none focus:ring"/>
      </div>

      <button
        class="w-full rounded-md bg-black px-3 py-2 text-white disabled:opacity-50"
        :disabled="loading"
      >
        {{ loading ? 'Registriere…' : 'Registrieren' }}
      </button>
      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useSession } from '@/composables/useSession';

const router = useRouter();
const route = useRoute();
const { login, register, loading, error } = useSession();

const tab = ref<'login' | 'register'>('login');

const loginForm = ref({ email_or_username: '', password: '' });
const registerForm = ref({ username: '', email: '', password: '' });

const activeTab = 'rounded-md bg-black px-3 py-2 text-white';
const inactiveTab = 'rounded-md px-3 py-2 text-gray-700 hover:bg-gray-50';

async function handleLogin() {
  await login(loginForm.value);
  const redirect = (route.query.redirect as string) ?? '/dashboard';
  router.push(redirect);
}

async function handleRegister() {
  await register(registerForm.value);
  router.push('/dashboard');
}
</script>

<!-- src/views/LoginView.vue -->

<template>
  <div class="mx-auto max-w-md">
    <!-- Header -->
    <div class="mb-6 text-center">
      <h2 class="text-2xl font-semibold tracking-tight text-slate-800">Welcome</h2>
      <p class="text-sm text-slate-500">Please log in or register</p>
    </div>

   <!-- Tabs mit gleitendem Indicator -->
<div class="relative mb-4 grid grid-cols-2 rounded-xl bg-white p-1 shadow-soft">
  <!-- Sliding indicator: deckt genau 50% ab, keine inset-y / left offsets -->
  <div
    class="pointer-events-none absolute top-1 left-1 bottom-1 w-[calc(50%-0.4rem)] rounded-xl bg-brand-600/10 ring-1 ring-brand-600/30 transition-transform duration-300"
    :class="isLogin ? 'translate-x-0' : 'translate-x-[calc(100%+0.25rem)]'"
  />
  <button
    class="z-[1] rounded-xl px-3 py-2 text-sm font-medium transition-colors"
    :class="isLogin ? 'text-brand-700' : 'text-slate-500 hover:text-slate-700'"
    @click="tab = 'login'"
    type="button"
  >
    Login
  </button>
  <button
    class="z-[1] rounded-lg px-3 py-2 text-sm font-medium transition-colors"
    :class="!isLogin ? 'text-brand-700' : 'text-slate-500 hover:text-slate-700'"
    @click="tab = 'register'"
    type="button"
  >
    Register
  </button>
</div>


    <!-- Forms mit Transition -->
    <Transition
      mode="out-in"
      enter-active-class="transition duration-300"
      enter-from-class="opacity-0 translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-200"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <!-- LOGIN -->
      <form
        v-if="isLogin"
        key="login"
        class="space-y-4 rounded-2xl bg-white p-5 shadow-card"
        @submit.prevent="handleLogin"
      >
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700">E-Mail or Username</label>
          <input v-model="loginForm.email_or_username" type="text" required
                 class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-brand-500" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700">Password</label>
          <input v-model="loginForm.password" type="password" required
                 class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-brand-500" />
        </div>

        <button
          class="w-full rounded-lg bg-brand-600 px-3 py-2 text-white font-medium shadow-soft transition-colors hover:bg-brand-700 disabled:opacity-50"
          :disabled="loading"
        >
          {{ loading ? 'Login…' : 'Login' }}
        </button>
        <p v-if="error" class="text-sm text-danger-500">{{ error }}</p>
      </form>

      <!-- REGISTER -->
      <form
        v-else
        key="register"
        class="space-y-4 rounded-2xl bg-white p-5 shadow-card"
        @submit.prevent="handleRegister"
      >
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700">Name (optional)</label>
          <input v-model="registerForm.username" type="text"
                 class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-brand-500" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700">E-Mail</label>
          <input v-model="registerForm.email" type="email" required
                 class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-brand-500" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-700">Password</label>
          <input v-model="registerForm.password" type="password" required minlength="8"
                 class="w-full rounded-lg border border-slate-300 px-3 py-2 outline-none focus:ring-2 focus:ring-brand-500" />
        </div>

        <button
          class="w-full rounded-lg bg-brand-600 px-3 py-2 text-white font-medium shadow-soft transition-colors hover:bg-brand-700 disabled:opacity-50"
          :disabled="loading"
        >
          {{ loading ? 'Register…' : 'Register' }}
        </button>
        <p v-if="error" class="text-sm text-danger-500">{{ error }}</p>
      </form>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useSession } from '@/composables/useSession'

const router = useRouter()
const route = useRoute()
const { login, register, loading, error, fetchMe } = useSession()

// Tabs
const tab = ref<'login' | 'register'>('login')
const isLogin = computed(() => tab.value === 'login')

// Forms
const loginForm = ref({ email_or_username: '', password: '' })
const registerForm = ref({ username: '', email: '', password: '' })

async function handleLogin() {
  if (loading.value) return
  error.value = '' as any
  try {
    await login(loginForm.value)
    const redirect = (route.query.redirect as string) ?? '/dashboard'
    router.push(redirect)
  } catch {
    // error wird von useSession gesetzt/weitergereicht
  }
}

async function handleRegister() {
  if (loading.value) return
  error.value = '' as any
  try {
    await register(registerForm.value)

    await fetchMe()

    await router.replace({ name: 'dashboard' })
    //router.push('dashboard')
  } catch {
    // error wird von useSession gesetzt/weitergereicht
  }
}
</script>

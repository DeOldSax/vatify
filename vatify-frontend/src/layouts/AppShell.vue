<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Sidebar from '@/components/Sidebar.vue'
import { useSession } from '@/composables/useSession'

const router = useRouter()
const route = useRoute()
const session = useSession()

const isOpen = ref(false)
const hideChrome = computed(() => route.name === 'login')

async function onLogout() {
  await session.logout()
  router.replace({ name: 'login' })
}

watch(() => route.fullPath, () => { isOpen.value = false })
</script>

<template>
  <div class="min-h-screen bg-white text-gray-900">
    <!-- Mobile overlay -->
    <transition name="fade">
      <div
        v-if="!hideChrome && isOpen"
        class="fixed inset-0 z-40 bg-black/40 md:hidden"
        @click="isOpen = false"
      />
    </transition>

    <!-- Mobile sidebar -->
    <transition name="slide">
      <div
        v-if="!hideChrome"
        class="fixed inset-y-0 left-0 z-50 md:hidden transform transition-transform"
        :class="isOpen ? 'translate-x-0' : '-translate-x-full'"
      >
        <Sidebar />
      </div>
    </transition>

    <!-- Desktop sidebar -->
    <div v-if="!hideChrome" class="hidden md:fixed md:inset-y-0 md:left-0 md:z-30 md:block">
      <Sidebar />
    </div>

    <!-- Main -->
    <main :class="!hideChrome ? 'md:pl-56' : ''">
      <!-- Topbar -->
      <header
        v-if="!hideChrome"
        class="h-14 border-b border-gray-200 flex items-center gap-3 px-4"
      >
        <!-- Hamburger (mobile) -->
        <button
          class="md:hidden inline-flex h-9 w-9 items-center justify-center rounded-lg border border-gray-300 bg-white"
          @click="isOpen = !isOpen"
          :aria-expanded="isOpen"
          aria-controls="mobile-sidebar"
          aria-label="Toggle Menu"
        >
          <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M4 7h16M4 12h16M4 17h16" stroke-linecap="round" />
          </svg>
        </button>

        <h1 class="text-xl font-semibold tracking-tight text-indigo-700">
          Vatify <span class="text-sm text-gray-600">- EU VAT API for validation & rates</span>
        </h1>

        <div class="ml-auto">
          <button
            v-if="session.isAuthenticated"
            class="px-3 py-1.5 rounded-lg border border-gray-300 text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:ring-2 focus:ring-indigo-500"
            @click="onLogout"
          >
            Logout
          </button>
        </div>
      </header>

      <!-- Page content -->
      <div class="p-4 md:p-6">
        <router-view />
      </div>
    </main>
  </div>
</template>

<style scoped>
.slide-enter-active, .slide-leave-active { transition: transform 0.2s ease; }
.slide-enter-from, .slide-leave-to { transform: translateX(-100%); }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@media (max-width: 768px) {
  main { padding-left: 0; }
}
</style>

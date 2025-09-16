<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const items = [
  { name: 'Dashboard', to: '/dashboard', icon: 'M3 12l7-7 7 7M5 10v10h4v-6h6v6h4V10' },
  { name: 'API Keys', to: '/keys', icon: 'M15 7a3 3 0 1 0-2.83 2H12l-2 2H8v2H6v2h2l4-4h.17A3 3 0 0 0 15 7z' },
  { name: 'API Playground', to: '/api', icon: 'M4 6h16v4H4zm0 6h10v6H4z' },
  { name: 'API Documentation', to: '/docs', icon: 'M6 2h9l5 5v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z M14 2v6h6 M8 13h8 M8 17h8' },
]
const isActive = (path: string) => route.path.startsWith(path)
</script>

<template>
  <aside class="h-full w-56 border-r border-gray-200 bg-white">
    <!-- Brand -->
    <div class="h-14 flex items-center gap-2 px-4">
    </div>

    <!-- Nav -->
    <nav class="p-2">
      <ul class="space-y-1">
        <li v-for="it in items" :key="it.to">
          <router-link
            :to="it.to"
            class="group flex items-center gap-3 rounded-xl px-3 py-2 text-sm hover:bg-gray-100"
            :class="isActive(it.to)
              ? 'bg-gray-100 text-gray-900'
              : 'text-gray-600'"
          >
            <svg viewBox="0 0 24 24" class="h-5 w-5 flex-none"
                 fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path :d="it.icon" />
            </svg>
            <span class="truncate">{{ it.name }}</span>
          </router-link>
        </li>
      </ul>
    </nav>

  </aside>
</template>

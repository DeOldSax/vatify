<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
const items = [
  { name: 'Dashboard', to: '/dashboard', icon: 'M3 12l7-7 7 7M5 10v10h4v-6h6v6h4V10' },
  { name: 'API Playground', to: '/api', icon: 'M4 6h16v4H4zm0 6h10v6H4z' },
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

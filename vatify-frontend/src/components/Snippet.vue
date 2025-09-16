<template>
  <div class="relative w-full max-w-full mt-3">
    <!-- dark-only snippet, scrolls inside the box -->
    <pre class="bg-slate-900 text-slate-100 rounded-xl px-4 py-0 font-mono text-sm relative">
      <code class="block whitespace-pre">{{ code }}</code>
    </pre>

    <button
      class="absolute top-2 right-2 px-2 py-1 rounded-md text-slate-100 text-[11px] hover:bg-slate-700 active:scale-95 transition"
      @click="copy"
      :aria-label="copied ? 'Copied!' : 'Copy'"
    >
      {{ copied ? 'Copied!' : 'Copy' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{ id?: string; code: string }>()
const copied = ref(false)

async function copy() {
  try {
    await navigator.clipboard.writeText(props.code)
    copied.value = true
    setTimeout(() => (copied.value = false), 1500)
  } catch {
    // optionally toast an error
  }
}
</script>

<style scoped>
/* Keep the snippet boxed so it can’t force the card wider */
:host, .relative { max-width: 100%; }
</style>

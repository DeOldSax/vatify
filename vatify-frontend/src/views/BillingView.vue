<!-- BillingBasicCard.vue -->
<template>
  <section class="rounded-2xl shadow-card border border-gray-200 bg-white p-6">
    <div class="mb-2 flex items-center justify-between">
  <h3 class="text-xl font-semibold">Vatify Pro Tier (1000 Requests / Month)</h3>
  <span
    v-if="props.user.subscriptionStatus === 'active'"
    class="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700"
  >
    ● Active until {{ new Date(props.user.currentPeriodEnd).toLocaleDateString() }}
  </span>
</div>

    <p class="mt-1 text-sm text-gray-500">Monthly Subscription, Cancel anytime</p>
    <p class="mt-4 text-3xl font-bold">€9 <span class="text-sm text-gray-500">/Month</span></p>

    <button v-if="props.user.subscriptionStatus !== 'active'" class="mt-6 w-full rounded-xl bg-indigo-600 px-4 py-2 text-white"
            @click="onBuy">
      Subscribe Now
    </button>

    <button v-if="props.user.subscriptionStatus === 'active'"  class="mt-6 px-3 py-1.5 w-full rounded-xl border border-gray-300 text-sm font-medium text-slate-700 bg-white hover:bg-gray-50 focus:ring-2 focus:ring-brand-500"
            @click="onOpenPortal">
      Manage Subscription
    </button>
</section>
</template>

<script setup lang="ts">
// load props :user
import { defineProps } from "vue";
const props = withDefaults(defineProps<{
  user: User
}>(), {
})

// Update the import path if the file is located elsewhere, for example:
import { startCheckout, openPortal } from "../services/billing";
import type { User } from "@/composables/useSession";
// Or, if the file does not exist, create src/services/billing.ts with the following content:
// export async function startCheckout() { /* implementation */ }
async function onBuy() { await startCheckout(); }
async function onOpenPortal() { await openPortal(); }
</script>

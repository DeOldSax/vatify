// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '@/views/LoginView.vue';
import DashboardView from '@/views/DashboardView.vue';
import { useSession } from '@/composables/useSession';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/login', name: 'login', component: LoginView, meta: { guestOnly: true } },
    { path: '/dashboard', name: 'dashboard', component: DashboardView, meta: { requiresAuth: true } },
    { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
  ],
});

router.beforeEach(async (to) => {
  const s = useSession()

  // Einmalige Initialisierung/Restore
  if (!s.state?.initialized.value && !s.loading.value) {
    try { await s.fetchMe() } catch {}
  }

  if (to.meta.requiresAuth && !s.isAuthenticated.value) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.guestOnly && s.isAuthenticated.value) {
    return { name: 'dashboard' }
  }
})


export default router;

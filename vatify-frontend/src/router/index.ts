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
  const session = useSession();
  // Falls noch kein User geladen wurde, versuchen
  if (session.user === null && !session.loading.value) {
    try { await session.fetchMe(); } catch {}
  }

  if (to.meta.requiresAuth && !session.isAuthenticated.value) {
    return { name: 'login', query: { redirect: to.fullPath } };
  }
  if (to.meta.guestOnly && session.isAuthenticated.value) {
    return { name: 'dashboard' };
  }
});

export default router;

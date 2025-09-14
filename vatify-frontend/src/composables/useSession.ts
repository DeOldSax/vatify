// src/composables/useSession.ts
import { reactive, computed } from 'vue';
import * as api from '@/apiClient';

export type User = {
  id: string | number;
  email: string;
  username?: string;
  subscriptionStatus?: string;
  currentPeriodEnd?: string;
  // weitere Felder nach Bedarf
};

export type Usage = {
  total: number;
  by_endpoint: Record<string, number>;
  max_quota: number; // z.B. 1000
  period?: string; // z.B. 'monthly'
};

export type ApiKey = {
  id: string;
  name?: string;
  key_preview?: string; // z.B. "sk-abc...123"
  created_at?: string;
  secret?: string; // nur bei Erstellung zurückgegeben
};


type State = {
  user: User | null;
  loading: boolean;
  error: string | null;
  initialized: boolean;
};

const state = reactive<State>({
  user: null,
  loading: false,
  error: null,
  initialized: false
});

async function fetchMe() {
  state.loading = true;
  state.error = null;
  try {
    const me = await api.get<User>('/me');
    state.user = me.data as User
  } catch (e: any) {
    state.user = null;
    state.error = e?.message ?? 'Fehler beim Laden des Users';
  } finally {
    state.loading = false;
    state.initialized = true;
  }
}

async function login(payload: { email: string; password: string }) {
  state.loading = true;
  state.error = null;
  try {
    await api.post('/auth/login', payload);
    await fetchMe();
  } catch (e: any) {
    state.error = e?.message ?? 'Login fehlgeschlagen';
    throw e;
  } finally {
    state.loading = false;
  }
}

async function register(payload: { email: string; password: string; username?: string }) {
  state.loading = true;
  state.error = null;

  if (!payload.username) {
    payload.username = payload.email.split("@")[0];
  }

  try {
    await api.post('/auth/register', payload);
    await fetchMe();
  } catch (e: any) {
    state.error = e?.message ?? 'Registrierung fehlgeschlagen';
    throw e;
  } finally {
    state.loading = false;
  }
}

async function logout() {
  try {
    await api.post('/auth/logout');
  } finally {
    state.user = null;
  }
}

async function getUsage() {
  return api.get<Usage>('/me/usage');
}

async function listApiKeys() {
  return api.get<ApiKey[]>('/apikeys');
}

async function createApiKey(payload?: { name?: string }) {
  return api.post<ApiKey>('/apikeys', payload ?? {});
}

export function useSession() {
  const isAuthenticated = computed(() => !!state.user);
  return {
    // state
    user: state.user,
    loading: computed(() => state.loading),
    error: computed(() => state.error),
    isAuthenticated,

    // actions
    fetchMe,
    login,
    register,
    logout,
    getUsage,
    listApiKeys,
    createApiKey,
  };
}

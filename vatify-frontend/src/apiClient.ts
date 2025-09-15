// apiClient.ts
// Minimaler Fetch-Wrapper für Vatify SPA
// - Cookies inkl. httpOnly via credentials: 'include'
// - CSRF-Protection (Double Submit)
// - Auto-Refresh bei 401 (Single-Flight)
type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export type ApiOk<T> = { ok: true; data: T; status: number };
export type ApiErr = { ok: false; error: { code?: string; message: string; status: number }; status: number };
export type ApiResult<T> = ApiOk<T> | ApiErr;
let BASE_URL = import.meta.env.VITE_API_BASE_URL; // z.B. "" (same origin) oder "http://localhost:8000"
export function setBaseUrl(url: string) {
  BASE_URL = url.replace(/\/+$/, "");
}

function getCookie(name: string) {
  return document.cookie
    .split("; ")
    .find((row) => row.startsWith(name + "="))
    ?.split("=")[1];
}

function needCsrf(method: HttpMethod) {
  return method !== "GET" && method !== "HEAD" && method !== "OPTIONS";
}

// ---- Refresh Single-Flight ----
let refreshingPromise: Promise<void> | null = null;
async function refreshSession(): Promise<void> {
  if (!refreshingPromise) {
    refreshingPromise = (async () => {
      const res = await fetch(`${BASE_URL}/auth/refresh`, {
        method: "POST",
        credentials: "include",
      });
      // 200 => Cookies erneuert; andere Status ignorieren (Caller entscheidet)
      if (!res.ok) throw new Error(`Refresh failed with ${res.status}`);
    })()
      .catch((e) => {
        // nach Fehler kaskadierende Aufrufer sollen sehen, dass refresh kaputt ist
        throw e;
      })
      .finally(() => {
        refreshingPromise = null;
      });
  }
  return refreshingPromise;
}

// ---- Kernaufruf ----
export async function apiFetch<T = any>(
  path: string,
  opts: {
    method?: HttpMethod;
    body?: any;
    headers?: Record<string, string>;
    signal?: AbortSignal;
    // wenn du Rohantwort brauchst:
    raw?: boolean;
  } = {}
): Promise<ApiResult<T>> {
  const method: HttpMethod = (opts.method || "GET").toUpperCase() as HttpMethod;
  const headers: Record<string, string> = { ...(opts.headers || {}) };

  // JSON-Body standardisieren (kein multipart)
  let body: BodyInit | undefined = undefined;
  if (opts.body !== undefined && !(opts.body instanceof FormData)) {
    headers["Content-Type"] = headers["Content-Type"] || "application/json";
    body = JSON.stringify(opts.body);
  } else if (opts.body instanceof FormData) {
    body = opts.body; // Browser setzt Boundary / Content-Type selbst
  }

  if (needCsrf(method)) {
    const csrf = getCookie("csrf_token");
    if (csrf) headers["x-csrf-token"] = csrf;
  }

  const doRequest = () =>
    fetch(`${BASE_URL}${path}`, {
      method,
      credentials: "include",
      headers,
      body,
      signal: opts.signal,
    });

  // 1. Versuch
  let res = await doRequest();

  // 401 → ein Mal Refresh probieren, dann retry
  if (res.status === 401) {
    try {
      await refreshSession();
      res = await doRequest();
    } catch {
      // Refresh fehlgeschlagen → fällt unten in Fehlerbehandlung
    }
  }

  if (opts.raw) {
    // @ts-ignore – für raw Rückgaben packen wir minimal den Status mit rein
    return { ok: res.ok, data: res, status: res.status } as any;
  }

  // Antwort parsen (JSON erwartet)
  let payload: any = null;
  let raw = '';

  try {
    raw = await res.text();             // Body nur einmal lesen
    payload = raw ? JSON.parse(raw) : null;
  } catch {
    payload = { message: raw || res.statusText };
  }

  if (!res.ok) {
    throw new Error(payload?.detail || payload?.message || res.statusText);
  }



  if (res.ok) {
    // Falls dein Backend {ok:true,data} nicht nutzt, normalisieren:
    const data = payload?.data !== undefined ? payload.data : payload;
    return { ok: true, data, status: res.status };
  } else {
    const message =
      payload?.error?.message ||
      payload?.detail ||
      payload?.message ||
      `HTTP ${res.status}`;
    const code = payload?.error?.code;
    return { ok: false, error: { code, message, status: res.status }, status: res.status };
  }
}

// Komfort-Methoden
export const get = <T = any>(path: string, signal?: AbortSignal) =>
  apiFetch<T>(path, { method: "GET", signal });

export const post = <T = any>(path: string, body?: any, signal?: AbortSignal) =>
  apiFetch<T>(path, { method: "POST", body, signal });

export const put = <T = any>(path: string, body?: any, signal?: AbortSignal) =>
  apiFetch<T>(path, { method: "PUT", body, signal });

export const patch = <T = any>(path: string, body?: any, signal?: AbortSignal) =>
  apiFetch<T>(path, { method: "PATCH", body, signal });

export const del = <T = any>(path: string, body?: any, signal?: AbortSignal) =>
  apiFetch<T>(path, { method: "DELETE", body, signal });

// Datei-Upload (FormData)
export async function upload<T = any>(path: string, form: FormData, signal?: AbortSignal) {
  return apiFetch<T>(path, { method: "POST", body: form, signal });
}

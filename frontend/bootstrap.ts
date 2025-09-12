// bootstrap.ts
import { setBaseUrl } from "./apiClient";
// gleiche Origin: setBaseUrl("");  // oder explizit:
setBaseUrl(import.meta.env.VITE_API_URL ?? "http://localhost:8000");

// login.ts
import { post } from "./apiClient";
const res = await post<{ id: string; email: string; username: string }>("/auth/login", {
  email_or_username: "test",
  password: "secret",
});
if (!res.ok) alert(res.error.message);

// protected call (App-Route, CSRF automatisch)
import { post as postApi } from "./apiClient";
const r = await postApi("/app/endpointA", { foo: "bar" });
if (r.ok) console.log(r.data);
else if (r.status === 429) console.warn("Quota exceeded");

import { post } from "@/apiClient"; // Fetch-Wrapper (Bearer etc.)

export async function startCheckout() {
  const res = await post("/billing/checkout/session", {});
  window.location.href = res.data.url;
}

export async function openPortal() {
  const res = await post("/billing/portal/session", { return_path: "/dashboard/billing" });
  window.location.href = res.data.url;
}

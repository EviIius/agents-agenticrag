import { toast } from "sonner";
export function showUpdateToast(reload: () => void) {
  toast("A new version is available", {
    id: "workbench-update",
    duration: Infinity,
    action: { label: "Reload", onClick: reload },
  });
}
export async function registerPWA() {
  if (
    !import.meta.env.PROD ||
    !window.isSecureContext ||
    !("serviceWorker" in navigator)
  )
    return;
  try {
    const registration = await navigator.serviceWorker.register("/sw.js", {
      updateViaCache: "none",
    });
    let reloading = false;
    const offer = () => {
      if (!registration.waiting || !navigator.serviceWorker.controller) return;
      showUpdateToast(() => {
        if (!registration.waiting) return;
        reloading = true;
        registration.waiting.postMessage({ type: "SKIP_WAITING" });
      });
    };
    navigator.serviceWorker.addEventListener("controllerchange", () => {
      if (reloading) window.location.reload();
    });
    offer();
    registration.addEventListener("updatefound", () => {
      registration.installing?.addEventListener("statechange", offer);
    });
    window.addEventListener(
      "online",
      () => void registration.update().catch(() => {}),
    );
    document.addEventListener("visibilitychange", () => {
      if (!document.hidden) void registration.update().catch(() => {});
    });
  } catch {
    // The online app still works when registration/storage is unavailable.
  }
}

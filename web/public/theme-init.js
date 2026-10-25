(() => {
  let preference = "system";
  let palette = "cobalt";
  try {
    preference = localStorage.getItem("workbench-theme") || "system";
    palette = localStorage.getItem("workbench-palette") || "cobalt";
  } catch {
    /* Storage may be unavailable. */
  }
  // Keep in step with PALETTE_IDS and the modes in src/lib/palettes.ts.
  if (
    ![
      "cobalt",
      "lime",
      "paper",
      "ember",
      "orchid",
      "midnight",
      "mono",
      "aero",
    ].includes(palette)
  )
    palette = "cobalt";
  const dark =
    palette === "midnight" ||
    preference === "dark" ||
    (preference !== "light" &&
      matchMedia("(prefers-color-scheme: dark)").matches);
  const root = document.documentElement;
  root.dataset.theme = dark ? "dark" : "light";
  root.dataset.palette = palette;
  if (palette === "cobalt") return;
  // The icon links come after this script in index.html; point them at the palette's set.
  document.addEventListener("DOMContentLoaded", () => {
    const base = "/icons/" + palette;
    const links = {
      icon: base + "/mark.svg",
      "apple-touch-icon": base + "/apple-touch-icon.png",
      manifest: "/manifests/" + palette + ".webmanifest",
    };
    for (const [rel, href] of Object.entries(links))
      document
        .querySelectorAll('link[rel="' + rel + '"]')
        .forEach((link) => link.setAttribute("href", href));
  });
})();

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { fileURLToPath, URL } from "node:url";
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    {
      name: "workbench-pwa",
      apply: "build",
      generateBundle(_, bundle) {
        const hash = createHash("sha256");
        for (const name of Object.keys(bundle).sort()) {
          const file = bundle[name];
          hash
            .update(name)
            .update(file.type === "chunk" ? file.code : file.source);
        }
        const precache = [
          "/index.html",
          "/theme-init.js",
          "/fonts/Geist-Variable.woff2",
          "/fonts/Newsreader-Variable.woff2",
          "/manifest.webmanifest",
          "/icons/icon-192.png",
          "/icons/icon-512.png",
          "/icons/maskable-512.png",
          "/icons/apple-touch-icon.png",
        ];
        for (const file of Object.values(bundle)) {
          if (file.type === "chunk" && file.isEntry) {
            precache.push(
              "/" + file.fileName,
              ...file.imports.map((name) => "/" + name),
            );
          }
          if (
            file.type === "asset" &&
            file.fileName.startsWith("assets/index-") &&
            file.fileName.endsWith(".css")
          )
            precache.push("/" + file.fileName);
        }
        for (const name of precache.filter(
          (name) => !name.startsWith("/assets/") && name !== "/index.html",
        )) {
          hash
            .update(name)
            .update(readFileSync(new URL("./public" + name, import.meta.url)));
        }
        hash.update(
          readFileSync(new URL("./service-worker.js", import.meta.url)),
        );
        hash.update(readFileSync(new URL("./index.html", import.meta.url)));
        const source = readFileSync(
          new URL("./service-worker.js", import.meta.url),
          "utf8",
        )
          .replace("__BUILD__", hash.digest("hex").slice(0, 16))
          .replace("__PRECACHE__", JSON.stringify([...new Set(precache)]));
        this.emitFile({ type: "asset", fileName: "sw.js", source });
      },
    },
  ],
  resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
  build: {
    manifest: true,
    assetsInlineLimit: 0,
    outDir: "../server/app/static",
    emptyOutDir: true,
  },
  server: {
    proxy: { "/api": { target: "http://127.0.0.1:8787", changeOrigin: false } },
  },
});

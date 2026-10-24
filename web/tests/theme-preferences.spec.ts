import AxeBuilder from "@axe-core/playwright";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { createServer } from "node:http";
import { extname, resolve } from "node:path";
import type { AddressInfo } from "node:net";
import { expect, test } from "@playwright/test";
import { fakeAppURL } from "../test-runtime";
import { PALETTES, paletteIcons } from "../src/lib/palettes";
import { settle } from "./helpers";

for (const width of [390, 1440]) {
  for (const theme of ["light", "dark"] as const) {
    test(`Paper settings at ${width} ${theme}: persist, reload, fit and keyboard`, async ({
      page,
    }) => {
      const saved = await (
        await page.request.get(fakeAppURL + "/api/settings")
      ).json();
      const restore = Object.fromEntries([
        ["appearance.palette", saved["appearance.palette"] ?? "cobalt"],
        ["appearance.greeting", saved["appearance.greeting"] ?? "languages"],
        ["appearance.theme", saved["appearance.theme"] ?? "system"],
        ["appearance.font", saved["appearance.font"] ?? "serif"],
      ]);
      try {
        await page.setViewportSize({ width, height: 1000 });
        await page.emulateMedia({
          reducedMotion: "reduce",
          colorScheme: theme,
        });
        await page.goto("/");
        await expect(page.locator(".composer")).toBeVisible();
        await page.evaluate(async (theme) => {
          const path = "/src/stores/ui.ts";
          const { useUI } = await import(path);
          useUI.getState().set({
            settings: true,
            settingsPane: "Appearance",
            theme,
            palette: "cobalt",
          });
        }, theme);
        const dialog = page.getByRole("dialog", {
          name: "Settings",
          exact: true,
        });
        const sans = dialog.getByRole("button", {
          name: "Sans · Geist",
          exact: true,
        });
        await sans.click();
        await dialog.locator('[data-palette-option="paper"]').click();
        await expect(sans).toBeDisabled();
        await expect(
          dialog.getByText("Paper uses Newsreader throughout.", {
            exact: false,
          }),
        ).toBeVisible();
        await dialog
          .getByRole("button", { name: "English only", exact: true })
          .click();
        await expect
          .poll(
            async () =>
              (
                await (
                  await page.request.get(fakeAppURL + "/api/settings")
                ).json()
              )["appearance.palette"],
          )
          .toBe("paper");
        await expect
          .poll(
            async () =>
              (
                await (
                  await page.request.get(fakeAppURL + "/api/settings")
                ).json()
              )["appearance.greeting"],
          )
          .toBe("english");
        await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
        await settle(page);
        expect(
          await dialog.evaluate(
            (element) => element.scrollWidth > element.clientWidth,
          ),
        ).toBe(false);
        const findings = (
          await new AxeBuilder({ page }).analyze()
        ).violations.filter((item) =>
          ["serious", "critical"].includes(item.impact ?? ""),
        );
        expect(findings).toEqual([]);
        await dialog.screenshot({
          path: `../artifacts/themes/review-20261023/screens/paper-settings-${theme}-${width}-${test.info().project.name}.png`,
        });
        const next = dialog.locator('[data-palette-option="orchid"]');
        await next.focus();
        await page.keyboard.press("Space");
        await expect(next).toHaveAttribute("aria-pressed", "true");
        await expect(sans).toBeEnabled();
        await expect(sans).toHaveAttribute("aria-pressed", "true");
        await dialog.locator('[data-palette-option="paper"]').click();
        await expect
          .poll(
            async () =>
              (
                await (
                  await page.request.get(fakeAppURL + "/api/settings")
                ).json()
              )["appearance.palette"],
          )
          .toBe("paper");
        await page.reload();
        await expect(page.locator("html")).toHaveAttribute(
          "data-palette",
          "paper",
        );
        await expect(page.locator(".greeting .greet-word")).toHaveAttribute(
          "lang",
          "en",
        );
        await expect(page.locator("h1.greeting")).not.toHaveAttribute(
          "data-animate",
          /.*/,
        );
      } finally {
        expect(
          (
            await page.request.patch(fakeAppURL + "/api/settings", {
              data: restore,
            })
          ).ok(),
        ).toBe(true);
      }
    });
  }
}

test("palette icons and manifests survive actual origin loss with exact cached bytes", async ({
  page,
}) => {
  // Avoid WebKit's broken setOffline flag (Playwright #42775). Stop a separate
  // loopback origin instead; no-store headers prevent an HTTP-cache false pass.
  const root = resolve("../server/app/static");
  const server = createServer(async (request, response) => {
    const url = new URL(request.url ?? "/", "http://127.0.0.1");
    response.setHeader("Cache-Control", "no-store");
    if (url.pathname === "/offline-theme-fixture.html") {
      response.setHeader("Content-Type", "text/html");
      response.end(
        '<!doctype html><title>Synthetic theme cache</title><h1>Synthetic theme cache</h1><script>navigator.serviceWorker.register("/sw.js")</script>',
      );
      return;
    }
    const path = resolve(root, "." + decodeURIComponent(url.pathname));
    if (!path.startsWith(root + "/")) {
      response.writeHead(403).end();
      return;
    }
    try {
      const types: Record<string, string> = {
        ".js": "application/javascript",
        ".css": "text/css",
        ".html": "text/html",
        ".webmanifest": "application/manifest+json",
        ".png": "image/png",
        ".svg": "image/svg+xml",
      };
      response.setHeader(
        "Content-Type",
        types[extname(path)] ?? "application/octet-stream",
      );
      response.end(await readFile(path));
    } catch {
      response.writeHead(404).end();
    }
  });
  await new Promise<void>((resolve) => server.listen(0, "127.0.0.1", resolve));
  const stop = () =>
    new Promise<void>((resolve, reject) => {
      server.close((error) => (error ? reject(error) : resolve()));
      server.closeAllConnections();
    });
  try {
    const origin = `http://127.0.0.1:${(server.address() as AddressInfo).port}`;
    await page.goto(origin + "/offline-theme-fixture.html");
    await page.evaluate(() => navigator.serviceWorker.ready);
    await expect
      .poll(() => page.evaluate(() => !!navigator.serviceWorker.controller))
      .toBe(true);
    const urls = PALETTES.flatMap(({ id }) => Object.values(paletteIcons(id)));
    const expected = Object.fromEntries(
      await Promise.all(
        urls.map(async (url) => [
          url,
          createHash("sha256")
            .update(await readFile(root + url))
            .digest("hex"),
        ]),
      ),
    );
    const cached = await page.evaluate(async () => {
      const paths: string[] = [];
      for (const name of await caches.keys())
        for (const request of await (await caches.open(name)).keys())
          paths.push(new URL(request.url).pathname);
      return paths;
    });
    for (const url of urls) expect(cached).toContain(url);
    expect(cached.some((path) => path.startsWith("/api"))).toBe(false);
    await stop();
    const result = await page.evaluate(async (urls) => {
      const files: Record<string, string> = {};
      for (const url of urls) {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Cache response failed: ${url}`);
        const hash = await crypto.subtle.digest(
          "SHA-256",
          await response.arrayBuffer(),
        );
        files[url] = [...new Uint8Array(hash)]
          .map((byte) => byte.toString(16).padStart(2, "0"))
          .join("");
      }
      let uncached = "unexpected response";
      try {
        await fetch("/uncached-theme-negative-control");
      } catch {
        uncached = "network failed";
      }
      return { files, uncached };
    }, urls);
    expect(result.files).toEqual(expected);
    expect(result.uncached).toBe("network failed");
  } finally {
    if (server.listening) await stop();
  }
});

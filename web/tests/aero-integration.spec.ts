import AxeBuilder from "@axe-core/playwright";
import { test, expect, type Page } from "@playwright/test";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { fakeAppURL } from "../test-runtime";
import { settle } from "./helpers";

const evidence = resolve("../artifacts/themes/aero-integration-20261024");
async function measureContrast(page: Page, name: string) {
  await settle(page);
  await page.evaluate(() => document.getAnimations().forEach((a) => a.pause()));
  // PNG passes must describe one state, including auto-expiring notifications.
  // The caller installs the clock before app timers are created. Resume after
  // measurement so subsequent interactions retain their ordinary timer behavior.
  await page.clock.pauseAt(await page.evaluate(() => Date.now() + 1000));
  try {
    const prefix = resolve(evidence, name);
    const text = await page.evaluate(() => {
      const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
      );
      const rows = [];
      while (walker.nextNode()) {
        const node = walker.currentNode;
        const el = node.parentElement;
        if (
          !el ||
          !node.textContent?.trim() ||
          el.closest("script,style,svg,[disabled],[aria-hidden=true]")
        )
          continue;
        const style = getComputedStyle(el);
        if (style.visibility !== "visible" || Number(style.opacity) < 1)
          continue;
        const range = document.createRange();
        range.selectNodeContents(node);
        const rects = [...range.getClientRects()].filter((r) => {
          if (
            r.width < 2 ||
            r.height < 2 ||
            r.top < 0 ||
            r.bottom > innerHeight ||
            r.left < 0 ||
            r.right > innerWidth
          )
            return false;
          const hit = document.elementFromPoint(
            r.x + r.width / 2,
            r.y + r.height / 2,
          );
          return hit === el || el.contains(hit);
        });
        if (!rects.length) continue;
        el.setAttribute("data-contrast-text", "true");
        const elementId: string =
          el.getAttribute("data-contrast-id") ?? String(rows.length);
        el.setAttribute("data-contrast-id", elementId);
        const size = parseFloat(style.fontSize);
        const large =
          size >= 24 || (size >= 18.66 && parseInt(style.fontWeight) >= 700);
        rows.push({
          text: node.textContent.trim(),
          elementId,
          required: large ? 3 : 4.5,
          foreground: style.color,
          gradient: style.backgroundImage,
          rects: rects.map((r) => [r.left, r.top, r.right, r.bottom]),
        });
      }
      return rows;
    });
    await writeFile(`${prefix}.json`, JSON.stringify(text, null, 2));
    await page.screenshot({ path: `${prefix}-normal.png`, scale: "css" });
    const hidden = await page.addStyleTag({
      content: `* { color: transparent !important; -webkit-text-fill-color: transparent !important; text-shadow:none !important; caret-color:transparent !important; } .greet-word,.greet-char,.greeting-name { background-image:none !important; }`,
    });
    await page.screenshot({ path: `${prefix}-background.png`, scale: "css" });
    await hidden.evaluate((el) => el.parentNode?.removeChild(el));
    const mask = await page.addStyleTag({
      content: `html,body { background:#000 !important; } * { color:transparent !important; -webkit-text-fill-color:transparent !important; background:none !important; border-color:transparent !important; box-shadow:none !important; text-shadow:none !important; filter:none !important; backdrop-filter:none !important; } [data-contrast-text] { color:white !important; -webkit-text-fill-color:white !important; } *::placeholder { color:transparent !important; } *::before,*::after,svg { visibility:hidden !important; }`,
    });
    await page.screenshot({ path: `${prefix}-mask.png`, scale: "css" });
    await mask.evaluate((el) => el.parentNode?.removeChild(el));
    const result = await page.evaluate(
      async ({ images, text }) => {
        const data = await Promise.all(
          images.map(async (encoded) => {
            const img = new Image();
            img.src = "data:image/png;base64," + encoded;
            await img.decode();
            const canvas = document.createElement("canvas");
            canvas.width = img.width;
            canvas.height = img.height;
            const ctx = canvas.getContext("2d")!;
            ctx.drawImage(img, 0, 0);
            return ctx.getImageData(0, 0, img.width, img.height);
          }),
        );
        if (
          data.some(
            (image) =>
              image.width !== innerWidth ||
              image.width !== data[0].width ||
              image.height !== data[0].height,
          )
        )
          throw new Error(
            "Contrast PNGs must use the same CSS viewport as the text coordinates",
          );
        const lum = (rgb: number[]) =>
          rgb
            .map((v) => {
              const x = v / 255;
              return x <= 0.04045 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4;
            })
            .reduce((sum, x, i) => sum + x * [0.2126, 0.7152, 0.0722][i], 0);
        const ctx = document.createElement("canvas").getContext("2d")!;
        const rgba = (color: string) => {
          ctx.clearRect(0, 0, 1, 1);
          ctx.fillStyle = color;
          ctx.fillRect(0, 0, 1, 1);
          return [...ctx.getImageData(0, 0, 1, 1).data];
        };
        const runs = text.flatMap((row) => {
          const element = document.querySelector(
            `[data-contrast-id="${row.elementId}"]`,
          );
          if (!element) throw new Error("Measured text element disappeared");
          const solid = rgba(row.foreground);
          const foregrounds = solid[3]
            ? [solid]
            : [...row.gradient.matchAll(/rgba?\([^)]+\)/g)].map((m) =>
                rgba(m[0]),
              );
          if (!foregrounds.length)
            throw new Error(`Unmeasured transparent text: ${row.text}`);
          const values: number[] = [];
          for (const [x0, y0, x1, y1] of row.rects)
            for (
              let y = Math.max(0, Math.floor(y0));
              y < Math.min(data[0].height, Math.ceil(y1));
              y++
            )
              for (
                let x = Math.max(0, Math.floor(x0));
                x < Math.min(data[0].width, Math.ceil(x1));
                x++
              ) {
                const pos = (y * data[0].width + x) * 4;
                if (Math.min(...data[2].data.slice(pos, pos + 3)) < 255)
                  continue;
                // A partially occluded line can have a visible center. Test each
                // sampled glyph against the restored real page, including toasts.
                const hit = document.elementFromPoint(x + 0.5, y + 0.5);
                if (hit !== element && !element.contains(hit)) continue;
                // PNG pixels cover an area: a fractional overlay edge can cover
                // one corner even when its center is outside the overlay.
                if (
                  [
                    [0.01, 0.01],
                    [0.99, 0.01],
                    [0.01, 0.99],
                    [0.99, 0.99],
                  ].some(([dx, dy]) => {
                    const corner = document.elementFromPoint(x + dx, y + dy);
                    return corner !== element && !element.contains(corner);
                  })
                )
                  continue;
                const bg = [...data[1].data.slice(pos, pos + 3)];
                const b = lum(bg);
                for (const fg of foregrounds) {
                  const a = lum(
                    fg
                      .slice(0, 3)
                      .map(
                        (v, i) => (v * fg[3]) / 255 + bg[i] * (1 - fg[3] / 255),
                      ),
                  );
                  values.push(
                    (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05),
                  );
                }
              }
          return values.length < 3
            ? []
            : [
                {
                  text: row.text,
                  pixels: values.length,
                  minimum: Math.min(...values),
                  required: row.required,
                },
              ];
        });
        return {
          method:
            "Computed CSS foreground (conservative gradient stops) against rendered background-only PNG at individually hit-tested visible glyph pixels; frozen CSS scene; antialias edges excluded",
          sampled_text_runs: runs.length,
          failures: runs.filter((r) => r.minimum + 0.02 < r.required),
          runs,
        };
      },
      {
        images: await Promise.all(
          ["normal", "background", "mask"].map(async (kind) =>
            (await readFile(`${prefix}-${kind}.png`)).toString("base64"),
          ),
        ),
        text,
      },
    );
    await writeFile(`${prefix}-contrast.json`, JSON.stringify(result, null, 2));
    await page.evaluate(() =>
      document.querySelectorAll("[data-contrast-text]").forEach((el) => {
        el.removeAttribute("data-contrast-text");
        el.removeAttribute("data-contrast-id");
      }),
    );
    return result;
  } finally {
    await page.clock.resume();
  }
}
async function audit(page: Page, name: string) {
  await settle(page);
  const violations = (await new AxeBuilder({ page }).analyze()).violations;
  expect(
    violations.filter((v) => ["serious", "critical"].includes(v.impact ?? "")),
  ).toEqual([]);
  const result = await measureContrast(page, name);
  expect(result.sampled_text_runs).toBeGreaterThanOrEqual(3);
  expect(result.failures).toEqual([]);
}

for (const width of [390, 1440]) {
  for (const theme of ["light", "dark"] as const) {
    test(`Aero saved app ${theme} ${width}: actual scene, send, overlays and rendered contrast`, async ({
      page,
      browserName,
    }) => {
      await mkdir(evidence, { recursive: true });
      const saved = await (
        await page.request.get(fakeAppURL + "/api/settings")
      ).json();
      let chatId: string | undefined;
      try {
        await page.clock.install();
        await page.setViewportSize({
          width,
          height: width === 390 ? 844 : 1000,
        });
        await page.emulateMedia({
          reducedMotion: "reduce",
          colorScheme: theme,
        });
        await page.goto("/");
        await expect(page.locator(".composer")).toBeVisible();
        await page.evaluate(async (theme) => {
          const path = "/src/stores/ui.ts";
          const { useUI } = await import(path);
          useUI
            .getState()
            .set({ settings: true, settingsPane: "Appearance", theme });
        }, theme);
        const dialog = page.getByRole("dialog", {
          name: "Settings",
          exact: true,
        });
        await dialog.locator('[data-palette-option="aero"]').click();
        await expect
          .poll(
            async () =>
              (
                await (
                  await page.request.get(fakeAppURL + "/api/settings")
                ).json()
              )["appearance.palette"],
          )
          .toBe("aero");
        await audit(page, `${browserName}-${theme}-${width}-settings-fake`);
        await page.keyboard.press("Escape");
        await page.reload();
        await expect(page.locator("html")).toHaveAttribute(
          "data-palette",
          "aero",
        );
        await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
        await expect(page.locator(".empty-chat .aero-scene")).toBeVisible();
        await audit(page, `${browserName}-${theme}-${width}-new-fake`);
        await page.emulateMedia({ reducedMotion: "no-preference" });
        await page.evaluate(() =>
          document
            .querySelector(".aero-scene")!
            .getAnimations({ subtree: true })
            .forEach((a) => {
              a.currentTime = 15000;
              a.pause();
            }),
        );
        await audit(page, `${browserName}-${theme}-${width}-scene-middle-fake`);
        await page.emulateMedia({ reducedMotion: "reduce" });
        await page.getByRole("button", { name: "Tools", exact: true }).click();
        await audit(page, `${browserName}-${theme}-${width}-tools-fake`);
        await page.keyboard.press("Escape");
        await page
          .locator(".composer textarea")
          .fill("Synthetic Aero integration check");
        await page
          .getByRole("button", { name: "Send message", exact: true })
          .click();
        await expect(page.getByRole("article")).toHaveCount(2);
        await expect(
          page.getByText("tokens", { exact: false }).last(),
        ).toBeVisible();
        chatId = new URL(page.url()).pathname.split("/").at(-1);
        await expect(page.locator(".aero-scene")).toHaveCount(0);
        await audit(page, `${browserName}-${theme}-${width}-thread-fake`);
        await page.goto("/workflows");
        await expect(
          page.getByRole("heading", { name: "Workflows", exact: true }),
        ).toBeVisible();
        await audit(page, `${browserName}-${theme}-${width}-workflows-fake`);
        await page.goto("/images");
        await expect(
          page.getByRole("heading", { name: "Images", exact: true }),
        ).toBeVisible();
        await audit(page, `${browserName}-${theme}-${width}-images-fake`);
        await page.goto("/design?themes");
        await expect(page.locator(".theme-lab-window")).toBeVisible();
        await audit(page, `${browserName}-${theme}-${width}-gel-controls-fake`);
      } finally {
        if (!page.isClosed()) await page.goto("about:blank");
        if (chatId) await page.request.delete(`/api/chats/${chatId}`);
        const data = Object.fromEntries(
          ["appearance.palette", "appearance.theme"].map((key) => [
            key,
            saved[key] ?? (key.endsWith("palette") ? "cobalt" : "system"),
          ]),
        );
        expect(
          (
            await page.request.patch(fakeAppURL + "/api/settings", { data })
          ).ok(),
        ).toBe(true);
      }
    });
  }
}

test("Aero animated new-chat frame diagnostic", async ({
  page,
  browserName,
}) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/design?themes");
  await page
    .getByRole("region", { name: "Controls" })
    .getByRole("button", { name: "Aero", exact: true })
    .click();
  await settle(page);
  const result = await page.evaluate(async () => {
    const frames: number[] = [];
    let previous = 0;
    for (let i = 0; i < 180; i++)
      await new Promise<void>((resolve) =>
        requestAnimationFrame((now) => {
          if (previous) frames.push(now - previous);
          previous = now;
          resolve();
        }),
      );
    frames.sort((a, b) => a - b);
    return {
      samples: frames.length,
      median_ms: frames[Math.floor(frames.length * 0.5)],
      p95_ms: frames[Math.floor(frames.length * 0.95)],
      running_animations: document
        .querySelector(".theme-lab-window .aero-scene")!
        .getAnimations({ subtree: true })
        .filter((a) => a.playState === "running").length,
      scope:
        "Desktop browser rAF diagnostic; not physical phone GPU certification",
    };
  });
  await mkdir(evidence, { recursive: true });
  await writeFile(
    resolve(evidence, `scene-frames-${browserName}.json`),
    JSON.stringify(result, null, 2),
  );
  expect(result.samples).toBe(179);
  expect(result.running_animations).toBeGreaterThan(0);
  expect(result.median_ms).toBeLessThan(20);
});

test("Rendered contrast ignores covered glyphs but rejects exposed low-contrast text", async ({
  page,
  browserName,
}) => {
  await mkdir(evidence, { recursive: true });
  await page.clock.install();
  await page.setContent(`<!doctype html><meta name="viewport" content="width=device-width, initial-scale=1"><title>Synthetic contrast control</title>
    <style>body{margin:16px;background:white;color:black;font:18px Arial}
    .covered{position:relative;width:320px;height:44px}button{width:320px;height:44px;background:#0a6fc0;color:white;border:0;font:18px Arial}
    aside{position:absolute;inset:0 0 auto;height:21.25px;background:white;color:black;font:14px Arial}
    .low{color:#eeeeee}</style>
    <h1>Contrast measurement control</h1>
    <div class="covered"><button>Partially covered</button><aside>Overlay</aside></div>
    <p class="low">Exposed low contrast</p><p>Readable control text</p>
    <p id="expiring">Readable expiring notification</p>`);
  await page.evaluate(() => {
    const notification = document.querySelector("#expiring")!;
    const observer = new MutationObserver(() => {
      if (!notification.hasAttribute("data-contrast-id")) return;
      observer.disconnect();
      setTimeout(() => notification.remove(), 10);
    });
    observer.observe(notification, { attributes: true });
  });
  const result = await measureContrast(
    page,
    `${browserName}-contrast-negative-control-fake`,
  );
  expect(result.runs.some((r) => r.text === "Partially covered")).toBe(true);
  expect(result.failures.map((r) => r.text)).toEqual(["Exposed low contrast"]);
  expect(result.failures[0].minimum).toBeLessThan(4.5);
  expect(
    result.runs.some((r) => r.text === "Readable expiring notification"),
  ).toBe(true);
  await expect(page.locator("#expiring")).toHaveCount(0);
});

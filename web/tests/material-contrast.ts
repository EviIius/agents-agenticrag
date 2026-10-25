import type { Page } from "@playwright/test";
import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { settle } from "./helpers";

export async function measureMaterialContrast(
  page: Page,
  evidence: string,
  name: string,
) {
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

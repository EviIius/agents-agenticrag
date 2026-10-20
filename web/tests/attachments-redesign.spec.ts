import { createServer, request as upstreamRequest } from "node:http";
import { fakeAppURL } from "../test-runtime";
import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { settle, enterImageMode } from "./helpers";
const dir = "../artifacts/attachments/at-a/browser";
test.use({ video: "on" });
test("native attachment input covers the touch button and desktop dialog/shortcut use one combined accept", async ({
  page,
}) => {
  await page.goto("/design?attachments");
  const input = page.locator("input.composer-file-input");
  await expect(input).toHaveAttribute(
    "accept",
    "image/*,.heic,.heif,.pdf,.docx,.txt,.csv,.wav,.m4a",
  );
  const coarse = await page.evaluate(
    () => matchMedia("(pointer: coarse)").matches,
  );
  if (coarse) {
    await input.scrollIntoViewIfNeeded();
    const box = await input.boundingBox();
    expect(box!.width).toBe(44);
    expect(box!.height).toBe(44);
    expect(
      await page.evaluate(
        ({ x, y }) => document.elementFromPoint(x, y)?.tagName,
        { x: box!.x + box!.width / 2, y: box!.y + box!.height / 2 },
      ),
    ).toBe("INPUT");
    const picker = page.waitForEvent("filechooser");
    await input.click();
    await (await picker).setFiles([]);
  } else {
    let picker = page.waitForEvent("filechooser");
    await page
      .getByRole("button", { name: "Attach files", exact: true })
      .click();
    await (await picker).setFiles([]);
    picker = page.waitForEvent("filechooser");
    await page.keyboard.press("Control+u");
    await (await picker).setFiles([]);
  }
  await expect(
    page.getByRole("menuitem", { name: "Add image", exact: true }),
  ).toHaveCount(0);
});
test("Tools keeps switches open, reports actual thinking levels, and chips turn off with focus return", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/design?attachments");
  const tools = page.getByRole("button", { name: "Tools", exact: true });
  await tools.focus();
  await page.keyboard.press("Enter");
  await page
    .getByRole("menuitemcheckbox", { name: "Library", exact: true })
    .click();
  await expect(
    page.getByRole("menuitemcheckbox", { name: "Library", exact: true }),
  ).toBeChecked();
  await page.getByRole("menuitemradio", { name: "Xhigh", exact: true }).click();
  await expect(
    page.getByRole("menuitemradio", { name: "Xhigh", exact: true }),
  ).toBeChecked();
  await page.keyboard.press("Escape");
  await expect(tools).toBeFocused();
  const box = await tools.boundingBox(),
    send = await page
      .getByRole("button", { name: "Send message", exact: true })
      .boundingBox();
  expect(Math.abs(box!.y - send!.y)).toBeLessThan(5);
  expect(
    await page
      .locator(".composer textarea")
      .evaluate((el) => getComputedStyle(el).fontSize),
  ).toBe("16px");
  await page
    .getByRole("button", { name: "Use model default thinking", exact: true })
    .click();
  await expect(tools).toBeFocused();
  await expect(
    page.getByRole("button", { name: "Think · Xhigh", exact: true }),
  ).toHaveCount(0);
  await page
    .getByRole("button", { name: "Turn Library off", exact: true })
    .click();
  await expect(tools).toBeFocused();
  await tools.focus();
  await page.keyboard.press("Space");
  await expect(
    page.getByRole("menu", { name: "Tools", exact: true }),
  ).toBeVisible();
  await page.keyboard.press("Home");
  await page.keyboard.press("ArrowDown");
  await expect(
    page.getByRole("menuitemcheckbox", { name: "Library", exact: true }),
  ).toBeFocused();
  await page.keyboard.press("ArrowUp");
  await expect(
    page.getByRole("menuitemcheckbox", { name: "Search the web", exact: true }),
  ).toBeFocused();
  await page.keyboard.press("Space");
  await expect(
    page.getByRole("menuitemcheckbox", { name: "Search the web", exact: true }),
  ).toBeChecked();
  await page
    .getByRole("menuitem", { name: "Create image", exact: true })
    .click();
  await expect(
    page.getByRole("textbox", { name: "Image prompt", exact: true }),
  ).toBeVisible();
  await expect(tools).toHaveCount(0);
  await page
    .getByRole("button", { name: "Leave image mode", exact: true })
    .click();
  await expect(tools).toBeVisible();
});
test("retained photos warn and block sending until a reported vision model is selected", async ({
  page,
}) => {
  await page.goto("/design?attachments&state=warning");
  await page.locator(".composer textarea").fill("Synthetic request");
  await expect(page.locator(".attachment-photo")).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Send message", exact: true }),
  ).toBeDisabled();
  await page.getByRole("button", { name: "Switch model", exact: true }).click();
  await expect(
    page.getByRole("menuitem", { name: "Fake text model", exact: true }),
  ).toHaveCount(0);
  await page
    .getByRole("menuitem", { name: "Fake vision model", exact: true })
    .click();
  await page.locator(".composer textarea").fill("Synthetic request");
  await expect(
    page.getByRole("button", { name: "Send message", exact: true }),
  ).toBeEnabled();
  await page.goto("/design?attachments&state=no+vision+model");
  await page.getByRole("button", { name: "Switch model", exact: true }).click();
  await expect(
    page.getByRole("menuitem", { name: "No vision models are available." }),
  ).toBeDisabled();
  const axe = await new AxeBuilder({ page }).analyze();
  expect(
    axe.violations.filter((v) =>
      ["serious", "critical"].includes(v.impact ?? ""),
    ),
  ).toEqual([]);
});
test("tray photos use the existing viewer without generation actions; cards preview real text", async ({
  page,
}) => {
  await page.goto("/design?attachments&state=ready");
  await page
    .getByRole("button", { name: "Open photo Harbor-fake.png", exact: true })
    .click();
  await expect(
    page.getByRole("dialog", { name: "Image viewer", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "More like this", exact: true }),
  ).toHaveCount(0);
  await page
    .getByRole("button", { name: "Close image viewer", exact: true })
    .click();
  await settle(page);
  await page
    .getByRole("button", {
      name: "Review document Spring-market-vendor-plan-fake-2026.pdf",
      exact: true,
    })
    .click();
  await expect(
    page.getByText("Synthetic PDF text. Nothing private.", { exact: true }),
  ).toBeVisible();
});
for (const width of [390, 1440])
  for (const theme of ["light", "dark"])
    test(`attachment states and Tools axe ${width} ${theme}`, async ({
      page,
    }, info) => {
      await page.setViewportSize({ width, height: 1000 });
      await page.emulateMedia({ colorScheme: theme as "light" | "dark" });
      await page.goto("/design?attachments");
      const results = [];
      for (const state of [
        "empty",
        "ready",
        "uploading",
        "reading",
        "warning",
        "over budget",
        "unsupported",
        "network",
        "8 files",
      ]) {
        await page
          .getByRole("button", { name: `Preview ${state}`, exact: true })
          .click();
        await settle(page);
        const axe = await new AxeBuilder({ page }).analyze();
        expect(
          axe.violations.filter((v) =>
            ["serious", "critical"].includes(v.impact ?? ""),
          ),
          state,
        ).toEqual([]);
        results.push({ state, violations: axe.violations });
        await mkdir(dir, { recursive: true });
        await page.locator(".composer").screenshot({
          path: `${dir}/${state.replaceAll(" ", "-")}-${width}-${theme}-${info.project.name}-fake.png`,
        });
      }
      await page
        .getByRole("button", { name: "Preview empty", exact: true })
        .click();
      await page.getByRole("button", { name: "Tools", exact: true }).click();
      await settle(page);
      const axe = await new AxeBuilder({ page }).analyze();
      expect(
        axe.violations.filter((v) =>
          ["serious", "critical"].includes(v.impact ?? ""),
        ),
      ).toEqual([]);
      await mkdir(dir, { recursive: true });
      await writeFile(
        `${dir}/states-${width}-${theme}-${info.project.name}-fake.json`,
        JSON.stringify(results, null, 2),
      );
      await page.screenshot({
        path: `${dir}/tools-${width}-${theme}-${info.project.name}-fake.png`,
      });
    });

async function liveUploads(
  page: import("@playwright/test").Page,
  request: import("@playwright/test").APIRequestContext,
) {
  const pending = await (await request.get("/api/attachments/pending")).json();
  for (const file of pending)
    await request.delete(`/api/attachments/${file.id}`);
  const [connection] = await (await request.get("/api/connections")).json();
  await request.patch("/api/settings", {
    data: {
      default_connection_id: connection.id,
      default_model_id: "fake-vision",
      default_preset_id: null,
      auto_title: false,
      "web.default_on": false,
    },
  });
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: "Choose model", exact: true }),
  ).toContainText("fake-vision");
}
test("photo preview appears before upload completes, Send waits, and the local URL is released after the server copy loads", async ({
  page,
  request,
}) => {
  await page.addInitScript(() => {
    const state = { created: [] as string[], revoked: [] as string[] };
    Object.assign(window, { fakeAttachmentUrls: state });
    const create = URL.createObjectURL.bind(URL),
      revoke = URL.revokeObjectURL.bind(URL);
    URL.createObjectURL = (blob) => {
      const url = create(blob);
      state.created.push(url);
      return url;
    };
    URL.revokeObjectURL = (url) => {
      state.revoked.push(url);
      revoke(url);
    };
  });
  await liveUploads(page, request);
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  // Preserve the browser's binary multipart body. Replaying WebKit's request
  // via route.fetch can change binary bytes; hold the native HTTP response instead.
  const proxy = createServer((incoming, outgoing) => {
    if (incoming.method === "OPTIONS") {
      outgoing.writeHead(204, {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Methods": "POST",
      });
      outgoing.end();
      return;
    }
    const upstream = upstreamRequest(
      new URL("/api/attachments", fakeAppURL),
      {
        method: incoming.method,
        headers: {
          ...incoming.headers,
          host: new URL(fakeAppURL).host,
          origin: fakeAppURL,
          referer: fakeAppURL + "/",
        },
      },
      (response) => {
        const chunks: Buffer[] = [];
        response.on("data", (chunk: Buffer) => chunks.push(chunk));
        response.on("end", () => {
          void gate.then(() => {
            if (outgoing.destroyed) return;
            const body = Buffer.concat(chunks);
            outgoing.writeHead(response.statusCode ?? 500, {
              "Content-Type": "application/json",
              "Content-Length": body.length,
              "Access-Control-Allow-Origin": "*",
            });
            outgoing.end(body);
          });
        });
      },
    );
    upstream.on("error", () => {
      if (!outgoing.destroyed) {
        outgoing.writeHead(502);
        outgoing.end();
      }
    });
    incoming.pipe(upstream);
  });
  await new Promise<void>((resolve) => proxy.listen(0, "127.0.0.1", resolve));
  const address = proxy.address() as import("node:net").AddressInfo;
  await page.route("**/api/attachments", async (route) => {
    if (route.request().method() !== "POST") return route.continue();
    await route.continue({
      url: `http://127.0.0.1:${address.port}/api/attachments`,
    });
  });
  try {
    await page
      .locator("input.composer-file-input")
      .setInputFiles("../server/tests/fixtures/images/fake-synthetic.png");
    await expect(page.locator(".attachment-photo img")).toBeVisible();
    await expect(page.locator(".attachment-photo img")).toHaveAttribute(
      "src",
      /^blob:/,
    );
    await page.locator(".composer textarea").fill("Synthetic request");
    await expect(
      page.getByRole("button", { name: "Send message", exact: true }),
    ).toBeDisabled();
    await expect(page.locator(".composer-send-ring")).toHaveAttribute(
      "aria-label",
      "Waiting for 1 file",
    );
    await page
      .getByRole("button", {
        name: "Open photo fake-synthetic.png",
        exact: true,
      })
      .click();
    const viewer = page.locator(".image-viewer-output");
    await expect(viewer).toHaveAttribute("src", /^blob:/);
    release();
    await expect(viewer).toHaveAttribute("src", /^\/api\/attachments\//);
    await expect(viewer).toBeVisible();
    await page
      .getByRole("button", { name: "Close image viewer", exact: true })
      .click();
    await expect(page.locator(".image-viewer")).toHaveCount(0);
    await expect(page.locator(".attachment-photo")).toHaveAttribute(
      "data-phase",
      "ready",
    );
    await expect(page.locator(".attachment-photo img")).toHaveAttribute(
      "src",
      /^\/api\/attachments\//,
    );
    await expect
      .poll(() =>
        page.evaluate(() => {
          const s = (
            window as unknown as {
              fakeAttachmentUrls: { created: string[]; revoked: string[] };
            }
          ).fakeAttachmentUrls;
          return (
            s.created.length > 0 &&
            s.created.every((url) => s.revoked.includes(url))
          );
        }),
      )
      .toBe(true);
    await expect(
      page.getByRole("button", { name: "Send message", exact: true }),
    ).toBeEnabled();
  } finally {
    release();
    proxy.closeAllConnections();
    await new Promise<void>((resolve) => proxy.close(() => resolve()));
  }
});
test("network errors stay on their file, allow ordinary sending, and retry the original file", async ({
  page,
  request,
}) => {
  await liveUploads(page, request);
  let attempts = 0;
  await page.route("**/api/attachments", async (route) => {
    if (route.request().method() !== "POST") return route.continue();
    attempts++;
    if (attempts === 1) await route.abort("failed");
    else await route.continue();
  });
  await page.locator("input.composer-file-input").setInputFiles({
    name: "Network-fake.txt",
    mimeType: "text/plain",
    buffer: Buffer.from("Synthetic retry content"),
  });
  await expect(page.locator(".attachment-status")).toContainText(
    "didn't finish uploading",
  );
  await expect(page.locator("[data-sonner-toast]")).toHaveCount(0);
  await page
    .locator(".composer textarea")
    .fill("Synthetic request without the failed file");
  await expect(
    page.getByRole("button", { name: "Send message", exact: true }),
  ).toBeEnabled();
  await page.locator(".attachment-retry").click();
  await expect(page.locator(".attachment-tile")).toHaveAttribute(
    "data-phase",
    "ready",
  );
  expect(attempts).toBe(2);
});
test("the eight-file limit counts ready and pending files together without attaching the ninth file", async ({
  page,
  request,
}) => {
  await liveUploads(page, request);
  let requests = 0;
  page.on("request", (r) => {
    if (r.method() === "POST" && r.url().endsWith("/api/attachments"))
      requests++;
  });
  await page.locator("input.composer-file-input").setInputFiles(
    Array.from({ length: 9 }, (_, i) => ({
      name: `Notes-${i + 1}-fake.txt`,
      mimeType: "text/plain",
      buffer: Buffer.from(`Synthetic ${i}`),
    })),
  );
  await expect(page.locator(".attachment-count")).toHaveText("8 of 8");
  await expect(page.locator("input.composer-file-input")).toBeDisabled();
  await expect(page.locator(".attachment-status")).toContainText(
    "8 files is the limit for one message",
  );
  await expect(page.locator(".attachment-tile[data-phase=ready]")).toHaveCount(
    8,
  );
  expect(requests).toBe(8);
});
test("cancelling an individual photo aborts its transport and releases the thumbnail URL", async ({
  page,
  request,
}) => {
  await page.addInitScript(() => {
    const revoked: string[] = [];
    Object.assign(window, { fakeRevokedUrls: revoked });
    const revoke = URL.revokeObjectURL.bind(URL);
    URL.revokeObjectURL = (url) => {
      revoked.push(url);
      revoke(url);
    };
  });
  await liveUploads(page, request);
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route("**/api/attachments", async (route) => {
    if (route.request().method() !== "POST") return route.continue();
    await gate;
    await route.abort("aborted").catch(() => {});
  });
  try {
    await page
      .locator("input.composer-file-input")
      .setInputFiles("../server/tests/fixtures/images/fake-synthetic.png");
    const img = page.locator(".attachment-photo img");
    await expect(img).toHaveAttribute("src", /^blob:/);
    const url = await img.getAttribute("src");
    await page
      .getByRole("button", {
        name: "Cancel upload fake-synthetic.png",
        exact: true,
      })
      .click();
    await expect(page.locator(".attachment-photo")).toHaveCount(0);
    expect(
      await page.evaluate(
        () =>
          (window as unknown as { fakeRevokedUrls: string[] }).fakeRevokedUrls,
      ),
    ).toContain(url);
    await page
      .locator(".composer textarea")
      .fill("Synthetic request after cancellation");
    await expect(
      page.getByRole("button", { name: "Send message", exact: true }),
    ).toBeEnabled();
  } finally {
    release();
  }
});

test("portrait attachments zoom to actual pixels using their longest dimension", async ({
  page,
  request,
}) => {
  await liveUploads(page, request);
  const data = await page.evaluate(() => {
    const canvas = document.createElement("canvas");
    canvas.width = 800;
    canvas.height = 1600;
    const ctx = canvas.getContext("2d")!;
    ctx.fillStyle = "#586c85";
    ctx.fillRect(0, 0, 800, 1600);
    return canvas.toDataURL("image/png").split(",")[1];
  });
  await page.locator("input.composer-file-input").setInputFiles({
    name: "Portrait-fake.png",
    mimeType: "image/png",
    buffer: Buffer.from(data, "base64"),
  });
  await expect(page.locator(".attachment-photo")).toHaveAttribute(
    "data-phase",
    "ready",
  );
  await page
    .getByRole("button", { name: "Open photo Portrait-fake.jpg", exact: true })
    .click();
  const img = page.locator(".image-viewer-output");
  await expect
    .poll(() => img.evaluate((el: HTMLImageElement) => el.naturalHeight))
    .toBe(1600);
  await page
    .getByRole("button", { name: "Zoom to actual size", exact: true })
    .click();
  const expected = await page
    .locator(".image-viewer-fit")
    .evaluate((el) =>
      (1600 / parseFloat(getComputedStyle(el).width)).toFixed(2),
    );
  await expect(page.locator(".image-viewer-stage")).toHaveAttribute(
    "data-zoom",
    expected,
  );
  await settle(page);
  expect(
    await img.evaluate((el) => el.getBoundingClientRect().height),
  ).toBeGreaterThanOrEqual(1599);
});

test("a dropped upload error reveals its tray from Image mode without losing the image draft", async ({
  page,
  request,
}) => {
  await liveUploads(page, request);
  await enterImageMode(page);
  await page
    .getByRole("textbox", { name: "Image prompt", exact: true })
    .fill("Synthetic preserved image draft");
  await page.locator(".app-main").evaluate((el) => {
    const transfer = new DataTransfer();
    transfer.items.add(
      new File(["fake broken image"], "Dropped-broken-fake.png", {
        type: "image/png",
      }),
    );
    el.dispatchEvent(
      new DragEvent("drop", {
        bubbles: true,
        cancelable: true,
        dataTransfer: transfer,
      }),
    );
  });
  await expect(
    page.getByRole("button", { name: "Leave image mode", exact: true }),
  ).toHaveCount(0);
  await expect(page.locator(".attachment-status")).toContainText(
    "Couldn't open this image",
  );
  await expect(page.locator("[data-sonner-toast]")).toHaveCount(0);
  await enterImageMode(page);
  await expect(
    page.getByRole("textbox", { name: "Image prompt", exact: true }),
  ).toHaveValue("Synthetic preserved image draft");
});

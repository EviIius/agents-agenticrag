import {
  test,
  expect,
  type Page,
  type APIRequestContext,
} from "@playwright/test";
import { readFile, mkdir, writeFile } from "node:fs/promises";
import { settle } from "./helpers";
const dir = "../artifacts/attachments/at-b";
test.use({ video: "on" });
async function setup(page: Page, request: APIRequestContext) {
  for (const file of await (
    await request.get("/api/attachments/pending")
  ).json())
    await request.delete(`/api/attachments/${file.id}`);
  const connection = (await (await request.get("/api/connections")).json())[0];
  await request.patch("/api/settings", {
    data: {
      default_connection_id: connection.id,
      default_model_id: "fake-vision",
      default_preset_id: null,
      auto_title: false,
      "appearance.reduce_motion": "system",
    },
  });
  const chat = await (
    await request.post("/api/chats", {
      data: { connection_id: connection.id, model_id: "fake-vision" },
    })
  ).json();
  await page.goto(`/c/${chat.id}`);
  await expect(page.locator(".composer textarea")).toBeVisible();
  return chat.id as string;
}
async function clipboard(page: Page, text?: string, image?: number[]) {
  return page.locator(".composer textarea").evaluate(
    (element, data) => {
      const transfer = new DataTransfer();
      if (data.text != null) transfer.setData("text/plain", data.text);
      if (data.image)
        transfer.items.add(
          new File([new Uint8Array(data.image)], "Clipboard-photo-fake.png", {
            type: "image/png",
          }),
        );
      const event = new ClipboardEvent("paste", {
        clipboardData: transfer,
        bubbles: true,
        cancelable: true,
      });
      element.dispatchEvent(event);
      return event.defaultPrevented;
    },
    { text, image },
  );
}
test("drop card, composer target, escape and other routes preserve the upload boundary", async ({
  page,
  request,
}) => {
  await setup(page, request);
  let posts = 0;
  page.on("request", (r) => {
    if (r.method() === "POST" && r.url().endsWith("/api/attachments")) posts++;
  });
  const transfer = await page.evaluateHandle(() => {
    const d = new DataTransfer();
    d.items.add(
      new File(["Synthetic fake drop"], "Dropped-fake.txt", {
        type: "text/plain",
      }),
    );
    return d;
  });
  const main = page.locator("main.app-main");
  await main.dispatchEvent("dragenter", { dataTransfer: transfer });
  await expect(
    page.getByRole("heading", { name: "Drop to attach", exact: true }),
  ).toBeVisible();
  await page.locator(".composer textarea").dispatchEvent("dragenter", {
    dataTransfer: transfer,
  });
  await page.locator(".composer textarea").dispatchEvent("dragleave", {
    dataTransfer: transfer,
  });
  await expect(page.locator('[data-slot="drop-overlay"]')).toBeVisible();
  await main.dispatchEvent("dragleave", { dataTransfer: transfer });
  await expect(page.locator('[data-slot="drop-overlay"]')).toHaveCount(0);
  await main.dispatchEvent("dragenter", { dataTransfer: transfer });
  await page
    .locator(".composer textarea")
    .dispatchEvent("dragover", { dataTransfer: transfer });
  await expect(main).toHaveAttribute("data-drop-target", "true");
  expect(
    await page
      .locator(".composer")
      .evaluate((el) => Number(getComputedStyle(el).zIndex)),
  ).toBeGreaterThan(30);
  await page.keyboard.press("Escape");
  await expect(page.locator('[data-slot="drop-overlay"]')).toHaveCount(0);
  await main.dispatchEvent("dragover", { dataTransfer: transfer });
  await expect(main).not.toHaveAttribute("data-drop-target");
  expect(posts).toBe(0);
  await main.dispatchEvent("dragenter", { dataTransfer: transfer });
  await main.dispatchEvent("drop", { dataTransfer: transfer });
  await expect(
    page.getByRole("button", {
      name: "Review file Dropped-fake.txt",
      exact: true,
    }),
  ).toBeVisible();
  expect(posts).toBe(1);
  const settings = page
    .getByRole("button", { name: "Settings", exact: true })
    .filter({ visible: true })
    .first();
  if (!(await settings.isVisible()))
    await page
      .getByRole("button", { name: "Open sidebar", exact: true })
      .click();
  await settings.click();
  await main.dispatchEvent("dragenter", { dataTransfer: transfer });
  await main.dispatchEvent("drop", { dataTransfer: transfer });
  await expect(page.locator('[data-slot="drop-overlay"]')).toHaveCount(0);
  expect(posts).toBe(1);
  await page.keyboard.press("Escape");
  await page.goto("/workflows");
  const workspaceTransfer = await page.evaluateHandle(() => {
    const d = new DataTransfer();
    d.items.add(
      new File(["Synthetic fake drop"], "Dropped-fake.txt", {
        type: "text/plain",
      }),
    );
    return d;
  });
  await page
    .locator("main.app-main")
    .dispatchEvent("dragenter", { dataTransfer: workspaceTransfer });
  await page
    .locator("main.app-main")
    .dispatchEvent("drop", { dataTransfer: workspaceTransfer });
  await expect(page.locator('[data-slot="drop-overlay"]')).toHaveCount(0);
  expect(posts).toBe(1);
});
test("pasted photos use the upload pipeline; long-paste undo preserves new typing and removes the file", async ({
  page,
  request,
}) => {
  await setup(page, request);
  const png = [
    ...(await readFile("../server/tests/fixtures/images/fake-synthetic.png")),
  ];
  const uploaded = page.waitForResponse(
    (r) =>
      r.url().endsWith("/api/attachments") && r.request().method() === "POST",
  );
  expect(await clipboard(page, undefined, png)).toBe(true);
  const photo = await (await uploaded).json();
  expect(photo.filename).toMatch(/^Pasted image 1\.(png|jpg)$/);
  await expect(
    page.getByRole("button", {
      name: `Open photo ${photo.filename}`,
      exact: true,
    }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: `Remove ${photo.filename}`, exact: true })
    .click();
  const field = page.locator(".composer textarea");
  await field.fill("Before: ");
  expect(await clipboard(page, "s".repeat(4000))).toBe(false);
  await expect(
    page.getByRole("button", { name: "Keep as text", exact: true }),
  ).toHaveCount(0);
  const raw = "Synthetic long paste fake. ".repeat(200);
  const pasted = page.waitForResponse(
    (r) =>
      r.url().endsWith("/api/attachments") && r.request().method() === "POST",
  );
  expect(await clipboard(page, raw)).toBe(true);
  const file = await (await pasted).json();
  await expect(
    page.getByRole("button", {
      name: "Review file Pasted text 1.txt",
      exact: true,
    }),
  ).toBeVisible();
  await expect(page.locator(".attachment-meta")).toContainText(
    `${raw.length.toLocaleString()} characters`,
  );
  await field.fill("New typing: ");
  const removed = page.waitForResponse(
    (r) =>
      r.url().endsWith(`/api/attachments/${file.id}`) &&
      r.request().method() === "DELETE",
  );
  await page.getByRole("button", { name: "Keep as text", exact: true }).click();
  expect((await removed).ok()).toBe(true);
  await expect(field).toHaveValue("New typing: " + raw);
  await expect(field).toBeFocused();
  await expect(
    page.getByRole("button", {
      name: "Review file Pasted text 1.txt",
      exact: true,
    }),
  ).toHaveCount(0);
  expect(
    await (await request.get(`/api/attachments/${file.id}/info`)).status(),
  ).toBe(404);
});
test("long-paste undo cancels an in-flight upload, restores the selection and expires after ten seconds", async ({
  page,
  request,
}) => {
  await page.clock.install();
  await setup(page, request);
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route("**/api/attachments", async (route) => {
    if (route.request().method() !== "POST") return route.continue();
    await gate;
    await route.continue().catch(() => undefined);
  });
  const field = page.locator(".composer textarea");
  await field.fill("Before selected after");
  await field.evaluate((el) => {
    el.focus();
    (el as HTMLTextAreaElement).setSelectionRange(7, 15);
  });
  const raw = "Synthetic fake text. ".repeat(250);
  await clipboard(page, raw);
  await expect(
    page.getByRole("button", {
      name: "Cancel upload Pasted text 1.txt",
      exact: true,
    }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Keep as text", exact: true }).click();
  await expect(field).toHaveValue("Before " + raw + " after");
  await expect(
    page.getByRole("button", {
      name: "Cancel upload Pasted text 1.txt",
      exact: true,
    }),
  ).toHaveCount(0);
  release();
  await page.unroute("**/api/attachments");
  await field.fill("Review synthetic fake text.");
  await clipboard(page, raw);
  await expect(
    page.getByRole("button", {
      name: "Review file Pasted text 2.txt",
      exact: true,
    }),
  ).toBeVisible();
  await page.clock.runFor(10500);
  await expect(
    page.getByRole("button", { name: "Keep as text", exact: true }),
  ).toHaveCount(0);
  await expect(
    page.getByRole("button", {
      name: "Review file Pasted text 2.txt",
      exact: true,
    }),
  ).toBeVisible();
});
test("an accepted earlier send preserves a newer paste and undo remains available during streaming", async ({
  page,
  request,
}) => {
  await page.clock.install();
  const chat = await setup(page, request);
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route(`**/api/chats/${chat}/messages`, async (route) => {
    await gate;
    await route.continue();
  });
  const field = page.locator(".composer textarea");
  const original = "#long:600 #slow:50 Synthetic fake earlier send.";
  await field.fill(original);
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  await expect(page.getByTestId("optimistic-send")).toBeVisible();
  await field.fill("New draft: ");
  const raw = "Synthetic later paste fake. ".repeat(200);
  await clipboard(page, raw);
  await expect(
    page.getByRole("button", {
      name: "Review file Pasted text 1.txt",
      exact: true,
    }),
  ).toBeVisible();
  const keep = page.getByRole("button", { name: "Keep as text", exact: true });
  await expect(keep).toBeDisabled();
  await page.clock.runFor(10500);
  await expect(keep).toBeVisible();
  const sent = page.waitForResponse(
    (r) =>
      r.url().endsWith(`/api/chats/${chat}/messages`) &&
      r.request().method() === "POST",
  );
  release();
  const response = await sent;
  expect(response.request().postDataJSON().content).toBe(original);
  expect(response.request().postDataJSON().attachment_ids).toEqual([]);
  await expect(
    page.getByRole("button", { name: "Stop generating", exact: true }),
  ).toBeVisible();
  await expect(keep).toBeEnabled();
  await keep.click();
  await expect(field).toHaveValue("New draft: " + raw);
  await page
    .getByRole("button", { name: "Stop generating", exact: true })
    .click();
});
test("optimistic and confirmed attachments retain previews, real request fields and durable history", async ({
  page,
  request,
}) => {
  const chat = await setup(page, request);
  let releaseImages!: () => void, releaseSend!: () => void;
  const images = new Promise<void>((resolve) => {
    releaseImages = resolve;
  });
  const send = new Promise<void>((resolve) => {
    releaseSend = resolve;
  });
  await page.route("**/api/attachments/*", async (route) => {
    if (route.request().resourceType() === "image") await images;
    await route.continue().catch(() => undefined);
  });
  await page.route(`**/api/chats/${chat}/messages`, async (route) => {
    await send;
    await route.continue();
  });
  const png = await readFile(
    "../server/tests/fixtures/images/fake-synthetic.png",
  );
  const uploaded = page.waitForResponse(
    (r) =>
      r.url().endsWith("/api/attachments") && r.request().method() === "POST",
  );
  await page.locator('input[type="file"]').setInputFiles({
    name: "Harbor-send-fake.png",
    mimeType: "image/png",
    buffer: png,
  });
  const attachment = await (await uploaded).json();
  await expect(
    page.getByRole("button", {
      name: `Open photo ${attachment.filename}`,
      exact: true,
    }),
  ).toBeVisible();
  await page
    .locator(".composer textarea")
    .fill("Describe the synthetic fake photo.");
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  const optimistic = page.getByTestId("optimistic-send");
  await expect(optimistic.locator(".message-photo img")).toBeVisible();
  const preview = await optimistic
    .locator(".message-photo img")
    .getAttribute("src");
  expect(preview).toMatch(/^blob:/);
  const sent = page.waitForResponse(
    (r) =>
      r.url().endsWith(`/api/chats/${chat}/messages`) &&
      r.request().method() === "POST",
  );
  releaseSend();
  const response = await sent;
  expect(response.ok()).toBe(true);
  const body = response.request().postDataJSON();
  expect(body).toEqual({
    content: "Describe the synthetic fake photo.",
    parent_id: null,
    attachment_ids: [attachment.id],
    web: false,
  });
  await expect(optimistic).toHaveCount(0);
  const photo = page
    .getByRole("article", { name: "user message", exact: true })
    .locator(".message-photo img");
  await expect(photo).toHaveAttribute("src", preview!);
  await expect(photo).toHaveJSProperty("complete", true);
  releaseImages();
  await expect(photo).toHaveAttribute(
    "src",
    `/api/attachments/${attachment.id}`,
  );
  await expect(photo).toHaveJSProperty("complete", true);
  await page.unroute("**/api/attachments/*");
  await page.reload();
  await expect(photo).toBeVisible();
  await expect(
    page.getByRole("article", { name: "user message", exact: true }),
  ).not.toHaveAttribute("data-fresh");
  await expect(photo).toHaveAttribute("loading", "lazy");
  await expect(photo).toHaveAttribute("decoding", "async");
  const saved = await (await request.get(`/api/chats/${chat}`)).json();
  expect(
    saved.messages.find((m: { role: string }) => m.role === "user")
      .attachments[0].id,
  ).toBe(attachment.id);
});
test("sent photo sets, document/text/recording sheets and delayed image boxes use production controls", async ({
  page,
}) => {
  await page.goto("/design?attachment-thread&state=sent-7");
  await expect(page.locator(".message-photo")).toHaveCount(6);
  await expect(page.locator(".message-photo-more")).toHaveText("+1");
  await page.locator(".message-photo").last().click();
  await expect(
    page.getByRole("dialog", { name: "Image viewer", exact: true }),
  ).toBeVisible();
  await page.keyboard.press("ArrowRight");
  await expect(page.getByRole("dialog")).toContainText("Harbor-7-fake.png");
  await page.keyboard.press("Escape");
  await page.getByRole("button", { name: "Preview pdf", exact: true }).click();
  await expect(
    page.getByText("Synthetic PDF text. Nothing private.", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Close document", exact: true })
    .click();
  await page.getByRole("button", { name: "Preview text", exact: true }).click();
  await expect(
    page.getByText("stall,price\nFake stall,40", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Close document", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Preview transcript", exact: true })
    .click();
  await expect(
    page.getByRole("button", { name: "Close transcript", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Close transcript", exact: true })
    .click();
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route("**/api/attachments/fake-photo-1", async (route) => {
    await gate;
    await route.fulfill({
      contentType: "image/svg+xml",
      body: '<svg xmlns="http://www.w3.org/2000/svg" width="120" height="400"><rect width="120" height="400" fill="blue"/></svg>',
    });
  });
  await page
    .getByRole("button", { name: "Preview loading", exact: true })
    .click();
  await page.locator(".message-photo").scrollIntoViewIfNeeded();
  await settle(page);
  const box = await page.locator(".message-photo").boundingBox();
  const bubble = await page.locator(".user-bubble").boundingBox();
  expect(box!.width).toBeLessThanOrEqual(240);
  expect(box!.height).toBe(box!.width);
  release();
  await expect(page.locator(".message-photo img")).toHaveJSProperty(
    "complete",
    true,
  );
  await expect(page.locator(".message-photo img")).toHaveJSProperty(
    "naturalHeight",
    400,
  );
  expect(await page.locator(".message-photo").boundingBox()).toEqual(box);
  expect(await page.locator(".user-bubble").boundingBox()).toEqual(bubble);
  await mkdir(dir, { recursive: true });
  await writeFile(
    `${dir}/layout-${test.info().project.name}-fake.json`,
    JSON.stringify(
      {
        reserved: box,
        bubble,
        after: await page.locator(".message-photo").boundingBox(),
      },
      null,
      2,
    ),
  );
});
test("drop badges really move and both reduced-motion triggers make the whole drop surface static", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.goto("/design?attachment-thread&state=drop");
  await expect(
    page.getByRole("heading", { name: "Drop to attach", exact: true }),
  ).toBeVisible();
  await settle(page);
  const badge = page.locator(".attachment-drop-fan .attachment-badge").first();
  const transforms = await badge.evaluate(
    (el) =>
      new Promise<string[]>((resolve) => {
        const values: string[] = [],
          start = performance.now();
        function sample() {
          values.push(getComputedStyle(el).transform);
          if (performance.now() - start < 250) requestAnimationFrame(sample);
          else resolve(values);
        }
        sample();
      }),
  );
  expect(new Set(transforms).size).toBeGreaterThan(3);
  for (const trigger of ["system", "always"]) {
    await page.emulateMedia({
      reducedMotion: trigger === "system" ? "reduce" : "no-preference",
    });
    if (trigger === "always")
      await page
        .getByRole("button", { name: "Reduce motion", exact: true })
        .click();
    expect(
      await page
        .locator(".attachment-drop")
        .evaluate(
          (el) =>
            el
              .getAnimations({ subtree: true })
              .filter((a) => a.playState === "running").length,
        ),
    ).toBe(0);
  }
});

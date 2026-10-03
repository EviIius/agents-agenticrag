import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, readFile } from "node:fs/promises";

const evidence = "../artifacts/phase-t";
test.afterEach(async ({ request }) => {
  const pending = await (await request.get("/api/attachments/pending")).json();
  for (const item of pending) {
    const removed = await request.delete(`/api/attachments/${item.id}`);
    expect(removed.ok()).toBeTruthy();
  }
});
test.beforeEach(async ({ page, request }) => {
  const pending = await (await request.get("/api/attachments/pending")).json();
  for (const item of pending)
    await request.delete(`/api/attachments/${item.id}`);
  await request.patch("/api/settings", {
    data: { default_model_id: "fake-chat" },
  });
  await page.addInitScript(() => {
    Object.defineProperty(navigator, "share", {
      configurable: true,
      value: undefined,
    });
    Object.defineProperty(navigator, "canShare", {
      configurable: true,
      value: undefined,
    });
  });
  await page.goto("/");
  await page.getByRole("button", { name: "Add attachment" }).click();
  await expect(
    page.getByRole("menuitem", { name: "Add recording", exact: true }),
  ).toBeVisible();
  await page.keyboard.press("Escape");
  await page.locator('input[type="file"]').setInputFiles({
    name: "Synthetic recording.wav",
    mimeType: "audio/wav",
    buffer: Buffer.from("fake"),
  });
  await expect(
    page.getByRole("button", {
      name: "Open transcript for Synthetic recording.wav",
    }),
  ).toBeVisible({ timeout: 12000 });
});
async function openDownload(
  page: import("@playwright/test").Page,
  name = "Download text",
) {
  await page
    .getByRole("button", {
      name: "Recording actions for Synthetic recording.wav",
    })
    .click();
  await page.getByRole("menuitem", { name, exact: true }).click();
  return page.getByRole("dialog", { name: "Save recording" });
}

test("format choice, cancel and downloads retain Workbench", async ({
  page,
}) => {
  let downloads = 0;
  page.on("download", () => downloads++);
  const original = page.url();
  let dialog = await openDownload(page);
  await dialog
    .getByRole("button", { name: "Details (.json)", exact: true })
    .click();
  await expect(
    dialog.getByRole("link", { name: "Download file" }),
  ).toBeVisible();
  await expect(dialog.getByLabel("Download filename")).toHaveText(
    "Synthetic recording.json",
  );
  await dialog.getByRole("button", { name: "Cancel", exact: true }).click();
  await expect(dialog).toHaveCount(0);
  expect(downloads).toBe(0);
  for (const [format, label] of [
    ["txt", "Text (.txt)"],
    ["srt", "Subtitles (.srt)"],
    ["json", "Details (.json)"],
  ]) {
    dialog = await openDownload(page);
    await dialog.getByRole("button", { name: label, exact: true }).click();
    const link = dialog.getByRole("link", { name: "Download file" });
    await expect(link).toBeVisible();
    await expect(link).toHaveAttribute("target", "_blank");
    const downloadReady = page.waitForEvent("download");
    await link.click();
    const saved = await downloadReady;
    expect(saved.suggestedFilename()).toBe(`Synthetic recording.${format}`);
    const content = await readFile((await saved.path())!, "utf8");
    expect(content).toContain("Fake transcript");
    if (format === "srt") expect(content).toContain("-->");
    if (format === "json")
      expect(JSON.parse(content).segments.length).toBeGreaterThan(0);
    await expect(
      dialog.getByRole("button", { name: "Close recording download" }),
    ).toBeVisible();
    await expect(page).toHaveURL(original);
    await dialog
      .getByRole("button", { name: "Close recording download" })
      .click();
  }
});

test("native save cancellation permits a different format without a fallback download", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(() => {
    let count = 0;
    Object.defineProperty(navigator, "canShare", {
      configurable: true,
      value: () => true,
    });
    Object.defineProperty(navigator, "share", {
      configurable: true,
      value: async (data: ShareData) => {
        count++;
        const file = data.files![0];
        document.documentElement.dataset.shareCount = String(count);
        document.documentElement.dataset.shareName = file.name;
        document.documentElement.dataset.shareActive = String(
          navigator.userActivation?.isActive ?? true,
        );
        document.documentElement.dataset.shareText = await file.text();
        if (count === 1) throw new DOMException("Cancelled", "AbortError");
      },
    });
  });
  let downloads = 0;
  page.on("download", () => downloads++);
  const original = page.url();
  const dialog = await openDownload(page);
  await dialog.getByRole("button", { name: "Save or share" }).click();
  await expect(
    dialog.getByText("Save cancelled. You can choose another format or close."),
  ).toBeVisible();
  expect(downloads).toBe(0);
  await dialog
    .getByRole("button", { name: "Details (.json)", exact: true })
    .click();
  await expect(dialog.getByLabel("Download filename")).toHaveText(
    "Synthetic recording.json",
  );
  await dialog.getByRole("button", { name: "Save or share" }).click();
  await expect(
    dialog.getByText(
      "Returned from the save sheet. You can choose another format or close.",
    ),
  ).toBeVisible();
  const shared = await page.evaluate(() => ({
    ...document.documentElement.dataset,
  }));
  expect(shared.shareCount).toBe("2");
  expect(shared.shareName).toBe("Synthetic recording.json");
  expect(shared.shareActive).toBe("true");
  expect(JSON.parse(shared.shareText!).text).toContain("Fake transcript");
  expect(downloads).toBe(0);
  await expect(page).toHaveURL(original);
  await page.evaluate(() =>
    Object.defineProperty(navigator, "share", {
      configurable: true,
      value: async () => {
        throw new DOMException("Unsupported host", "NotAllowedError");
      },
    }),
  );
  await dialog.getByRole("button", { name: "Save or share" }).click();
  await expect(
    dialog.getByText(
      "Couldn't open the save sheet. Try again or download separately.",
    ),
  ).toBeVisible();
  await expect(
    dialog.getByRole("link", { name: "Download separately" }),
  ).toBeVisible();
  expect(downloads).toBe(0);
  await dialog.getByRole("button", { name: "Cancel", exact: true }).click();
});

test("preparation failure, retry and original audio remain cancellable", async ({
  page,
}) => {
  await page.route("**/transcript/download?*", (route) =>
    route.fulfill({ status: 503, body: "Synthetic failure" }),
  );
  let dialog = await openDownload(page);
  await expect(dialog.getByRole("alert")).toContainText(
    "Couldn't prepare this file",
  );
  await expect(
    dialog.getByRole("button", { name: "Cancel", exact: true }),
  ).toBeEnabled();
  await page.unroute("**/transcript/download?*");
  await dialog.getByRole("button", { name: "Retry", exact: true }).click();
  await expect(
    dialog.getByRole("link", { name: "Download file" }),
  ).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(dialog).toHaveCount(0);
  let audioRequests = 0;
  page.on("request", (request) => {
    if (
      /\/api\/attachments\/[^/]+$/.test(request.url()) &&
      request.method() === "GET"
    )
      audioRequests++;
  });
  dialog = await openDownload(page, "Download audio");
  await expect(
    dialog.getByRole("button", { name: "Original audio", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
  await expect(dialog.getByLabel("Download filename")).toHaveText(
    "Synthetic recording.wav",
  );
  expect(audioRequests).toBe(0);
  const link = dialog.getByRole("link", { name: "Download file" });
  await expect(link).toHaveAttribute("target", "_blank");
  const downloadReady = page.waitForEvent("download");
  await link.click();
  expect((await downloadReady).suggestedFilename()).toBe(
    "Synthetic recording.wav",
  );
  await dialog.getByRole("button", { name: "Cancel", exact: true }).click();
});

for (const width of [320, 390, 1440])
  for (const theme of ["light", "dark"]) {
    test(`save dialog and nested transcript ${width} ${theme}`, async ({
      page,
      request,
    }) => {
      await request.patch("/api/settings", {
        data: { "appearance.theme": theme },
      });
      await page.reload();
      await page.setViewportSize({ width, height: 844 });
      if (width < 640)
        await page.evaluate(() => {
          document.documentElement.style.setProperty("--safe-area-top", "47px");
          document.documentElement.style.setProperty(
            "--safe-area-bottom",
            "34px",
          );
        });
      await page
        .getByRole("button", {
          name: "Open transcript for Synthetic recording.wav",
        })
        .click();
      await page.getByRole("button", { name: "Download", exact: true }).click();
      const dialog = page.getByRole("dialog", { name: "Save recording" });
      await expect(
        dialog.getByRole("link", { name: "Download file" }),
      ).toBeVisible();
      const close = dialog.getByRole("button", {
        name: "Close recording download",
      });
      const cancel = dialog.getByRole("button", {
        name: "Cancel",
        exact: true,
      });
      await expect(close).toBeInViewport({ ratio: 1 });
      await expect(cancel).toBeInViewport({ ratio: 1 });
      expect(
        await close.evaluate(
          (element) => element.getBoundingClientRect().height,
        ),
      ).toBeGreaterThanOrEqual(44);
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBe(true);
      await mkdir(evidence, { recursive: true });
      await page.screenshot({
        animations: "disabled",
        path: `${evidence}/mobile-save-${width}-${theme}-fake.png`,
      });
      const axe = await new AxeBuilder({ page }).analyze();
      expect(
        axe.violations.filter((v) =>
          ["serious", "critical"].includes(v.impact ?? ""),
        ),
      ).toEqual([]);
      if (width < 640) {
        await page.setViewportSize({ width, height: 480 });
        await expect(close).toBeInViewport({ ratio: 1 });
        await expect(cancel).toBeInViewport({ ratio: 1 });
      }
      await cancel.click();
      await expect(dialog).toHaveCount(0);
      await expect(
        page.getByRole("button", { name: "Close transcript" }),
      ).toBeInViewport({ ratio: 1 });
      await page.getByRole("button", { name: "Close transcript" }).click();
      await expect(page.getByTestId("audio-chip")).toBeVisible();
    });
  }

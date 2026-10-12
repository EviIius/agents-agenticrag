import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { fakeAppURL } from "../test-runtime";
import { settle } from "./helpers";
const dir = "../artifacts/composer-workflows/browser/workflows";

test.beforeEach(async ({ request }) => {
  const connection = (await (await request.get("/api/connections")).json())[0];
  await request.put("/api/models/prefs", {
    data: {
      connection_id: connection.id,
      model_id: "fake-chat",
      display_name: "fake-chat",
      params: {},
      context_length: 16384,
    },
  });
});

for (const width of [390, 1440])
  for (const theme of ["light", "dark"]) {
    test(`Workflow synthetic states ${width} ${theme}`, async ({
      page,
      browserName,
    }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.goto("/design?workflows");
      await page.getByRole("button", { name: theme, exact: true }).click();
      await mkdir(dir, { recursive: true });
      const results = [];
      for (const state of [
        "empty",
        "queued",
        "running",
        "paused",
        "complete",
        "failed",
        "cancelling",
        "cancelled",
        "interrupted",
        "meeting-running",
        "meeting-complete",
        "uploading",
        "upload-failed",
        "cleanup-failed",
      ]) {
        await page.getByRole("button", { name: state, exact: true }).click();
        await settle(page);
        expect(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
        ).toBeTruthy();
        const scan = await new AxeBuilder({ page }).analyze();
        expect(
          scan.violations.filter((v) =>
            ["serious", "critical"].includes(v.impact ?? ""),
          ),
          state,
        ).toEqual([]);
        results.push({ state, seriousCritical: 0 });
        await page.screenshot({
          path: `${dir}/${state}-${width}-${theme}-${browserName}-fake.png`,
          fullPage: true,
        });
      }
      await page
        .getByRole("button", { name: "View original transcript" })
        .click();
      await expect(
        page.getByRole("dialog", { name: "Original transcript" }),
      ).toContainText("Synthetic source");
      await page
        .getByText("Original source timestamps", { exact: true })
        .click();
      await expect(page.getByText("0.2s–2.8s", { exact: true })).toBeVisible();
      await page.screenshot({
        path: `${dir}/source-timeline-${width}-${theme}-${browserName}-fake.png`,
        fullPage: true,
      });
      await page.keyboard.press("Escape");
      await page.getByRole("button", { name: "Save outputs" }).click();
      const dialog = page.getByRole("dialog", {
        name: "Save workflow outputs",
      });
      await dialog
        .getByRole("button", { name: "Details and source (.json)" })
        .click();
      await expect(
        dialog.getByRole("button", { name: "Details and source (.json)" }),
      ).toHaveAttribute("aria-pressed", "true");
      await page.screenshot({
        path: `${dir}/save-json-${width}-${theme}-${browserName}-fake.png`,
        fullPage: true,
      });
      await page.keyboard.press("Escape");
      await writeFile(
        `${dir}/axe-${width}-${theme}-${browserName}.json`,
        JSON.stringify(results, null, 2),
      );
    });
  }

test("Creative workflow review, reconnect, variants and cancellable saving", async ({
  page,
}) => {
  await page.goto("/workflows");
  await page
    .getByRole("textbox", { name: "Image brief" })
    .fill("Synthetic browser workflow: one blue circle on a white background");
  await page
    .getByRole("button", { name: "Configure Draft image prompt", exact: true })
    .click();
  await page.getByRole("combobox", { name: "Prompt draft model" }).click();
  await page.getByRole("option").filter({ hasText: "fake-chat" }).click();
  await page
    .getByRole("button", { name: "Configure Generate images", exact: true })
    .click();
  await page.getByText("Advanced seeds", { exact: true }).click();
  await page
    .getByRole("textbox", { name: "Image variant seeds" })
    .fill("901,902");
  await page
    .getByRole("button", { name: "Start workflow", exact: true })
    .click();
  const card = page
    .getByRole("article", { name: "Brief to images run" })
    .first();
  await expect(
    card.getByRole("textbox", { name: "Review image prompt" }),
  ).toBeVisible();
  await page.reload();
  await expect(
    card.getByRole("textbox", { name: "Review image prompt" }),
  ).toBeVisible();
  await card
    .getByRole("textbox", { name: "Review image prompt" })
    .fill("Synthetic blue circle");
  await card
    .getByRole("button", { name: "Approve prompt and generate" })
    .click();
  await expect(card.getByRole("status")).toContainText("Ready for review", {
    timeout: 15000,
  });
  await expect(
    card.getByRole("img", { name: "Workflow generated image" }),
  ).toHaveCount(2);
  let downloads = 0;
  page.on("download", () => downloads++);
  await card.getByRole("button", { name: "Save outputs" }).click();
  await page.getByRole("button", { name: "Close workflow save" }).click();
  expect(downloads).toBe(0);
  await page.reload();
  await expect(card.getByRole("status")).toContainText("Ready for review");
});

test("Recording workflow retains source and sends only explicit overrides", async ({
  page,
  request,
}) => {
  const upload = await request.post("/api/attachments", {
    multipart: {
      file: {
        name: "Synthetic-workflow.wav",
        mimeType: "audio/wav",
        buffer: Buffer.from("fake"),
      },
    },
  });
  expect(upload.status()).toBe(201);
  await page.goto("/workflows");
  await page
    .getByRole("button", { name: "Recording to meeting pack", exact: true })
    .click();
  await page.getByRole("combobox", { name: "Saved recording" }).click();
  await page
    .getByRole("option")
    .filter({ hasText: "Synthetic-workflow.wav" })
    .first()
    .click();
  await page
    .getByRole("button", { name: "Configure Draft meeting pack", exact: true })
    .click();
  await page.getByRole("combobox", { name: "Meeting-pack model" }).click();
  await page.getByRole("option").filter({ hasText: "fake-chat" }).click();
  await page.getByText("Optional model overrides", { exact: true }).click();
  await page
    .getByRole("spinbutton", { name: "Workflow output token limit" })
    .fill("900");
  await page
    .getByRole("spinbutton", { name: "Workflow temperature" })
    .fill("0.4");
  await page
    .getByRole("button", { name: "Start workflow", exact: true })
    .click();
  const card = page
    .getByRole("article", { name: "Recording to meeting pack run" })
    .first();
  await expect(card.getByRole("status")).toContainText("Ready for review", {
    timeout: 15000,
  });
  await card.getByRole("button", { name: "View original transcript" }).click();
  await expect(
    page.getByRole("dialog", { name: "Original transcript" }),
  ).toContainText("Fake transcript");
  await page.keyboard.press("Escape");
  const captures = await request.get("http://127.0.0.1:18080/tests/state");
  expect(captures.ok()).toBeTruthy();
  {
    const rows = (await captures.json()).captures;
    const body = rows.findLast(
      (r: { options?: { num_predict?: number } }) =>
        r.options?.num_predict === 900,
    );
    expect(body.options.temperature).toBe(0.4);
    expect(body.tools).toBeUndefined();
  }
  expect((await request.get(fakeAppURL + "/api/health")).status()).toBe(200);
});

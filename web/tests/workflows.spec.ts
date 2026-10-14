import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { fakeAppURL } from "../test-runtime";
import {
  configureStudioBlock,
  chooseStudioModel,
  openStudioRun,
} from "./studio-helpers";
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
  await page.goto("/workflows/new?template=brief_images");
  await configureStudioBlock(page, "Draft image prompt");
  await chooseStudioModel(page);
  await configureStudioBlock(page, "Create images");
  await page.getByRole("button", { name: "2", exact: true }).click();
  await page.getByRole("button", { name: "Advanced", exact: true }).click();
  await page
    .getByRole("spinbutton", { name: "Seed 1", exact: true })
    .fill("901");
  await page
    .getByRole("spinbutton", { name: "Seed 2", exact: true })
    .fill("902");
  await openStudioRun(page);
  await page
    .getByRole("textbox", { name: "Image brief", exact: true })
    .fill("Synthetic browser workflow: one blue circle on a white background");
  await page.getByRole("button", { name: "Run workflow", exact: true }).click();
  const card = page
    .getByRole("article", { name: "Brief to images run" })
    .first();
  await expect(
    card.getByRole("textbox", { name: "Review result" }),
  ).toBeVisible();
  await page.reload();
  await expect(
    card.getByRole("textbox", { name: "Review result" }),
  ).toBeVisible();
  await card
    .getByRole("textbox", { name: "Review result" })
    .fill("Synthetic blue circle");
  await card.getByRole("button", { name: "Approve", exact: true }).click();
  await expect(card.getByRole("status")).toContainText("Ready for review", {
    timeout: 15000,
  });
  await expect(
    card.getByRole("img", { name: /Workflow generated image/ }),
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
  await page.goto("/workflows/new?template=meeting_pack");
  await configureStudioBlock(page, "Draft meeting pack");
  await chooseStudioModel(page);
  await page.getByText("Optional overrides", { exact: true }).click();
  await page
    .getByRole("spinbutton", { name: "Output limit", exact: true })
    .fill("900");
  await page
    .getByRole("spinbutton", { name: "Temperature", exact: true })
    .fill("0.4");
  await openStudioRun(page);
  await page
    .getByRole("combobox", { name: "Saved recording", exact: true })
    .click();
  await page
    .getByRole("option")
    .filter({ hasText: "Synthetic-workflow.wav" })
    .first()
    .click();
  await page.getByRole("button", { name: "Run workflow", exact: true }).click();
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

import { settle } from "./helpers";
import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir } from "node:fs/promises";
const evidence = "../artifacts/phase-t";
async function upload(page: Page, directive = "fake") {
  await page.locator('input[type="file"]').setInputFiles({
    name: "Synthetic recording.wav",
    mimeType: "audio/wav",
    buffer: Buffer.from(directive),
  });
}
async function ready(page: Page) {
  await expect(
    page.getByTestId("audio-chip").getByRole("button", {
      name: "Open transcript for Synthetic recording.wav",
    }),
  ).toBeVisible({ timeout: 12000 });
}
test.beforeEach(async ({ page, request }) => {
  const pending = await (await request.get("/api/attachments/pending")).json();
  for (const item of pending)
    await request.delete(`/api/attachments/${item.id}`);
  await request.patch("/api/settings", {
    data: {
      "transcription.block_web": true,
      "transcription.keep_audio": true,
      default_model_id: "fake-chat",
    },
  });
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: "Choose model" }),
  ).toContainText("fake-chat");
});
test("T-1/T-2/T-5 upload, transcript views, downloads, local chat and follow-up", async ({
  page,
  request,
}) => {
  const state = await (
    await request.get("http://127.0.0.1:18080/tests/state")
  ).json();
  await upload(page);
  await ready(page);
  await expect(page.getByTestId("audio-chip")).toContainText("1:15");
  await expect(page.getByTestId("audio-chip")).toContainText("words");
  await page
    .getByRole("button", {
      name: "Open transcript for Synthetic recording.wav",
    })
    .click();
  await expect(
    page
      .getByText("Fake transcript. This recording is not real.", {
        exact: false,
      })
      .last(),
  ).toBeVisible();
  await page.getByRole("button", { name: "Timestamps", exact: true }).click();
  await expect(page.getByText(/\[0:00\]/)).toBeVisible();
  await page.getByRole("button", { name: "Close transcript" }).click();
  await page.getByRole("button", { name: "Summarize", exact: true }).click();
  await expect(page.locator(".composer textarea")).toHaveValue(
    "Summarize this recording.",
  );
  await expect(
    page.getByRole("button", {
      name: "Search is off in chats with a recording",
    }),
  ).toHaveAttribute("aria-disabled", "true");
  await page.getByRole("button", { name: "Send message" }).click();
  await expect(page).toHaveURL(/\/c\//);
  await expect(
    page.getByText(
      "Web search is off in chats with a recording, so nothing from it leaves this Mac.",
    ),
  ).toBeVisible();
  await expect(page.getByRole("button", { name: "Search anyway" })).toHaveCount(
    0,
  );
  await expect(
    page.getByRole("button", { name: "Stop generating" }),
  ).toHaveCount(0);
  await page.locator(".composer textarea").fill("What was decided?");
  await page.getByRole("button", { name: "Send message" }).click();
  await expect(
    page.getByRole("article", { name: "assistant message" }),
  ).toHaveCount(2);
  await expect(
    page.getByRole("button", { name: "Stop generating" }),
  ).toHaveCount(0);
  const captures = (
    await (await request.get("http://127.0.0.1:18080/tests/state")).json()
  ).captures.slice(state.captures.length);
  expect(
    captures.filter((capture: { messages?: { content: string }[] }) =>
      capture.messages?.some((message) =>
        message.content.includes("<transcript"),
      ),
    ).length,
  ).toBeGreaterThanOrEqual(2);
  const detail = await (
    await request.get(`/api/chats/${page.url().split("/").at(-1)}`)
  ).json();
  const id = detail.messages.find(
    (message: { attachments?: unknown[] }) => message.attachments?.length,
  ).attachments[0].id;
  for (const format of ["txt", "srt", "json"])
    expect(
      (
        await request.get(
          `/api/attachments/${id}/transcript/download?format=${format}`,
        )
      ).ok(),
    ).toBeTruthy();
});
test("T-3/T-4 reload while transcribing, cancel, retry and remove", async ({
  page,
}) => {
  await upload(page, "#fake:slow 5");
  await expect(page.getByTestId("audio-chip")).toContainText("Transcribing");
  await page.locator(".composer textarea").fill("Still editable");
  await expect(
    page.getByRole("button", { name: "Send message" }),
  ).toBeDisabled();
  await page.reload();
  await expect(page.getByTestId("audio-chip")).toContainText("Transcribing");
  await ready(page);
  await page
    .getByRole("button", {
      name: "Recording actions for Synthetic recording.wav",
    })
    .click();
  await page
    .getByRole("menuitem", { name: "Transcribe again", exact: true })
    .click();
  await expect(page.getByTestId("audio-chip")).toContainText("Transcribing");
  await page.getByRole("button", { name: "Cancel transcription" }).click();
  await expect(page.getByTestId("audio-chip")).toContainText("Cancelled");
  await page.getByRole("button", { name: "Retry", exact: true }).click();
  await ready(page);
  await page
    .getByRole("button", {
      name: "Recording actions for Synthetic recording.wav",
    })
    .click();
  await page.getByRole("menuitem", { name: "Remove", exact: true }).click();
  await expect(page.getByTestId("audio-chip")).toHaveCount(0);
  await upload(page, "#fake:fail Synthetic decoder failure");
  await expect(page.getByTestId("audio-chip")).toContainText(
    "Synthetic decoder failure",
  );
  await page.getByRole("button", { name: "Retry", exact: true }).click();
  await expect(page.getByTestId("audio-chip")).toContainText(
    "Synthetic decoder failure",
  );
});
test("T-6 too-large transcript warns; switching model changes budget", async ({
  page,
}) => {
  await upload(page, "#fake:words 9000");
  await ready(page);
  await expect(page.getByTestId("audio-chip")).toContainText("≈13,500 tokens");
  await expect(page.getByTestId("audio-chip")).toContainText("more than");
  await page
    .getByRole("button", { name: "Choose model", exact: true })
    .first()
    .click();
  await page.getByRole("option", { name: /^fake-vision/ }).click();
  await expect(
    page.getByRole("button", { name: "Choose model", exact: true }).first(),
  ).toContainText("fake-vision");
  await expect(page.getByTestId("audio-chip")).not.toContainText("more than");
});
test("T-9 unavailable engine menu and settings", async ({ page }) => {
  await page.route("**/api/bootstrap", async (route) => {
    const response = await route.fetch();
    const json = await response.json();
    json.features.transcription = false;
    await route.fulfill({ json });
  });
  await page.reload();
  await page.getByRole("button", { name: "Add attachment" }).click();
  await expect(
    page.getByRole("menuitem", {
      name: "Recordings need the transcription engine",
    }),
  ).toHaveAttribute("data-disabled", "");
  await page.keyboard.press("Escape");
  await page.route("**/api/transcription/status", (route) =>
    route.fulfill({ json: { configured: false, ready: false, checks: [] } }),
  );
  await page.keyboard.press("Control+,");
  await page
    .getByRole("button", { name: "Transcription", exact: true })
    .click();
  await expect(page.getByText(/Not set up/)).toBeVisible();
  await expect(
    page.getByText("WORKBENCH_TRANSCRIBE_HOME", { exact: true }),
  ).toBeVisible();
});
for (const width of [390, 1440])
  for (const theme of ["light", "dark"])
    test(`T-10 design and transcript ${width} ${theme}`, async ({ page }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.goto("/design");
      await page
        .getByRole("button", {
          name: theme === "light" ? "Light" : "Dark",
          exact: true,
        })
        .first()
        .click();
      const preview = page.getByRole("region", {
        name: "Transcription preview",
      });
      await preview.scrollIntoViewIfNeeded();
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBeTruthy();
      await mkdir(evidence, { recursive: true });
      await settle(page);
      await preview.screenshot({
        path: `${evidence}/states-${width}-${theme}-fake.png`,
      });
      await preview
        .getByRole("button", {
          name: "Recording actions for Synthetic recording.wav",
        })
        .first()
        .click();
      const menu = page.getByRole("menu");
      await expect(menu.getByRole("separator")).toHaveCount(3);
      await expect(
        menu.getByRole("menuitem", { name: "Remove", exact: true }),
      ).toHaveAttribute("data-variant", "destructive");
      await expect(menu).toBeInViewport({ ratio: 0.99 });
      await settle(page);
      await page.screenshot({
        animations: "disabled",
        path: `${evidence}/recording-menu-${width}-${theme}-fake.png`,
      });
      await settle(page);
      const menuAxe = await new AxeBuilder({ page }).analyze();
      expect(
        menuAxe.violations.filter((violation) =>
          ["serious", "critical"].includes(violation.impact ?? ""),
        ),
      ).toEqual([]);
      await page.keyboard.press("Escape");
      await expect(
        preview
          .getByRole("button", {
            name: "Recording actions for Synthetic recording.wav",
          })
          .first(),
      ).toBeFocused();
      await preview
        .getByRole("button", { name: "Preview transcript panel" })
        .click();
      await expect(
        page.getByRole("button", { name: "Close transcript" }),
      ).toBeVisible();
      await expect(
        page.getByRole("button", { name: "Copy", exact: true }),
      ).toBeInViewport({ ratio: 0.9 });
      await settle(page);
      await page.screenshot({
        animations: "disabled",
        path: `${evidence}/transcript-text-${width}-${theme}-fake.png`,
      });
      await settle(page);
      const axe = await new AxeBuilder({ page }).analyze();
      expect(
        axe.violations.filter((violation) =>
          ["serious", "critical"].includes(violation.impact ?? ""),
        ),
      ).toEqual([]);
      await page
        .getByRole("button", { name: "Timestamps", exact: true })
        .click();
      await settle(page);
      await page.screenshot({
        path: `${evidence}/transcript-timestamps-${width}-${theme}-fake.png`,
      });
    });

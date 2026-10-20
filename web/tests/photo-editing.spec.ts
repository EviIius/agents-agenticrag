import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { openTools, settle } from "./helpers";
import { photoStates } from "../src/lib/photo-edit-states";

const directory = "../artifacts/photo-editing/pe1-b-20261020/browser";
const file = {
  name: "Synthetic-photo.png",
  mimeType: "image/png",
  buffer: Buffer.from(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a/f8AAAAASUVORK5CYII=",
    "base64",
  ),
};
async function choose(page: Page) {
  await openTools(page);
  const chooser = page.waitForEvent("filechooser");
  await page.getByRole("menuitem", { name: "Edit photo", exact: true }).click();
  await (await chooser).setFiles(file);
  await expect(
    page.getByRole("textbox", { name: "Photo edit instruction" }),
  ).toBeVisible();
  await expect(page.locator('[data-slot="photo-reference"]')).toContainText(
    "Ready",
  );
}
async function ready(page: Page) {
  await page.goto("/");
  await choose(page);
}

test("a rejected new-chat generation cannot capture a later photo's owner", async ({
  page,
}) => {
  await page.goto("/?image=1");
  await page
    .getByRole("textbox", { name: "Image prompt" })
    .fill("Synthetic failed generation");
  await page.route("**/api/chats/*/images", (route) =>
    route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({
        error: { code: "unavailable", message: "Synthetic rejection" },
      }),
    }),
  );
  await page.getByRole("button", { name: "Create image", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText("Synthetic rejection");
  await page.unroute("**/api/chats/*/images");
  await page
    .getByRole("button", { name: "Leave image mode", exact: true })
    .click();
  const upload = page.waitForResponse((r) =>
    r.url().endsWith("/image-references"),
  );
  await choose(page);
  const reference = await (await upload).json();
  await page
    .getByRole("textbox", { name: "Photo edit instruction" })
    .fill("Synthetic owned photo edit");
  const acceptance = page.waitForResponse(
    (r) => r.url().endsWith("/images") && r.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Edit photo", exact: true }).click();
  const response = await acceptance;
  expect(response.status()).toBe(202);
  expect(response.url()).toContain(`/chats/${reference.chat_id}/images`);
  await expect(page).toHaveURL(`/c/${reference.chat_id}`);
});

test("photo upload, lost acceptance replay, reference comparison and clear preserve outputs", async ({
  page,
}) => {
  await page.goto("/");
  await page.locator(".composer textarea").fill("Synthetic ordinary draft");
  await choose(page);
  await expect(page.getByRole("button", { name: "Image count" })).toHaveCount(
    0,
  );
  const instruction = page.getByRole("textbox", {
    name: "Photo edit instruction",
  });
  await instruction.fill("Change the synthetic background to cobalt.");
  const bodies: Record<string, unknown>[] = [];
  await page.route("**/api/chats/*/images", async (route) => {
    bodies.push(route.request().postDataJSON());
    if (bodies.length === 1) {
      await route.fetch();
      await route.abort("failed");
    } else await route.continue();
  });
  await page.getByRole("button", { name: "Edit photo", exact: true }).click();
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(instruction).toHaveValue(
    "Change the synthetic background to cobalt.",
  );
  await page.getByRole("button", { name: "Edit photo", exact: true }).click();
  await expect(page).toHaveURL(/\/c\//);
  expect(bodies).toHaveLength(2);
  expect(bodies[1]).toEqual(bodies[0]);
  expect(bodies[0].count).toBe(1);
  expect(bodies[0].reference_id).toMatch(/^[a-f0-9]{32}$/);
  expect(bodies[0].seeds).toHaveLength(1);
  await expect(
    page.getByText("FLUX.2 klein 4B · Photo edit", { exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Open image 1", exact: true }).click();
  const viewer = page.getByRole("dialog", { name: "Image viewer" });
  await viewer
    .getByRole("button", { name: "Show reference", exact: true })
    .click();
  await expect(
    viewer.getByRole("img", { name: "Normalized photo reference" }),
  ).toHaveAttribute("src", /\/reference$/);
  await expect(
    viewer.getByRole("button", { name: "Save image", exact: true }),
  ).toHaveCount(0);
  await viewer
    .getByRole("button", { name: "Show edited image", exact: true })
    .click();
  await expect(
    viewer.getByRole("button", { name: "Save image", exact: true }),
  ).toBeVisible();
  await viewer.getByRole("button", { name: "Close image viewer" }).click();
  await page.getByRole("button", { name: "Leave photo edit mode" }).click();
  await expect(page.locator(".composer textarea")).toHaveValue(
    "Synthetic ordinary draft",
  );
  const chat = page.url();
  await page.goto("/images");
  await page
    .getByRole("button", { name: "Clear inactive photo inputs", exact: true })
    .click();
  const clear = page.getByRole("dialog", {
    name: "Clear inactive photo inputs?",
  });
  await expect(clear).toContainText("Completed outputs stay");
  await clear.getByRole("button", { name: "Cancel", exact: true }).click();
  await page
    .getByRole("button", { name: "Clear inactive photo inputs", exact: true })
    .click();
  await clear
    .getByRole("button", { name: "Remove files", exact: true })
    .click();
  await page.goto(chat);
  await expect(
    page.getByRole("button", { name: "Try again", exact: true }),
  ).toBeDisabled();
  await expect(
    page.getByRole("button", { name: "Open image 1", exact: true }),
  ).toBeVisible();
});

test("new typing survives an in-flight photo send and the new chat adoption", async ({
  page,
}) => {
  await ready(page);
  const instruction = page.getByRole("textbox", {
    name: "Photo edit instruction",
  });
  await instruction.fill("Earlier synthetic edit");
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route("**/api/chats/*/images", async (route) => {
    await gate;
    await route.continue();
  });
  const response = page.waitForResponse(
    (r) => r.url().endsWith("/images") && r.request().method() === "POST",
  );
  await page.getByRole("button", { name: "Edit photo", exact: true }).click();
  await instruction.fill("Newer synthetic edit draft");
  let releasePhoto!: () => void;
  const photoGate = new Promise<void>((resolve) => {
    releasePhoto = resolve;
  });
  await page.route("**/api/chats/*/image-references", async (route) => {
    await photoGate;
    await route.continue();
  });
  const replacement = page.waitForEvent("filechooser");
  await page
    .getByRole("button", { name: "Replace photo", exact: true })
    .click();
  await (await replacement).setFiles(file);
  await expect(page.locator('[data-slot="photo-reference"]')).toContainText(
    "Preparing photo",
  );
  release();
  expect((await response).request().postDataJSON().prompt).toBe(
    "Earlier synthetic edit",
  );
  await expect(page).toHaveURL(/\/c\//);
  await expect(instruction).toHaveValue("Newer synthetic edit draft");
  releasePhoto();
  await expect(page.locator('[data-slot="photo-reference"]')).toContainText(
    "Ready",
  );
});

test("cancelled uploads cannot return into another chat; completed drafts restore to their owner", async ({
  page,
  request,
}) => {
  const connection = (await (await request.get("/api/connections")).json())[0];
  const first = await (
    await request.post("/api/chats", {
      data: { connection_id: connection.id, model_id: "fake-chat" },
    })
  ).json();
  // Only chats with history appear in the sidebar. Seed a real fake-runtime
  // message before using its navigation link; an empty chat has no such link.
  const seeded = await request.post(`/api/chats/${first.id}/messages`, {
    data: {
      content: "Synthetic history for photo draft navigation",
      web: false,
      attachment_ids: [],
    },
  });
  expect(seeded.status()).toBe(202);
  await page.goto(`/c/${first.id}`);
  await choose(page);
  await page
    .getByRole("textbox", { name: "Photo edit instruction" })
    .fill("Retained photo instruction");
  const newLink = page.getByRole("link", { name: "New chat", exact: true });
  if (!(await newLink.isVisible()))
    await page
      .getByRole("button", { name: "Open sidebar", exact: true })
      .click();
  await newLink.click();
  await expect(page).toHaveURL("/");
  if ((page.viewportSize()?.width ?? 1440) < 1024)
    await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(
    page.getByRole("textbox", { name: "Photo edit instruction" }),
  ).toHaveCount(0);
  // Sidebar links are real SPA navigation, so no draft store reload occurs.
  const firstLink = page.locator(`a[href="/c/${first.id}"]:visible`).first();
  if (!(await firstLink.isVisible()))
    await page
      .getByRole("button", { name: "Open sidebar", exact: true })
      .click();
  await firstLink.click();
  await expect(
    page.getByRole("textbox", { name: "Photo edit instruction" }),
  ).toHaveValue("Retained photo instruction");
  let release!: () => void;
  const gate = new Promise<void>((resolve) => {
    release = resolve;
  });
  await page.route("**/api/chats/*/image-references", async (route) => {
    await gate;
    await route.continue().catch(() => {});
  });
  const chooser = page.waitForEvent("filechooser");
  await page
    .getByRole("button", { name: "Replace photo", exact: true })
    .click();
  await (await chooser).setFiles(file);
  await page
    .getByRole("button", { name: "Cancel photo upload", exact: true })
    .click();
  release();
  await expect(page.locator('[data-slot="photo-reference"]')).toContainText(
    "Choose one",
  );
  await expect(
    page.getByRole("button", { name: "Edit photo", exact: true }),
  ).toBeDisabled();
  await expect(
    page.getByRole("textbox", { name: "Photo edit instruction" }),
  ).toHaveValue("Retained photo instruction");
});

test("editing a generated output explicitly binds pixels; Refine keeps generation semantics", async ({
  page,
}) => {
  await ready(page);
  await page
    .getByRole("textbox", { name: "Photo edit instruction" })
    .fill("Synthetic first edit");
  await page.getByRole("button", { name: "Edit photo", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Open image 1", exact: true }),
  ).toBeVisible();
  const copy = page.waitForResponse((r) =>
    r.url().endsWith("/image-references/from-job"),
  );
  await page
    .getByRole("button", { name: "More image actions", exact: true })
    .click();
  await page.getByRole("menuitem", { name: "Edit image", exact: true }).click();
  const result = await copy;
  expect(result.request().postDataJSON().source_job_id).toMatch(
    /^[a-f0-9]{32}$/,
  );
  await expect(page.locator('[data-slot="photo-reference"]')).toContainText(
    "Ready",
  );
  await page.getByRole("button", { name: "Refine image", exact: true }).click();
  await expect(
    page.getByRole("textbox", { name: "Image prompt", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Image count", exact: true }),
  ).toBeVisible();
  await expect(page.locator('[data-slot="photo-reference"]')).toHaveCount(0);
});

for (const width of [390, 1440])
  for (const theme of ["light", "dark"]) {
    test(`photo edit states, comparison, tokens and reduced motion ${width} ${theme}`, async ({
      page,
      browserName,
    }) => {
      await page.setViewportSize({ width, height: 1000 });
      await page.goto("/design?photo-edit");
      await page.getByRole("button", { name: theme, exact: true }).click();
      await mkdir(directory, { recursive: true });
      const reports = [];
      for (const state of photoStates) {
        await page
          .getByRole("button", { name: `Preview ${state}`, exact: true })
          .click();
        await settle(page);
        const violations = (
          await new AxeBuilder({ page }).analyze()
        ).violations.filter((v) =>
          ["serious", "critical"].includes(v.impact ?? ""),
        );
        reports.push({ state, violations });
        expect(violations).toEqual([]);
        expect(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
        ).toBe(true);
        await page.screenshot({
          path: `${directory}/${state}-${width}-${theme}-${browserName}-fake.png`,
          fullPage: true,
        });
      }
      await page
        .getByRole("button", { name: "Preview comparison", exact: true })
        .click();
      await page
        .getByRole("button", { name: "Open image 1", exact: true })
        .click();
      const viewer = page.getByRole("dialog", { name: "Image viewer" });
      await viewer
        .getByRole("button", { name: "Show reference", exact: true })
        .click();
      await expect(
        viewer.getByRole("img", { name: "Normalized photo reference" }),
      ).toBeVisible();
      await viewer.getByRole("button", { name: "Close image viewer" }).click();
      await page
        .getByRole("button", { name: "Reduce motion", exact: true })
        .click();
      expect(
        await page.evaluate(
          () => document.documentElement.dataset.reduceMotion,
        ),
      ).toBe("always");
      await writeFile(
        `${directory}/axe-${width}-${theme}-${browserName}.json`,
        JSON.stringify(reports, null, 2),
      );
    });
  }

import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { fakeAppURL } from "../test-runtime";
import { settle } from "./helpers";
const dir = "../artifacts/chat-images/ci-b/browser";
test.use({ video: { mode: "on" } });
const prompt = (page: Page) =>
  page.getByRole("textbox", { name: "Image prompt", exact: true });
const turn = (page: Page) => page.locator('[data-slot="image-turn"]').last();
async function enter(page: Page) {
  await page.goto("/?image=1");
  await expect(prompt(page)).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Leave image mode" }),
  ).toBeEnabled();
}

test("saved image turn handles a lost response, automatic seeds, drafts, saving and reload", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "no-preference" });
  await page.addInitScript(() => {
    const state = window as Window & { imageReveals?: number };
    state.imageReveals = 0;
    document.addEventListener("animationstart", (event) => {
      if (event.animationName === "image-reveal") state.imageReveals!++;
    });
  });
  await page.goto("/");
  const text = page.locator(".composer textarea");
  await text.fill("Synthetic unsent text draft");
  await expect(
    page.getByRole("button", { name: "Create image", exact: true }),
  ).toBeEnabled();
  await page.getByRole("button", { name: "Create image", exact: true }).click();
  await prompt(page).fill("Synthetic saved cobalt circle #slow");
  const bodies: Record<string, unknown>[] = [];
  await page.route("**/api/chats/*/images", async (route) => {
    bodies.push(route.request().postDataJSON());
    if (bodies.length === 1) {
      await route.fetch();
      await route.abort("failed");
    } else await route.continue();
  });
  await page.getByRole("button", { name: "Create image", exact: true }).click();
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(prompt(page)).toHaveValue("Synthetic saved cobalt circle #slow");
  await page.getByRole("button", { name: "Create image", exact: true }).click();
  await expect(page).toHaveURL(/\/c\//);
  expect(bodies).toHaveLength(2);
  expect(bodies[1]).toEqual(bodies[0]);
  expect(bodies[0].seeds).toHaveLength(1);
  await expect(page.locator('[data-slot="image-turn"]')).toHaveCount(1);
  await expect(turn(page).locator("img")).toBeVisible();
  await expect
    .poll(() =>
      page.evaluate(
        () => (window as Window & { imageReveals?: number }).imageReveals,
      ),
    )
    .toBe(1);
  await turn(page)
    .getByRole("button", { name: "Save image", exact: true })
    .click();
  const save = page.getByRole("dialog", { name: "Save image", exact: true });
  await save
    .getByRole("button", { name: "Details (.json)", exact: true })
    .click();
  await expect(
    save.getByRole("button", { name: "Details (.json)", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
  let downloads = 0;
  page.on("download", () => downloads++);
  await save
    .getByRole("button", { name: "Close image save", exact: true })
    .click();
  expect(downloads).toBe(0);
  await page.getByRole("button", { name: "Leave image mode" }).click();
  await expect(text).toHaveValue("Synthetic unsent text draft");
  const id = await turn(page)
    .locator("[data-job-id]")
    .getAttribute("data-job-id");
  await page.reload();
  await expect(turn(page).locator("img")).toBeVisible();
  expect(
    await page.evaluate(
      () => (window as Window & { imageReveals?: number }).imageReveals,
    ),
  ).toBe(0);
  await expect(turn(page).locator("img")).not.toHaveAttribute(
    "data-reveal",
    "true",
  );
  await page.goto("/images");
  const gallery = page.locator(`[data-job-id="${id}"]`);
  await gallery.getByRole("link", { name: /^From / }).click();
  await expect(page).toHaveURL(/#m-/);
  await expect(turn(page)).toBeVisible();
});

test("real paused worker progress, next frames, SSE reconnection and sibling retry", async ({
  page,
  request,
}) => {
  await request.post(`${fakeAppURL}/tests/images/pause`);
  await enter(page);
  await page.getByRole("button", { name: "Image count" }).click();
  await page.getByRole("menuitem", { name: "3 images", exact: true }).click();
  await prompt(page).fill("Synthetic paused lanterns #pause-step");
  await page.getByRole("button", { name: "Create image", exact: true }).click();
  await expect(turn(page).getByRole("progressbar").first()).toHaveAttribute(
    "aria-valuenow",
    "2",
  );
  await expect(turn(page).getByText("Next", { exact: true })).toHaveCount(2);
  const jobIds = await turn(page)
    .locator("[data-job-id]")
    .evaluateAll((nodes) => nodes.map((n) => (n as HTMLElement).dataset.jobId));
  await page.waitForTimeout(900);
  await expect(turn(page).getByRole("progressbar").first()).toHaveAttribute(
    "aria-valuenow",
    "2",
  );
  await page.reload();
  await expect(turn(page).getByRole("progressbar").first()).toHaveAttribute(
    "aria-valuenow",
    "2",
  );
  const gets: string[] = [];
  page.on("request", (r) => {
    if (r.method() === "GET" && /\/images\/(jobs|events)/.test(r.url()))
      gets.push(r.url());
  });
  await request.post(`${fakeAppURL}/tests/images/release`);
  await expect(turn(page).locator("img")).toHaveCount(3);
  await expect(turn(page).locator("div[role=status]")).toContainText(
    "3 images",
  );
  await expect(
    turn(page).getByRole("button", { name: "Try again", exact: true }),
  ).toBeVisible();
  expect(gets.filter((url) => /\/images\/jobs[^/]*$/.test(url))).toHaveLength(
    0,
  );
  const old = await request
    .get(`/api/images/jobs/${jobIds[0]}`)
    .then((r) => r.json());
  await turn(page)
    .getByRole("button", { name: "Try again", exact: true })
    .click();
  await expect(
    turn(page).getByRole("button", { name: "Previous branch" }),
  ).toBeEnabled();
  await expect(turn(page).locator("img")).toHaveCount(3);
  const retryIds = await turn(page)
    .locator("[data-job-id]")
    .evaluateAll((nodes) => nodes.map((n) => (n as HTMLElement).dataset.jobId));
  expect(retryIds).not.toEqual(jobIds);
  const retried = await request
    .get(`/api/images/jobs/${retryIds[0]}`)
    .then((r) => r.json());
  expect(retried.seed).not.toBe(old.seed);
  await turn(page).getByRole("button", { name: "Previous branch" }).click();
  await expect(turn(page).locator("[data-job-id]").first()).toHaveAttribute(
    "data-job-id",
    jobIds[0]!,
  );
});

test("image command, independent drafts, cancellation, removed outputs and failed load retry", async ({
  page,
  request,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: "Create image", exact: true }),
  ).toBeEnabled();
  await page
    .locator(".composer textarea")
    .fill("/image Synthetic cancel circle #slow");
  await expect(prompt(page)).toHaveValue("Synthetic cancel circle #slow");
  await page.getByRole("button", { name: "Leave image mode" }).click();
  await page.locator(".composer textarea").fill("Synthetic separate text");
  await page.getByRole("button", { name: "Create image", exact: true }).click();
  await expect(prompt(page)).toHaveValue("Synthetic cancel circle #slow");
  await page.getByRole("button", { name: "Create image", exact: true }).click();
  await turn(page).getByRole("button", { name: "Cancel", exact: true }).click();
  await expect(turn(page).locator("div[role=status]")).toHaveText("Cancelled");
  await turn(page)
    .getByRole("button", { name: "Try again", exact: true })
    .click();
  await expect(turn(page).locator("img")).toBeVisible();
  await page.route("**/api/images/jobs/*/output/png", (route) =>
    route.fulfill({ status: 404, body: "Synthetic load failure" }),
  );
  await page.reload();
  await expect(turn(page)).toContainText("Couldn't load the image");
  await page.unroute("**/api/images/jobs/*/output/png");
  await turn(page).getByRole("button", { name: "Retry", exact: true }).click();
  await expect(turn(page).locator("img.is-loaded")).toBeVisible();
  await turn(page).getByRole("button", { name: "More image actions" }).click();
  await page
    .getByRole("menuitem", { name: "Remove image", exact: true })
    .click();
  await page
    .getByRole("dialog")
    .getByRole("button", { name: "Remove", exact: true })
    .click();
  await expect(turn(page)).toContainText("Image removed");
  const chatId = new URL(page.url()).pathname.split("/").at(-1);
  await request.delete(`/api/chats/${chatId}`);
  await page.goto("/images");
  await expect(page.getByText("From a deleted chat").first()).toBeVisible();
});

test("image and text user siblings remain reachable without offering text edit for images", async ({
  page,
  request,
}) => {
  await enter(page);
  await prompt(page).fill("Synthetic image root branch");
  await page.getByRole("button", { name: "Create image", exact: true }).click();
  await expect(turn(page).locator("img")).toBeVisible();
  const cid = new URL(page.url()).pathname.split("/").at(-1);
  const detail = await request.get(`/api/chats/${cid}`).then((r) => r.json());
  const imageUser = detail.messages.find(
    (row: { role: string }) => row.role === "user",
  );
  const accepted = await request.post(`/api/chats/${cid}/messages`, {
    data: { content: "Synthetic text sibling branch", parent_id: null },
  });
  expect(accepted.status()).toBe(202);
  const textUser = (await accepted.json()).user_message;
  await page.goto(`/c/${cid}`);
  const textRow = page.locator(`[data-message-id="${textUser.id}"]`);
  await expect(
    textRow.getByRole("button", { name: "Previous branch" }),
  ).toBeEnabled();
  await textRow.getByRole("button", { name: "Previous branch" }).click();
  const imageRow = page.locator(`[data-message-id="${imageUser.id}"]`);
  await expect(imageRow).toContainText("Synthetic image root branch");
  await expect(
    imageRow.getByRole("button", { name: "Edit message" }),
  ).toHaveCount(0);
  await expect(
    imageRow.getByRole("button", { name: "Next branch" }),
  ).toBeEnabled();
  await page.reload();
  await imageRow.getByRole("button", { name: "Next branch" }).click();
  await expect(textRow).toContainText("Synthetic text sibling branch");
  await expect(turn(page)).toHaveCount(0);
});

test("fixed seeds are optional, validated per image and sent exactly", async ({
  page,
}) => {
  await enter(page);
  await prompt(page).fill("Synthetic fixed-seed circles");
  await page.getByRole("button", { name: "Image count" }).click();
  await page.getByRole("menuitem", { name: "2 images", exact: true }).click();
  await page.getByRole("button", { name: "Image options" }).click();
  await page
    .getByRole("textbox", { name: "Seed 1", exact: true })
    .fill("4294967296");
  await expect(page.getByRole("alert")).toContainText("4,294,967,295");
  await expect(
    page.getByRole("button", {
      name: "Create image",
      exact: true,
      includeHidden: true,
    }),
  ).toBeDisabled();
  await page.getByRole("textbox", { name: "Seed 1", exact: true }).fill("1337");
  await page.getByRole("textbox", { name: "Seed 2", exact: true }).fill("42");
  await page.keyboard.press("Escape");
  await expect(prompt(page)).toBeFocused();
  const accepted = page.waitForRequest(
    (r) =>
      r.method() === "POST" &&
      /\/api\/chats\/[^/]+\/images$/.test(new URL(r.url()).pathname),
  );
  await page.getByRole("button", { name: "Create image", exact: true }).click();
  expect((await accepted).postDataJSON().seeds).toEqual([1337, 42]);
  await expect(turn(page).locator("img")).toHaveCount(2);
});

for (const width of [390, 1440])
  for (const theme of ["light", "dark"])
    test(`chat image frame states, counts and axe ${width} ${theme}`, async ({
      page,
      browserName,
    }) => {
      await page.setViewportSize({ width, height: 900 });
      await page.goto("/design?chat-images");
      await page.getByRole("button", { name: theme, exact: true }).click();
      await mkdir(dir, { recursive: true });
      const results = [];
      for (const state of [
        "queued",
        "preparing",
        "step 0",
        "step 1",
        "step 2",
        "step 3",
        "step 4",
        "decoding",
        "complete",
        "cancelling",
        "cancelled",
        "failed",
        "interrupted",
        "removed",
      ]) {
        await page
          .getByRole("button", { name: `Preview ${state}`, exact: true })
          .click();
        for (const count of [1, 2, 3]) {
          await page
            .getByRole("button", {
              name: `Preview ${count} image${count > 1 ? "s" : ""}`,
              exact: true,
            })
            .click();
          await expect(page.locator(".image-frame")).toHaveCount(count);
        }
        await settle(page);
        expect(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
        ).toBe(true);
        const scan = await new AxeBuilder({ page }).analyze();
        const violations = scan.violations.filter((v) =>
          ["critical", "serious"].includes(v.impact ?? ""),
        );
        expect(violations).toEqual([]);
        results.push({ state, count: 3, violations });
        await page.screenshot({
          path: `${dir}/${state.replace(" ", "-")}-${width}-${theme}-${browserName}-fake.png`,
          fullPage: true,
        });
      }
      await writeFile(
        `${dir}/axe-${width}-${theme}-${browserName}.json`,
        JSON.stringify(results, null, 2),
      );
    });

for (const mode of ["always", "system"] as const)
  test(`image develop and progress motion respects ${mode}`, async ({
    page,
  }) => {
    await page.emulateMedia({
      reducedMotion: mode === "system" ? "reduce" : "no-preference",
    });
    await page.goto("/design?chat-images");
    if (mode === "always")
      await page.getByRole("button", { name: "Reduce motion" }).click();
    await expect(page.locator(".image-progress")).toHaveCount(2);
    expect(
      await page
        .locator(".image-develop i,.image-progress i")
        .evaluateAll((nodes) =>
          nodes.every((node) => {
            const css = getComputedStyle(node);
            return (
              css.animationName === "none" &&
              css.transitionDuration
                .split(",")
                .every((n) => parseFloat(n) === 0)
            );
          }),
        ),
    ).toBe(true);
    await page
      .getByRole("button", { name: "Preview step 4", exact: true })
      .click();
    await expect(page.getByRole("progressbar").first()).toHaveAttribute(
      "aria-valuenow",
      "4",
    );
  });

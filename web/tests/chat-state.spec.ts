import { test, expect, type APIRequestContext } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { settle } from "./helpers";
const directory = "../artifacts/design-critique-b-20261025/browser";
const png = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a/f8AAAAASUVORK5CYII=",
  "base64",
);
let savedSettings: Record<string, unknown>;
let savedModel: {
  connection_id: string;
  model_id: string;
  params_defaults: Record<string, unknown>;
  context_length: number;
};
test.beforeEach(async ({ request }) => {
  const settings = await (await request.get("/api/settings")).json();
  savedSettings = Object.fromEntries(
    ["default_connection_id", "default_model_id", "auto_title"].map((key) => [
      key,
      settings[key],
    ]),
  );
  savedModel = (await (await request.get("/api/models")).json()).find(
    (model: { model_id: string }) => model.model_id === "fake-reasoning",
  );
});
test.afterEach(async ({ request }) => {
  expect(
    (await request.patch("/api/settings", { data: savedSettings })).ok(),
  ).toBeTruthy();
  expect(
    (
      await request.put("/api/models/prefs", {
        data: {
          connection_id: savedModel.connection_id,
          model_id: savedModel.model_id,
          params: savedModel.params_defaults,
          context_length: savedModel.context_length,
        },
      })
    ).ok(),
  ).toBeTruthy();
});
async function setup(request: APIRequestContext, modelID = "fake-chat") {
  const connection = (await (await request.get("/api/connections")).json())[0];
  await request.patch("/api/settings", {
    data: {
      default_connection_id: connection.id,
      default_model_id: modelID,
      auto_title: false,
    },
  });
  const response = await request.post("/api/chats", {
    data: { connection_id: connection.id, model_id: modelID },
  });
  expect(response.ok()).toBeTruthy();
  return { connection, chat: await response.json() };
}
async function image(
  request: APIRequestContext,
  chat: string,
  reference?: string,
) {
  const response = await request.post(`/api/chats/${chat}/images`, {
    data: {
      request_key: crypto.randomUUID(),
      prompt: "Synthetic Part B image",
      count: 1,
      seeds: [42],
      ...(reference ? { reference_id: reference } : {}),
    },
  });
  expect(response.status()).toBe(202);
  const rows = await response.json();
  await expect
    .poll(
      async () =>
        (
          await (
            await request.get(`/api/images/jobs/${rows.assistant.images[0].id}`)
          ).json()
        ).state,
    )
    .toBe("complete");
  return rows;
}

test("image user turns retain selected source/mode after reload and clearing never invents a thumbnail", async ({
  page,
  request,
}) => {
  const { chat } = await setup(request);
  const upload = await request.post(`/api/chats/${chat.id}/image-references`, {
    multipart: {
      file: { name: "Synthetic-photo.png", mimeType: "image/png", buffer: png },
    },
  });
  expect(upload.status()).toBe(201);
  const ref = await upload.json();
  await image(request, chat.id, ref.id);
  await image(request, chat.id);
  await page.goto(`/c/${chat.id}`);
  const sources = page.locator('[data-slot="image-prompt-source"]');
  await expect(sources).toHaveCount(2);
  await expect(sources.first()).toContainText("Edit photo · Photo reference");
  await expect(sources.first().getByRole("img")).toHaveAttribute(
    "src",
    /\/reference$/,
  );
  await expect(sources.last()).toHaveText("Create image");
  await sources
    .first()
    .getByRole("button", { name: "View source photo" })
    .click();
  await expect(
    page.getByRole("dialog", { name: "Image viewer" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Close image viewer" }).click();
  await page.reload();
  await expect(sources.first()).toContainText("Edit photo");
  expect(
    (
      await request.post("/api/images/references/clear", {
        data: { confirm: true },
      })
    ).ok(),
  ).toBeTruthy();
  await page.reload();
  await expect(sources.first()).toContainText("Source photo unavailable");
  await expect(sources.first().getByRole("img")).toHaveCount(0);
  await expect(
    page.locator('[data-slot="image-turn"] img.is-loaded'),
  ).toHaveCount(2);
});

test("image-mode followup shows its source, pins that branch and never silently generates on reference failure", async ({
  page,
  request,
}) => {
  const { chat } = await setup(request);
  const first = await image(request, chat.id);
  const second = await image(request, chat.id);
  await request.patch(`/api/chats/${chat.id}`, {
    data: { current_leaf_id: first.assistant.id },
  });
  await page.goto(`/c/${chat.id}?image=1`);
  const followup = page.locator('[data-slot="image-followup"]');
  await expect(followup).toContainText("Edit last image");
  await expect(followup.getByRole("img")).toHaveAttribute(
    "src",
    `/api/images/jobs/${first.assistant.images[0].id}/output/png`,
  );
  await expect(page.getByRole("button", { name: "Image count" })).toHaveCount(
    0,
  );
  const bodies: Record<string, unknown>[] = [];
  await page.route(
    `**/api/chats/${chat.id}/image-references/from-job`,
    async (route) => {
      const response = await route.fetch();
      // Simulate another client changing the branch while the clone is in flight.
      await request.patch(`/api/chats/${chat.id}`, {
        data: { current_leaf_id: second.assistant.id },
      });
      await route.fulfill({ response });
    },
  );
  await page.route(`**/api/chats/${chat.id}/images`, async (route) => {
    bodies.push(route.request().postDataJSON());
    await route.continue();
  });
  await page
    .getByRole("textbox", { name: "Image prompt" })
    .fill("Add a synthetic hat");
  await page.getByRole("button", { name: "Edit image", exact: true }).click();
  await expect.poll(() => bodies.length).toBe(1);
  expect(bodies[0]).toMatchObject({ parent_id: first.assistant.id, count: 1 });
  expect(bodies[0].reference_id).toEqual(expect.any(String));
  await expect(page.locator('[data-slot="image-turn"]').last()).toContainText(
    "Photo edit",
  );
  await expect(
    page.locator('[data-slot="image-turn"]').last().locator("img.is-loaded"),
  ).toBeVisible();
  await page.unroute(`**/api/chats/${chat.id}/image-references/from-job`);
  await followup.getByRole("button", { name: "Create image instead" }).click();
  await expect(followup).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Image count" })).toBeVisible();
  await page
    .getByRole("textbox", { name: "Image prompt" })
    .fill("Create a separate synthetic scene");
  await page.getByRole("button", { name: "Create image", exact: true }).click();
  await expect.poll(() => bodies.length).toBe(2);
  expect(bodies[1]).not.toHaveProperty("reference_id");
  await expect(
    page
      .getByText("Create a separate synthetic scene", { exact: true })
      .first(),
  ).toBeVisible();
  await expect(page.getByRole("textbox", { name: "Image prompt" })).toHaveValue(
    "",
  );
  await expect(followup).toBeVisible();
  await expect(
    page.locator('[data-slot="image-turn"]').last().locator("img.is-loaded"),
  ).toBeVisible();
  await page.route(
    `**/api/chats/${chat.id}/image-references/from-job`,
    (route) =>
      route.fulfill({
        status: 404,
        contentType: "application/json",
        body: JSON.stringify({
          error: { code: "not_found", message: "Synthetic source unavailable" },
        }),
      }),
  );
  await page
    .getByRole("textbox", { name: "Image prompt" })
    .fill("An edit that cannot find its source");
  await page.getByRole("button", { name: "Edit image", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText(
    "Synthetic source unavailable",
  );
  expect(bodies).toHaveLength(2);
  await expect(page.getByRole("textbox", { name: "Image prompt" })).toHaveValue(
    "An edit that cannot find its source",
  );
});

test("stopped and empty replies are visible, Continue names its parent and preserves the unsent draft", async ({
  page,
  request,
}) => {
  const { connection, chat } = await setup(request);
  const model = {
    connection_id: connection.id,
    model_id: "fake-chat",
    display_name: "fake-chat",
  };
  const rows = [
    {
      id: "stopped-synthetic",
      chat_id: chat.id,
      role: "assistant",
      status: "stopped",
      content: "I'd begin",
      model,
      created_at: chat.created_at,
    },
    {
      id: "empty-synthetic",
      chat_id: chat.id,
      parent_id: "stopped-synthetic",
      role: "assistant",
      status: "complete",
      content: "",
      reasoning: "Synthetic reasoning without a final answer",
      model,
      created_at: chat.created_at,
    },
  ];
  await page.route(`**/api/chats/${chat.id}`, (route) =>
    route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        chat: { ...chat, current_leaf_id: "empty-synthetic" },
        messages: rows,
      }),
    }),
  );
  let body: Record<string, unknown> | undefined;
  await page.route(`**/api/chats/${chat.id}/messages`, (route) => {
    body = route.request().postDataJSON();
    return route.fulfill({
      status: 503,
      contentType: "application/json",
      body: JSON.stringify({
        error: {
          code: "unavailable",
          message: "Synthetic rejected continuation",
        },
      }),
    });
  });
  await page.goto(`/c/${chat.id}`);
  const stopped = page.locator('[data-message-id="stopped-synthetic"]');
  const empty = page.locator('[data-message-id="empty-synthetic"]');
  await expect(stopped.locator('[data-slot="reply-outcome"]')).toContainText(
    "Stopped",
  );
  await expect(
    stopped.getByRole("button", { name: "Retry", exact: true }),
  ).toHaveCount(1);
  await expect(
    stopped.getByRole("button", { name: "Regenerate answer", exact: true }),
  ).toHaveCount(0);
  await expect(empty.locator('[data-slot="reply-outcome"]')).toContainText(
    "No answer",
  );
  await page.locator(".composer textarea").fill("An unsent draft");
  await stopped.getByRole("button", { name: "Continue", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText(
    "Something went wrong. Try again.",
  );
  expect(body).toMatchObject({
    content: "Continue your previous answer.",
    parent_id: "stopped-synthetic",
    attachment_ids: [],
  });
  await expect(page.locator(".composer textarea")).toHaveValue(
    "An unsent draft",
  );
  await expect(stopped).toContainText("I'd begin");
});

test("one Save retains reasoning, saves only changed scopes, and retries a partial failure without repeating the chat save", async ({
  page,
  request,
}) => {
  const { connection, chat } = await setup(request, "fake-reasoning");
  await request.put("/api/models/prefs", {
    data: {
      connection_id: connection.id,
      model_id: "fake-reasoning",
      params: { reasoning: "on" },
      context_length: 16384,
    },
  });
  await request.patch(`/api/chats/${chat.id}`, {
    data: { params: { reasoning: "off" } },
  });
  let patches = 0,
    failed = false;
  page.on("request", (req) => {
    if (req.method() === "PATCH" && req.url().endsWith(`/api/chats/${chat.id}`))
      patches++;
  });
  await page.route("**/api/models/prefs", (route) => {
    if (!failed && route.request().postDataJSON().params) {
      failed = true;
      return route.fulfill({
        status: 503,
        contentType: "application/json",
        body: JSON.stringify({
          error: { code: "unavailable", message: "Synthetic defaults failure" },
        }),
      });
    }
    return route.continue();
  });
  await page.goto(`/c/${chat.id}`);
  await page
    .getByRole("button", { name: "Chat controls", exact: true })
    .click();
  const controls = page.getByRole("region", { name: "Chat controls" });
  await expect(
    controls.getByRole("combobox", { name: "Reasoning" }),
  ).toHaveCount(0);
  await controls
    .getByRole("switch", {
      name: "Use model default for Temperature",
      exact: true,
    })
    .click();
  await controls
    .getByRole("spinbutton", { name: "Temperature", exact: true })
    .fill("0.4");
  await controls
    .locator("summary")
    .filter({ hasText: "Every chat with this model" })
    .click();
  await controls
    .getByRole("switch", {
      name: "Use model default for Model Top K",
      exact: true,
    })
    .click();
  await controls
    .getByRole("spinbutton", { name: "Model Top K", exact: true })
    .fill("23");
  await controls
    .getByRole("spinbutton", { name: "Context length" })
    .fill("8192");
  const save = controls.getByRole("button", {
    name: "Save settings",
    exact: true,
  });
  await save.click();
  await expect(
    page.getByText("Synthetic defaults failure", { exact: true }),
  ).toBeVisible();
  await expect(save).toBeEnabled();
  expect(patches).toBe(1);
  expect(
    (await (await request.get(`/api/chats/${chat.id}`)).json()).chat.params,
  ).toEqual({ temperature: 0.4, reasoning: "off" });
  await save.click();
  await expect(save).toContainText("Saved");
  expect(patches).toBe(1);
  const models = await (await request.get("/api/models")).json();
  const updated = models.find(
    (m: { model_id: string }) => m.model_id === "fake-reasoning",
  );
  expect(updated.params_defaults).toEqual({ top_k: 23, reasoning: "on" });
  expect(updated.context_length).toBe(8192);
  await page.keyboard.press("Escape");
  await expect(controls).not.toBeVisible();
  await request.put("/api/models/prefs", {
    data: {
      connection_id: connection.id,
      model_id: "fake-reasoning",
      params: {},
      context_length: 16384,
    },
  });
});

test("feature starters invoke the existing picker and Library paths, reuse recent prompts, and keep Max's wire value", async ({
  page,
}) => {
  let modelRequests = 0;
  page.on("request", (req) => {
    if (req.method() === "POST" && /\/api\/(chats|images)/.test(req.url()))
      modelRequests++;
  });
  await page.goto("/design?chat-state&state=starters");
  const composer = page.locator(".composer");
  const photo = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: "Edit a photo", exact: true }).click();
  await (
    await photo
  ).setFiles({
    name: "Synthetic-photo.png",
    mimeType: "image/png",
    buffer: png,
  });
  await expect(
    page.getByText("Photo chosen · preview only", { exact: true }),
  ).toBeVisible();
  const recording = page.waitForEvent("filechooser");
  await page
    .getByRole("button", { name: "Transcribe a recording", exact: true })
    .click();
  await (
    await recording
  ).setFiles({
    name: "Synthetic-audio.wav",
    mimeType: "audio/wav",
    buffer: Buffer.from("Synthetic preview; no engine"),
  });
  await expect(
    page.getByText("Files chosen · preview only", { exact: true }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Ask my files", exact: true }).click();
  await expect(
    page.getByText("Library chosen · preview only", { exact: true }),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Plan a synthetic workshop.", exact: true })
    .click();
  await expect(composer.locator("textarea")).toHaveValue(
    "Plan a synthetic workshop.",
  );
  await composer.getByRole("button", { name: "Tools", exact: true }).click();
  await page.getByRole("menuitemradio", { name: "Max", exact: true }).click();
  await expect(
    page.getByText("Thinking value: xhigh · preview only", { exact: true }),
  ).toBeVisible();
  await page.keyboard.press("Escape");
  expect(modelRequests).toBe(0);
});

for (const width of [390, 1440])
  for (const theme of ["light", "dark"])
    test(`Part B design states ${width} ${theme}`, async ({
      page,
      browserName,
    }) => {
      const pageErrors: string[] = [];
      page.on("pageerror", (error) => pageErrors.push(error.message));
      await page.setViewportSize({ width, height: 900 });
      await page.route("**/api/images/jobs/*/output/png", (route) =>
        route.fulfill({
          contentType: "image/png",
          path: fileURLToPath(
            new URL("../public/icons/apple-touch-icon.png", import.meta.url),
          ),
        }),
      );
      await page.goto("/design?chat-state");
      await page.getByRole("button", { name: theme, exact: true }).click();
      await page.getByRole("button", { name: "Aero", exact: true }).click();
      await mkdir(directory, { recursive: true });
      const audits = [];
      for (const state of [
        "thread",
        "cleared",
        "controls",
        "image-controls",
        "followup",
        "variants",
        "starters",
      ]) {
        await page.getByRole("button", { name: state, exact: true }).click();
        if (state === "variants")
          await page
            .locator(".design-page")
            .getByRole("button", { name: "Choose model", exact: true })
            .click();
        await expect(page.locator(".design-page h1")).toBeVisible();
        expect(pageErrors).toEqual([]);
        if (state === "variants") {
          const choices = page.locator('[data-slot="model-choice"]');
          await expect(choices).toHaveCount(2);
          await page
            .getByRole("button", { name: "Variants for synthetic-family" })
            .click();
          await expect(choices).toHaveCount(3);
          await expect(
            choices.filter({ hasText: "Synthetic 16K variant" }),
          ).toContainText("Sees");
          const search = page.getByRole("combobox", { name: "Search models" });
          await search.fill("synthetic-other");
          await expect(choices).toHaveCount(1);
          await expect(choices).toContainText("Synthetic 16K variant");
          await search.press("Enter");
          await expect(page.getByRole("grid", { name: "Models" })).toHaveCount(
            0,
          );
          await page
            .locator(".design-page")
            .getByRole("button", { name: "Choose model", exact: true })
            .click();
          await page.getByRole("combobox", { name: "Search models" }).fill("");
          await expect(choices).toHaveCount(3);
        }
        if (state === "followup") {
          const card = page.locator('[data-slot="image-followup"]');
          const preview = card.getByRole("img", { name: "Image to edit" });
          await preview.evaluate((image) =>
            (image as HTMLImageElement).decode(),
          );
          const box = await preview.boundingBox();
          expect(box!.width).toBeGreaterThanOrEqual(56);
          expect(box!.height).toBeGreaterThanOrEqual(56);
          if (width < 640) {
            const button = await card
              .getByRole("button", { name: "Create image instead" })
              .boundingBox();
            expect(button!.y).toBeGreaterThanOrEqual(box!.y + box!.height);
          }
        }
        await settle(page);
        const audit = await new AxeBuilder({ page }).analyze();
        const violations = audit.violations.filter((v) =>
          ["serious", "critical"].includes(v.impact ?? ""),
        );
        expect(violations, state).toEqual([]);
        expect(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
        ).toBeTruthy();
        await page.screenshot({
          path: `${directory}/${state}-${width}-${theme}-${browserName}-fake.png`,
          fullPage: true,
        });
        audits.push({ state, seriousCritical: violations.length });
        if (state === "variants") {
          await page
            .getByRole("button", { name: "Variants for synthetic-family" })
            .focus();
          await page.keyboard.press("Escape");
          await expect(page.getByRole("grid", { name: "Models" })).toHaveCount(
            0,
          );
        }
      }
      await writeFile(
        `${directory}/axe-${width}-${theme}-${browserName}-fake.json`,
        JSON.stringify(audits, null, 2),
      );
    });

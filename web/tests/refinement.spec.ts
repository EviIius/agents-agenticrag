import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { settle } from "./helpers";

test.beforeEach(async ({ request }) => {
  const [connection] = await (await request.get("/api/connections")).json();
  expect(connection.base_url).toBe("http://127.0.0.1:18080");
  await request.patch("/api/settings", {
    data: {
      default_connection_id: connection.id,
      default_model_id: "fake-chat",
      auto_title: false,
      "web.default_on": false,
      "appearance.theme": "light",
      "appearance.reduce_motion": "system",
    },
  });
  await request.put("/api/models/prefs", {
    data: {
      connection_id: connection.id,
      model_id: "fake-chat",
      params: {},
      context_length: 16384,
    },
  });
});

test("display name, PWA metadata and original internal storage key", async ({
  page,
  request,
}) => {
  await page.goto("/");
  await expect(page).toHaveTitle("Atelier");
  const manifest = await (await request.get("/manifest.webmanifest")).json();
  expect(manifest.name).toBe("Atelier");
  expect(manifest.short_name).toBe("Atelier");
  expect(manifest.id).toBe("/");
  expect(
    await page
      .locator('meta[name="apple-mobile-web-app-title"]')
      .getAttribute("content"),
  ).toBe("Atelier");
  expect(
    await page.evaluate(() => localStorage.getItem("workbench-theme")),
  ).toBeTruthy();
  await page.getByRole("button", { name: "Choose model", exact: true }).click();
  await page
    .getByRole("button", { name: "Manage models…", exact: true })
    .click();
  const settings = page.getByRole("dialog", { name: "Settings", exact: true });
  await expect(
    settings.getByRole("heading", { name: "Models", exact: true }),
  ).toBeVisible();
  await settle(page);
  await page.keyboard.press("Escape");
  await expect(settings).not.toBeVisible();
});

test("defaults hide unused inputs and explicit values remain editable", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .getByRole("button", { name: "Chat controls", exact: true })
    .click();
  const panel = page.getByRole("region", {
    name: "Chat controls",
    exact: true,
  });
  for (const label of [
    "Temperature",
    "Top P",
    "Top K",
    "Max output tokens",
    "Seed",
  ]) {
    await expect(
      panel.getByRole("switch", {
        name: `Use model default for ${label}`,
        exact: true,
      }),
    ).toBeChecked();
    await expect(
      panel.getByRole("spinbutton", { name: label, exact: true }),
    ).toHaveCount(0);
  }
  await panel
    .getByRole("switch", {
      name: "Use model default for Temperature",
      exact: true,
    })
    .click();
  await panel
    .getByRole("spinbutton", { name: "Temperature", exact: true })
    .fill("0.55");
  await expect(
    panel.getByRole("spinbutton", { name: "Temperature", exact: true }),
  ).toHaveValue("0.55");
});

test("actual theme drives both phone theme-color tags and segmented selection", async ({
  page,
}) => {
  await page.goto("/");
  await page.keyboard.press("Control+,");
  await page.getByRole("button", { name: "Appearance", exact: true }).click();
  await page.getByRole("button", { name: "Dark", exact: true }).click();
  await settle(page);
  const tags = await page.evaluate(() => ({
    bg: getComputedStyle(document.documentElement)
      .getPropertyValue("--bg")
      .trim(),
    colors: [
      ...document.querySelectorAll<HTMLMetaElement>('meta[name="theme-color"]'),
    ].map((m) => m.content),
  }));
  expect(tags.colors).toEqual([tags.bg, tags.bg]);
  await expect(
    page.getByRole("button", { name: "Dark", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
  await page.getByRole("button", { name: "Web search", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Web search", exact: true }),
  ).toBeVisible();
});

test("offline guidance keeps technical failure behind Details", async ({
  page,
}) => {
  await page.route("**/api/bootstrap", (route) => route.abort());
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Can't reach Atelier" }),
  ).toBeVisible();
  await expect(
    page.getByText("Your Mac may be asleep or off the tailnet."),
  ).toBeVisible();
  const details = page.locator("details");
  await expect(details).not.toHaveAttribute("open", "");
  await details.locator("summary").click();
  await expect(details).toHaveAttribute("open", "");
});

test("message alignment, single code/table surfaces and inline rename", async ({
  page,
  request,
}, testInfo) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  const [connection] = await (await request.get("/api/connections")).json();
  const chat = await (
    await request.post("/api/chats", {
      data: { connection_id: connection.id, model_id: "fake-chat" },
    })
  ).json();
  expect(
    (
      await request.post(`http://127.0.0.1:8787/tests/long-chat/${chat.id}`)
    ).ok(),
  ).toBe(true);
  const seeded = { chat_id: chat.id };
  await page.goto("/c/" + seeded.chat_id);
  await expect(page.locator(".topbar-title")).toBeVisible();
  await page.locator(".topbar-title").dblclick();
  const title = page.getByRole("textbox", { name: "Rename chat inline" });
  await title.fill("Synthetic renamed checkpoint");
  await title.press("Enter");
  await expect(page.locator(".topbar-title")).toHaveText(
    "Synthetic renamed checkpoint",
  );
  expect(
    (await (await request.get("/api/chats/" + seeded.chat_id)).json()).chat
      .title,
  ).toBe("Synthetic renamed checkpoint");
  await page.goto("/design");
  // Production bubbles use the same presentation before and after confirmation.
  const bubbles = page.locator(".user-bubble");
  await expect(bubbles.first()).toBeVisible();
  const css = await bubbles.first().evaluate((el) => ({
    border: getComputedStyle(el).borderTopWidth,
    radius: getComputedStyle(el).borderRadius,
    size: getComputedStyle(el).fontSize,
    line: getComputedStyle(el).lineHeight,
  }));
  expect(css.border).toBe("0px");
  expect(css.size).toBe("15px");
  expect(css.line).toBe("23px");
  const code = page.locator('[data-streamdown="code-block"]').first();
  await code.scrollIntoViewIfNeeded();
  await settle(page);
  const body = code.locator('[data-streamdown="code-block-body"]');
  expect(await body.evaluate((el) => getComputedStyle(el).borderTopWidth)).toBe(
    "0px",
  );
  const results = await new AxeBuilder({ page })
    .include('[aria-label="Visual refinement previews"]')
    .analyze();
  expect(
    results.violations.filter((v) =>
      ["serious", "critical"].includes(v.impact ?? ""),
    ),
  ).toEqual([]);
  await page.screenshot({
    path: `../artifacts/phase-4/4d/refinement-1440-${testInfo.project.name}-fake.png`,
    animations: "disabled",
  });
});

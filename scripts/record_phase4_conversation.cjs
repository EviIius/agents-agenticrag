const { chromium } = require(process.cwd() + "/web/node_modules/playwright");
(async () => {
  const browser = await chromium.launch();
  for (const [name, width, reduced] of [
    ["send-reasoning-phone", 390, false],
    ["search-phone", 390, false],
    ["copy-phone", 390, false],
    ["theme-desktop", 1440, false],
    ["send-reduced-phone", 390, true],
  ]) {
    const context = await browser.newContext({
      viewport: { width, height: width === 390 ? 844 : 900 },
      reducedMotion: reduced ? "reduce" : "no-preference",
      recordVideo: {
        dir: "/tmp/workbench-phase4-video-fake",
        size: { width, height: width === 390 ? 844 : 900 },
      },
    });
    const page = await context.newPage();
    const api = context.request;
    const bootstrap = await (
      await api.get("http://127.0.0.1:8787/api/bootstrap")
    ).json();
    if (
      !bootstrap.connections.length ||
      !bootstrap.connections.every(
        (c) =>
          c.base_url === "http://127.0.0.1:18080" && c.name === "Fake runtime",
      )
    )
      throw new Error(
        "Isolated fake runtime required; production capture refused.",
      );
    const connection = bootstrap.connections[0];
    await api.patch("http://127.0.0.1:8787/api/settings", {
      data: {
        default_connection_id: connection.id,
        default_model_id: "fake-reasoning",
        auto_title: false,
        "web.default_on": false,
        "appearance.theme": "dark",
        "appearance.reduce_motion": "system",
        user_name: "",
      },
    });
    const chat = await (
      await api.post("http://127.0.0.1:8787/api/chats", {
        data: {
          connection_id: connection.id,
          model_id: "fake-reasoning",
          web_enabled: false,
        },
      })
    ).json();
    await page.addInitScript(() =>
      Object.defineProperty(navigator, "clipboard", {
        configurable: true,
        value: { writeText: async () => {} },
      }),
    );
    await page.goto("http://127.0.0.1:5175/c/" + chat.id);
    await page
      .getByRole("button", { name: "Choose model", exact: true })
      .waitFor();
    await page.waitForTimeout(400);
    if (name.startsWith("theme")) {
      await page.keyboard.press("Control+,");
      const dialog = page.getByRole("dialog", {
        name: "Settings",
        exact: true,
      });
      await dialog.waitFor();
      await dialog
        .getByRole("button", { name: "Appearance", exact: true })
        .click();
      await dialog.getByRole("button", { name: "Light", exact: true }).click();
      await page.waitForTimeout(700);
      await dialog.getByRole("button", { name: "Dark", exact: true }).click();
      await page.waitForTimeout(700);
      await page
        .getByRole("button", { name: "Close settings", exact: true })
        .click();
    } else {
      if (name.startsWith("search"))
        await page
          .getByRole("button", { name: "Search off", exact: true })
          .click();
      const prompt = name.startsWith("search")
        ? "Who lost the 2021 NBA Finals? Show a table."
        : name.startsWith("copy")
          ? "Synthetic copy preview"
          : "#think #long:80 #slow:20";
      await page.locator(".composer textarea").fill(prompt);
      await page
        .getByRole("button", { name: "Send message", exact: true })
        .click();
      await page
        .getByRole("button", { name: "Stop generating", exact: true })
        .waitFor({ state: "hidden" });
      if (name.startsWith("copy")) {
        await page
          .getByRole("article", { name: "assistant message" })
          .getByRole("button", { name: "Copy message", exact: true })
          .click();
        await page.waitForTimeout(1700);
      }
      if (name.startsWith("send") && !reduced) {
        await page.getByRole("button", { name: /Thought for/ }).click();
        await page.waitForTimeout(500);
        await page.getByRole("button", { name: /Thought for/ }).click();
      }
    }
    await page.waitForTimeout(500);
    const video = page.video();
    await context.close();
    await video.saveAs("artifacts/phase-4/motion/" + name + "-fake.webm");
    await video.delete();
  }
  await browser.close();
})().catch((error) => {
  console.error(error);
  process.exit(1);
});

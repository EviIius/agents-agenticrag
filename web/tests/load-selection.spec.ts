import { test, expect } from "@playwright/test";

for (const width of [390, 1440]) {
  for (const existing of [false, true]) {
    test(`Load selects a 32K model and uses its context ${width} ${existing ? "existing" : "new"}`, async ({
      page,
      request,
      browserName,
    }) => {
      await page.setViewportSize({ width, height: 844 });
      const connection = (
        await (await request.get("/api/connections")).json()
      )[0];
      await request.patch("/api/settings", {
        data: {
          default_connection_id: connection.id,
          default_model_id: "fake-chat",
          auto_title: false,
        },
      });
      await request.post("/api/models/unload", {
        data: { connection_id: connection.id, model_id: "fake-vision" },
      });
      await request.put("/api/models/prefs", {
        data: {
          connection_id: connection.id,
          model_id: "fake-vision",
          context_length: 32768,
          params: {},
        },
      });
      const chat = existing
        ? await (
            await request.post("/api/chats", {
              data: { connection_id: connection.id, model_id: "fake-chat" },
            })
          ).json()
        : null;
      await page.goto(chat ? "/c/" + chat.id : "/");
      if (width >= 640)
        await page
          .getByRole("button", { name: "Chat settings", exact: true })
          .click();
      await page
        .getByRole("button", { name: "Choose model", exact: true })
        .click();
      await page
        .getByRole("button", { name: "Load fake-vision", exact: true })
        .click();
      await expect(
        page.getByText("fake-vision loaded", { exact: true }),
      ).toBeVisible();
      const selected = page.getByRole("option", { name: /^fake-vision/ });
      await expect(selected).toContainText("Loaded");
      await expect(
        selected.getByRole("img", { name: "Selected for chat" }),
      ).toBeVisible();
      await page.screenshot({
        path: `../artifacts/phase-2/load-selected-${width}-${existing ? "existing" : "new"}-${browserName}.png`,
      });
      if (width < 640)
        await page.getByRole("button", { name: "Close", exact: true }).click();
      else await page.keyboard.press("Escape");
      await expect(
        page.getByRole("button", { name: "Choose model", exact: true }),
      ).toContainText("fake-vision");
      await expect(page.locator(".composer textarea")).toHaveAttribute(
        "placeholder",
        "Message fake-vision…",
      );
      if (chat)
        expect(
          (await (await request.get(`/api/chats/${chat.id}`)).json()).chat
            .model_id,
        ).toBe("fake-vision");
      if (width < 640)
        await page
          .getByRole("button", { name: "Chat settings", exact: true })
          .click();
      const controls = page.getByRole("region", {
        name: "Chat settings controls",
      });
      await expect(
        controls.getByText("fake-vision", { exact: true }),
      ).toBeVisible();
      const context = controls.getByRole("spinbutton", {
        name: "Context length",
      });
      await expect(context).toHaveValue("32768");
      await expect(context).toHaveAttribute("max", "32768");
      await expect(
        controls.getByRole("button", { name: "64K", exact: true }),
      ).toHaveCount(0);
      await context.fill("16384");
      await controls.getByRole("button", { name: "32K", exact: true }).click();
      await expect(
        controls.getByRole("button", { name: "32K", exact: true }),
      ).toHaveAttribute("aria-pressed", "true");
      await controls
        .getByRole("button", { name: "Save settings", exact: true })
        .click();
      if (width < 640) {
        const drawer = page.getByRole("dialog", { name: "Chat settings" });
        expect(await drawer.evaluate((element) => element.scrollTop)).toBe(0);
        await expect(
          drawer.getByRole("button", { name: "Close chat settings" }),
        ).toBeInViewport({ ratio: 1 });
      }
      await page.screenshot({
        path: `../artifacts/phase-2/load-context-32k-${width}-${browserName}.png`,
      });
      await page
        .getByRole("button", { name: "Close chat settings", exact: true })
        .click();
      const question = `Context payload ${width} ${existing} ${browserName}`;
      await page.locator(".composer textarea").fill(question);
      await page
        .getByRole("button", { name: "Send message", exact: true })
        .click();
      await expect(
        page.getByText("Fake runtime reply.", { exact: false }),
      ).toBeVisible();
      const state = await (
        await request.get("http://127.0.0.1:18080/tests/state")
      ).json();
      const payload = state.captures.findLast(
        (item: { messages?: { content: string }[] }) =>
          item.messages?.some((message) => message.content === question),
      );
      expect(payload.model).toBe("fake-vision");
      expect(payload.options).toEqual({ num_ctx: 32768 });
      await page.reload();
      await expect(
        page.getByRole("button", { name: "Choose model", exact: true }),
      ).toContainText("fake-vision");
    });
  }

  test(`Settings model Load also selects the active chat ${width}`, async ({
    page,
    request,
  }) => {
    await page.setViewportSize({ width, height: 844 });
    const connection = (
      await (await request.get("/api/connections")).json()
    )[0];
    await request.patch("/api/settings", {
      data: {
        default_connection_id: connection.id,
        default_model_id: "fake-chat",
      },
    });
    await request.post("/api/models/unload", {
      data: { connection_id: connection.id, model_id: "fake-reasoning" },
    });
    await page.goto("/");
    await page.keyboard.press("Control+,");
    const settings = page.getByRole("dialog", {
      name: "Settings",
      exact: true,
    });
    await settings.getByRole("button", { name: "Models", exact: true }).click();
    const card = settings
      .getByRole("textbox", {
        name: "Display name for fake-reasoning",
        exact: true,
      })
      .locator("..");
    await card.getByRole("button", { name: "Load", exact: true }).click();
    await expect(
      card.getByRole("button", { name: "Eject", exact: true }),
    ).toBeVisible();
    await settings
      .getByRole("button", { name: "Close settings", exact: true })
      .click();
    await expect(
      page.getByRole("button", { name: "Choose model", exact: true }),
    ).toContainText("fake-reasoning");
  });
}

test("failed Load stays visibly unloaded and reports the error", async ({
  page,
  request,
}) => {
  const connection = (await (await request.get("/api/connections")).json())[0];
  await request.post("/api/models/unload", {
    data: { connection_id: connection.id, model_id: "fake-vision" },
  });
  await page.route("**/api/models/load", (route) =>
    route.fulfill({
      status: 502,
      json: {
        error: { code: "model_load_failed", message: "Synthetic load failure" },
      },
    }),
  );
  await page.goto("/");
  await page.getByRole("button", { name: "Choose model", exact: true }).click();
  await page
    .getByRole("button", { name: "Load fake-vision", exact: true })
    .click();
  await expect(
    page.getByText("Couldn’t load fake-vision", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("option", { name: /^fake-vision/ }),
  ).toContainText("Not loaded");
  await expect(
    page.getByRole("button", { name: "Load fake-vision", exact: true }),
  ).toBeEnabled();
});

for (const preference of ["system", "always"]) {
  test(`settings transitions respect reduced motion ${preference}`, async ({
    page,
    request,
  }) => {
    await page.emulateMedia({
      reducedMotion: preference === "system" ? "reduce" : "no-preference",
    });
    await request.patch("/api/settings", {
      data: { "appearance.reduce_motion": preference },
    });
    await page.goto("/");
    await page.keyboard.press("Control+,");
    const settings = page.getByRole("dialog", {
      name: "Settings",
      exact: true,
    });
    await settings.getByRole("button", { name: "Data", exact: true }).click();
    await expect
      .poll(() =>
        settings
          .getByRole("region", { name: "Data", exact: true })
          .evaluate((element) => getComputedStyle(element).animationName),
      )
      .toBe("none");
    await request.patch("/api/settings", {
      data: { "appearance.reduce_motion": "system" },
    });
  });
}

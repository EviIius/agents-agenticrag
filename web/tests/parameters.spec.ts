import { test, expect } from "@playwright/test";

for (const width of [390, 1440]) {
  test(`parameter controls reach the runtime and persist ${width}`, async ({
    page,
    request,
    browserName,
  }) => {
    await page.setViewportSize({ width, height: 900 });
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
    await request.put("/api/models/prefs", {
      data: {
        connection_id: connection.id,
        model_id: "fake-chat",
        params: {},
        context_length: 16384,
      },
    });
    await page.goto("/");
    await expect(
      page.getByRole("button", { name: "Choose model" }),
    ).toContainText("fake-chat");
    const open = () =>
      page.getByRole("button", { name: "Chat controls", exact: true }).click();
    const close = () =>
      page.getByRole("button", { name: "Close chat controls" }).click();
    await open();
    for (const [label, value] of [
      ["Temperature", "0.55"],
      ["Top P", "0.85"],
      ["Top K", "37"],
      ["Max output tokens", "96"],
      ["Seed", "42"],
    ]) {
      await page
        .getByRole("switch", { name: `Use model default for ${label}` })
        .click();
      await page
        .getByRole("spinbutton", { name: label, exact: true })
        .fill(value!);
    }
    await page
      .getByRole("switch", { name: "Use default system prompt" })
      .click();
    await page
      .getByRole("textbox", { name: "System prompt", exact: true })
      .fill("Be concise. Parameter integration check.");
    await page.getByRole("spinbutton", { name: "Context length" }).fill("4096");
    await page
      .getByRole("button", { name: "Save settings", exact: true })
      .click();
    await expect
      .poll(async () => {
        const models = await (await request.get("/api/models")).json();
        return models.find(
          (m: { model_id: string }) => m.model_id === "fake-chat",
        ).context_length;
      })
      .toBe(4096);
    await close();
    await open();
    await expect(
      page.getByRole("spinbutton", { name: "Temperature", exact: true }),
    ).toHaveValue("0.55");
    await expect(
      page.getByRole("textbox", { name: "System prompt", exact: true }),
    ).toHaveValue("Be concise. Parameter integration check.");
    await close();
    const question = `Parameter payload ${width} ${browserName}`;
    await page.locator(".composer textarea").fill(question);
    await page.getByRole("button", { name: "Send message" }).click();
    await expect(page).toHaveURL(/\/c\//);
    const id = page.url().split("/c/")[1]!;
    const detail = async () => (await request.get(`/api/chats/${id}`)).json();
    await expect
      .poll(async () => (await detail()).messages.at(-1).status)
      .toBe("complete");
    const captures = async () =>
      (await (await request.get("http://127.0.0.1:18080/tests/state")).json())
        .captures;
    const sent = (await captures()).findLast(
      (r: { messages?: { content: string }[] }) =>
        r.messages?.at(-1)?.content === question,
    );
    expect(sent.options).toEqual({
      temperature: 0.55,
      top_p: 0.85,
      top_k: 37,
      num_predict: 96,
      seed: 42,
      num_ctx: 4096,
    });
    expect(sent.messages[0].content).toContain(
      "Be concise. Parameter integration check.",
    );
    await page.reload();
    await open();
    await expect(
      page.getByRole("spinbutton", { name: "Temperature", exact: true }),
    ).toHaveValue("0.55");
    await page.getByRole("button", { name: "Reset to model defaults" }).click();
    await expect.poll(async () => (await detail()).chat.params).toEqual({});
    await close();
    const followup = `Runtime defaults ${width} ${browserName}`;
    await page.locator(".composer textarea").fill(followup);
    await page.getByRole("button", { name: "Send message" }).click();
    await expect
      .poll(async () => (await detail()).messages.at(-1).status)
      .toBe("complete");
    const reset = (await captures()).findLast(
      (r: { messages?: { content: string }[] }) =>
        r.messages?.at(-1)?.content === followup,
    );
    expect(reset.options).toEqual({ num_ctx: 4096 });
    await request.put("/api/models/prefs", {
      data: {
        connection_id: connection.id,
        model_id: "fake-chat",
        context_length: 16384,
      },
    });
  });
}

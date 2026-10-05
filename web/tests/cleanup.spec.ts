import { test, expect } from "@playwright/test";
for (const width of [390, 1440]) {
  test(`6A clean progress rejected section versions download context discard ${width}`, async ({
    page,
    request,
  }) => {
    await page.setViewportSize({ width, height: 900 });
    const connections = await (await request.get("/api/connections")).json();
    for (const item of await (
      await request.get("/api/attachments/pending")
    ).json())
      await request.delete(`/api/attachments/${item.id}`);
    await request.patch("/api/settings", {
      data: {
        default_connection_id: connections[0].id,
        default_model_id: "fake-chat",
        auto_title: false,
        "transcription.keep_audio": false,
      },
    });
    await request.put("/api/transcription/glossary", { data: { text: "" } });
    await page.goto("/");
    await page.locator('input[type="file"]').setInputFiles({
      name: "Invented cleanup recording.wav",
      mimeType: "audio/wav",
      buffer: Buffer.from("#fake:cleanup"),
    });
    const chip = page.getByTestId("audio-chip");
    await expect(chip).toContainText("Transcript saved · audio removed");
    const pending = await (
      await request.get("/api/attachments/pending")
    ).json();
    const id = pending[0].id;
    const before = await (
      await request.get(`/api/attachments/${id}/transcript`)
    ).json();
    await chip
      .getByRole("button", {
        name: "Open transcript for Invented cleanup recording.wav",
      })
      .click();
    await page
      .getByRole("button", { name: "Clean up with fake-chat", exact: true })
      .click();
    await expect(
      page.getByRole("button", { name: "Cancel clean-up", exact: true }),
    ).toBeVisible();
    await expect(chip).toContainText("Cleaning up…");
    await expect(
      page.getByRole("button", { name: "Cleaned", exact: true }),
    ).toBeVisible({ timeout: 20000 });
    await expect(
      page.getByText(/sections were left as transcribed/),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Cleaned", exact: true }),
    ).toHaveAttribute("aria-pressed", "true");
    await page
      .getByRole("button", { name: "As transcribed", exact: true })
      .click();
    await expect(
      page.getByRole("button", { name: "As transcribed", exact: true }),
    ).toHaveAttribute("aria-pressed", "true");
    await page
      .getByRole("button", { name: "Raw Whisper", exact: true })
      .click();
    await page.getByRole("button", { name: "Timestamps", exact: true }).click();
    await expect(
      page.getByText("Timestamps use the original transcript."),
    ).toBeVisible();
    const value = await (
      await request.get(`/api/attachments/${id}/transcript`)
    ).json();
    expect(value.text).toBe(before.text);
    expect(value.raw_text).toBe(before.raw_text);
    expect(value.segments).toEqual(before.segments);
    expect(value.cleaned_text).toContain("FAKE-REWRITE");
    const txt = await request.get(
      `/api/attachments/${id}/transcript/download?format=txt&variant=best`,
    );
    expect(await txt.text()).toBe(value.cleaned_text);
    await page.getByRole("button", { name: "Close transcript" }).click();
    await page
      .locator(".composer textarea")
      .fill("Summarize the invented recording.");
    await page
      .getByRole("button", { name: "Send message", exact: true })
      .click();
    await expect(page).toHaveURL(/\/c\//);
    await expect(
      page.getByRole("article", { name: "assistant message" }),
    ).toContainText("Fake runtime reply.");
    const runtime = await (
      await request.get("http://127.0.0.1:18080/tests/state")
    ).json();
    const capture = runtime.captures
      .filter((b: { messages?: { content: string }[] }) =>
        b.messages?.some((m) => m.content.includes("<transcript ")),
      )
      .at(-1);
    expect(capture.messages.at(-1).content).toContain(value.cleaned_text);
    await page
      .getByRole("button", {
        name: "Open transcript for Invented cleanup recording.wav",
      })
      .click();
    await page
      .getByRole("button", { name: "Discard clean-up", exact: true })
      .click();
    await expect(
      page.getByRole("button", { name: "Cleaned", exact: true }),
    ).toHaveCount(0);
    await page.getByRole("button", { name: "Close transcript" }).click();
    const chatId = page.url().split("/c/")[1];
    await request.delete(`/api/chats/${chatId}`);
  });
  test(`6A glossary edit validation saved state and next transcription ${width}`, async ({
    page,
    request,
  }) => {
    await page.setViewportSize({ width, height: 900 });
    const old = await (await request.get("/api/transcription/glossary")).json();
    try {
      await page.goto("/");
      if (width < 640)
        await page
          .getByRole("button", { name: "Open sidebar", exact: true })
          .click();
      await page.getByRole("button", { name: "Settings", exact: true }).click();
      await page
        .getByRole("button", { name: "Transcription", exact: true })
        .click();
      const box = page.getByRole("textbox", {
        name: "Terms for transcription",
      });
      await expect(box).toBeVisible();
      await box.fill("Invented Aurora = invented aurora\nInvented Grove");
      await page
        .getByRole("button", { name: "Save glossary", exact: true })
        .click();
      await expect(
        page.getByText("Glossary saved", { exact: true }),
      ).toBeVisible();
      await expect(
        page.getByText("2 saved terms", { exact: true }),
      ).toBeVisible();
      const stored = await (
        await request.get("/api/transcription/glossary")
      ).json();
      expect(stored.terms).toEqual(["Invented Aurora", "Invented Grove"]);
      const uploaded = await request.post("/api/attachments", {
        multipart: {
          file: {
            name: "Invented glossary recording.wav",
            mimeType: "audio/wav",
            buffer: Buffer.from("fake"),
          },
        },
      });
      expect(uploaded.status()).toBe(201);
      const added = await uploaded.json();
      await expect
        .poll(async () =>
          (
            await request.get(`/api/attachments/${added.id}/transcript`)
          ).status(),
        )
        .toBe(200);
      const output = await (
        await request.get(
          `/api/attachments/${added.id}/transcript/download?format=json`,
        )
      ).json();
      expect(output.engine.prompt).toContain("Invented Aurora");
      await request.delete(`/api/attachments/${added.id}`);

      await box.fill("x".repeat(65537));
      await expect(
        page.getByRole("button", { name: "Save glossary", exact: true }),
      ).toBeDisabled();
      await expect(
        page.getByText(
          "Glossary can be up to 64 KB and cannot contain NUL bytes.",
          { exact: true },
        ),
      ).toBeVisible();
      const bad = await request.put("/api/transcription/glossary", {
        data: { text: "bad\u0000term" },
      });
      expect(bad.status()).toBe(422);
      expect(
        (await (await request.get("/api/transcription/glossary")).json()).text,
      ).toBe(stored.text);
    } finally {
      await request.put("/api/transcription/glossary", {
        data: { text: old.text },
      });
    }
  });
}
test("6A cancelling clean-up preserves all original transcript fields", async ({
  page,
  request,
}) => {
  const connections = await (await request.get("/api/connections")).json();
  for (const item of await (
    await request.get("/api/attachments/pending")
  ).json())
    await request.delete(`/api/attachments/${item.id}`);
  await request.patch("/api/settings", {
    data: {
      default_connection_id: connections[0].id,
      default_model_id: "fake-chat",
      auto_title: false,
    },
  });
  await page.goto("/");
  await page.locator('input[type="file"]').setInputFiles({
    name: "Invented cancellation.wav",
    mimeType: "audio/wav",
    buffer: Buffer.from("#fake:cleanup-slow"),
  });
  const chip = page.getByTestId("audio-chip");
  await expect(chip).toContainText("words");
  const id = (await (await request.get("/api/attachments/pending")).json())[0]
    .id;
  const before = await (
    await request.get(`/api/attachments/${id}/transcript`)
  ).json();
  await chip
    .getByRole("button", {
      name: "Open transcript for Invented cancellation.wav",
    })
    .click();
  await page
    .getByRole("button", { name: "Clean up with fake-chat", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Cancel clean-up", exact: true })
    .click();
  await expect(
    page.getByText("Clean-up cancelled. The transcript is unchanged.", {
      exact: true,
    }),
  ).toBeVisible();
  const after = await (
    await request.get(`/api/attachments/${id}/transcript`)
  ).json();
  expect(after.text).toBe(before.text);
  expect(after.raw_text).toBe(before.raw_text);
  expect(after.segments).toEqual(before.segments);
  expect(after.cleaned_text).toBeNull();
  await request.delete(`/api/attachments/${id}`);
});

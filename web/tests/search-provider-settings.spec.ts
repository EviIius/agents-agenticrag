import { test, expect } from "@playwright/test";

for (const width of [390, 1440]) {
  test(`Ollama search key is saved, redacted and removed ${width}`, async ({
    page,
    request,
  }) => {
    await page.setViewportSize({ width, height: 900 });
    await request.patch("/api/settings", {
      data: {
        "web.provider_order": ["ollama", "searxng", "exa", "ddgs"],
        "web.ollama_api_key": null,
      },
    });
    await page.goto("/");
    if (width < 640)
      await page.getByRole("button", { name: "Open sidebar" }).click();
    await page.getByRole("button", { name: "Settings", exact: true }).click();
    await page.getByRole("button", { name: "Web search", exact: true }).click();
    const field = page.getByLabel("Ollama search API key");
    await expect(
      page.getByRole("button", { name: "Save Ollama key" }),
    ).toBeDisabled();
    await field.fill("browser-fixture-not-a-real-key");
    await page.getByRole("button", { name: "Save Ollama key" }).click();
    await expect(field).toHaveValue("");
    await expect(
      page.getByRole("button", { name: "Remove Ollama key" }),
    ).toBeEnabled();
    const settings = await (await request.get("/api/settings")).json();
    expect(settings["web.has_ollama_api_key"]).toBe(true);
    expect(settings).not.toHaveProperty("web.ollama_api_key");
    expect(JSON.stringify(settings)).not.toContain(
      "browser-fixture-not-a-real-key",
    );
    await page.getByRole("button", { name: "Remove Ollama key" }).click();
    await expect(
      page.getByRole("button", { name: "Remove Ollama key" }),
    ).toBeDisabled();
    expect(
      (await (await request.get("/api/settings")).json())[
        "web.has_ollama_api_key"
      ],
    ).toBe(false);
  });
}

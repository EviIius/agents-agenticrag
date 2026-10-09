import { test, expect } from "@playwright/test";
import { readFile, mkdir } from "node:fs/promises";
import { settle } from "./helpers";

for (const width of [390, 1440]) {
  test(`isolated evidence replay preserves values and inert source markup ${width}`, async ({
    page,
    request,
    browserName,
  }) => {
    const fixture = JSON.parse(
      await readFile(
        "../artifacts/reliability/evidence-v10/synthetic-rendering.json",
        "utf8",
      ),
    );
    const connection = (
      await (await request.get("/api/connections")).json()
    )[0];
    await request.patch("/api/settings", {
      data: {
        default_connection_id: connection.id,
        default_model_id: "fake-chat",
        auto_title: false,
        "web.default_on": false,
        "appearance.theme": "dark",
      },
    });
    await page.setViewportSize({ width, height: 844 });
    await page.emulateMedia({ colorScheme: "dark" });
    await page.goto("/");
    await page
      .locator(".composer textarea")
      .fill("Synthetic rendering fixture");
    await page
      .getByRole("button", { name: "Send message", exact: true })
      .click();
    await expect(page).toHaveURL(/\/c\//);
    await expect(
      page.getByText("Fake runtime reply.", { exact: false }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Stop generating" }),
    ).not.toBeVisible();
    const id = page.url().split("/").at(-1);
    await page.route(`**/api/chats/${id}`, async (route) => {
      const response = await route.fetch();
      const detail = await response.json();
      const assistant = detail.messages.find(
        (message: { role: string }) => message.role === "assistant",
      );
      assistant.content = fixture.content;
      detail.sources[assistant.id] = fixture.sources;
      await route.fulfill({ response, json: detail });
    });
    await page.reload();
    const answer = page.getByRole("article", { name: "assistant message" });
    await expect(answer.getByRole("table")).toBeVisible();
    await expect(answer).toContainText("-24.5");
    await expect(answer).toContainText("CEDAR-42");
    await expect(answer).toContainText(
      "[900] A|B <img src=x> [click](https://example.invalid)",
    );
    await expect(
      answer.locator('img[src="x"], a[href="https://example.invalid"]'),
    ).toHaveCount(0);
    await expect(
      answer.getByRole("button", { name: "View source: Invented evidence 1" }),
    ).toHaveCount(2);
    await expect(
      answer.getByRole("button", { name: "View source: Invented evidence 2" }),
    ).toHaveCount(1);
    await expect(answer.getByRole("row")).toHaveCount(4);
    await expect(answer.getByRole("row").last().getByRole("cell")).toHaveCount(
      2,
    );
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBeTruthy();
    await settle(page);
    await mkdir("../artifacts/reliability/evidence-v10/browser", {
      recursive: true,
    });
    await page.screenshot({
      path: `../artifacts/reliability/evidence-v10/browser/synthetic-literal-${width}-${browserName}.png`,
    });
  });
}

import { expect, test } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import { fakeAppURL } from "../test-runtime";
import { settle } from "./helpers";

const output = "../artifacts/assistant-chat-open-20261108/browser";

test("app-opening design states fit and expose no reply approvals", async ({
  page,
  browserName,
}) => {
  await page.goto("/design?assistant&native");
  await expect(
    page.getByRole("heading", { name: "Computer use · Your Mac" }),
  ).toBeVisible();
  await mkdir(output, { recursive: true });
  const checks = [];
  for (const state of [
    "queued",
    "running",
    "needs input",
    "complete",
    "cancelled",
    "failed",
    "interrupted",
    "outcome unknown",
  ]) {
    await page.getByRole("button", { name: state, exact: true }).click();
    await settle(page);
    const card = page.getByRole("article", {
      name: "Computer task",
      exact: true,
    });
    await expect(card).toContainText("Your Mac");
    await expect(
      card.getByRole("button", { name: /Send|Apply|Edit/ }),
    ).toHaveCount(0);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBeTruthy();
    const scan = await new AxeBuilder({ page }).analyze();
    expect(
      scan.violations.filter((v) =>
        ["serious", "critical"].includes(v.impact ?? ""),
      ),
    ).toEqual([]);
    await page.screenshot({
      path: `${output}/${state.replaceAll(" ", "-")}-${browserName}.png`,
      fullPage: true,
    });
    checks.push({ state, horizontalOverflow: false, seriousCritical: 0 });
  }
  await writeFile(
    `${output}/design-${browserName}.json`,
    JSON.stringify(checks, null, 2),
  );
});

test("typed app task persists through SSE and reload using only fake operations", async ({
  page,
  request,
}) => {
  await request.post(fakeAppURL + "/tests/assistant/setup?native_open=true");
  const before = (
    await (await request.get("http://127.0.0.1:18080/tests/state")).json()
  ).captures;
  await page.goto("/");
  await page.getByRole("button", { name: "Tools", exact: true }).click();
  await page.getByRole("menuitem", { name: /Use computer/ }).click();
  await expect(
    page.getByText(/Ask your local AI to open Notes or Messages/),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: /Messages demo|Notes demo|Tools/ }),
  ).toHaveCount(0);
  await page
    .getByRole("textbox", { name: "Message" })
    .fill("Please open Notes.");
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  const card = page.getByRole("article", {
    name: "Computer task",
    exact: true,
  });
  await expect(card.getByRole("status")).toHaveText("Opened Notes");
  await expect(card).toContainText("Your Mac");
  const url = page.url();
  expect(url).toContain("/c/");
  await page.reload();
  await page.getByRole("button", { name: "Tools", exact: true }).click();
  await page.getByRole("menuitem", { name: /Use computer/ }).click();
  await expect(card.getByRole("status")).toHaveText("Opened Notes");
  await expect(card.getByRole("button", { name: /Send|Apply/ })).toHaveCount(0);
  const after = (
    await (await request.get("http://127.0.0.1:18080/tests/state")).json()
  ).captures;
  const inference = (bodies: Record<string, unknown>[]) =>
    bodies.filter((body) => Object.keys(body).some((key) => key !== "model"));
  expect(inference(after)).toEqual(inference(before));
});

import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import {
  mkdir,
  readFile,
  mkdtemp,
  open,
  rm,
  writeFile,
} from "node:fs/promises";
import { tmpdir } from "node:os";
import { execFileSync } from "node:child_process";
import { settle } from "./helpers";
const dir = "../artifacts/phase-7/7a";
for (const width of [390, 1440])
  test(`7A Library upload collection reindex delete ${width}`, async ({
    page,
    request,
  }) => {
    await page.setViewportSize({ width, height: 900 });
    await request.delete("/api/library", { data: { confirmation: "DELETE" } });
    await request.post("/api/library/embedding", { data: { embedding: null } });
    const conn = (await (await request.get("/api/connections")).json())[0];
    await request.patch("/api/settings", {
      data: {
        default_connection_id: conn.id,
        default_model_id: "fake-chat",
        "library.document_prefix": "",
        "library.requires_local": true,
      },
    });
    await page.goto("/");
    await page.keyboard.press("Control+,");
    const settings = page.getByRole("dialog", {
      name: "Settings",
      exact: true,
    });
    await settings
      .getByRole("button", { name: "Library", exact: true })
      .click();
    await expect(
      settings.getByText("No files yet. Add one to start your Library."),
    ).toBeVisible();
    await settings
      .getByRole("combobox", { name: "Embedding model", exact: true })
      .click();
    await page
      .getByRole("option", { name: "fake-embedding", exact: true })
      .click();
    await page
      .getByRole("button", { name: "Change model", exact: true })
      .click();
    await expect(
      settings.getByText("8 dimensions", { exact: false }),
    ).toBeVisible();
    await settings
      .getByRole("button", { name: "New collection", exact: true })
      .click();
    await page
      .getByRole("textbox", { name: "Collection name" })
      .fill("Invented orchard");
    await page.getByRole("button", { name: "Save", exact: true }).click();
    await settings
      .getByRole("combobox", { name: "Collection for new files" })
      .click();
    await page
      .getByRole("option", { name: "Invented orchard", exact: true })
      .click();
    await settings
      .locator("input[type=file]")
      .setInputFiles("../server/tests/fixtures/documents/two-pages.pdf");
    const row = settings.getByRole("article", {
      name: "Library file two-pages.pdf",
    });
    await expect(row.getByRole("status")).toHaveText("Ready");
    await expect(row).toContainText("2 pages");
    await expect(row).toContainText("Invented orchard");
    await settings
      .locator("input[type=file]")
      .setInputFiles("../server/tests/fixtures/documents/two-pages.pdf");
    await expect(settings.getByRole("alert")).toContainText(
      "already in the Library",
    );
    await settings
      .getByRole("combobox", { name: "Embedding model", exact: true })
      .click();
    await page
      .getByRole("option", { name: "fake-embedding-alt", exact: true })
      .click();
    await page
      .getByRole("button", { name: "Change model", exact: true })
      .click();
    await expect(row.getByRole("status")).toHaveText("Needs re-indexing");
    await settings
      .getByRole("button", { name: "Re-index library", exact: true })
      .click();
    await expect(row.getByRole("status")).toHaveText("Ready");
    await settings
      .getByRole("button", { name: "Actions for collection Invented orchard" })
      .click();
    await page
      .getByRole("menuitem", { name: "Delete collection", exact: true })
      .click();
    await page.getByRole("button", { name: "Delete", exact: true }).click();
    await expect(row).toContainText("Unfiled");
    await settings
      .getByRole("button", { name: "Delete all library files", exact: true })
      .click();
    const clear = page.getByRole("dialog", {
      name: "Delete all Library files?",
    });
    await expect(
      clear.getByRole("button", { name: "Delete", exact: true }),
    ).toBeDisabled();
    await clear
      .getByRole("textbox", { name: "Type DELETE to confirm" })
      .fill("DELETE");
    await clear.getByRole("button", { name: "Delete", exact: true }).click();
    await expect(
      settings.getByText("No files yet. Add one to start your Library."),
    ).toBeVisible();
    await page
      .getByRole("button", { name: "Close settings", exact: true })
      .click();
    await page
      .locator(".composer textarea")
      .fill("Synthetic chat after Library management");
    await expect(
      page.getByRole("button", { name: "Send message" }),
    ).toBeEnabled();
  });
for (const width of [390, 1440])
  for (const theme of ["light", "dark"])
    test(`7A Library states axe ${width} ${theme}`, async ({
      page,
      browserName,
    }) => {
      test.setTimeout(180000);
      await page.setViewportSize({ width, height: 900 });
      await page.goto("/design?library");
      await page.getByRole("button", { name: theme, exact: true }).click();
      await mkdir(dir + "/screenshots", { recursive: true });
      const results = [];
      const libraryStates = await page
        .locator('select[aria-label="Library preview state"] option')
        .allTextContents();
      expect(libraryStates.length).toBeGreaterThanOrEqual(21);
      for (const state of libraryStates) {
        await page
          .getByRole("combobox", { name: "Library preview state" })
          .selectOption(state);
        await settle(page);
        const result = await new AxeBuilder({ page }).analyze();
        const violations = result.violations.filter((v) =>
          ["serious", "critical"].includes(v.impact ?? ""),
        );
        results.push({ state, seriousCritical: violations.length });
        expect(violations, state).toEqual([]);
        expect(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
        ).toBeTruthy();
        if (
          ["Ready", "Embedding", "Delete all", "Change model"].includes(state)
        )
          await page.screenshot({
            path: `${dir}/screenshots/library-${state.toLowerCase().replaceAll(" ", "-")}-${width}-${theme}-${browserName}-fake.png`,
            animations: "disabled",
          });
        const dialog = page.getByRole("dialog");
        if (await dialog.count()) {
          await page.keyboard.press("Escape");
          await expect(dialog).not.toBeVisible();
        }
      }
      await writeFile(
        `${dir}/axe-${width}-${theme}-${browserName}-fake.json`,
        JSON.stringify(results, null, 2),
      );
    });
test("7A 100 MB Library upload server RSS growth below 20 MB", async ({
  page,
  request,
  browserName,
}) => {
  const folder = await mkdtemp(tmpdir() + "/workbench-library-memory-");
  const source = await readFile(
    "../server/tests/fixtures/documents/two-pages.pdf",
  );
  const path = folder + "/invented-large.pdf";
  const target = await open(path, "w"),
    bytes = 100 * 1024 ** 2;
  const tail = Buffer.from(
    source.toString().slice(source.toString().lastIndexOf("startxref")),
  );
  await target.write(source, 0, source.length, 0);
  await target.truncate(bytes);
  await target.write(tail, 0, tail.length, bytes - tail.length);
  await target.close();
  await request.delete("/api/library", { data: { confirmation: "DELETE" } });
  await page.goto("/");
  await page.keyboard.press("Control+,");
  const settings = page.getByRole("dialog", { name: "Settings", exact: true });
  await settings.getByRole("button", { name: "Library", exact: true }).click();
  const pid = execFileSync("lsof", ["-t", "-iTCP:8787", "-sTCP:LISTEN"], {
    encoding: "utf8",
  })
    .trim()
    .split("\n")[0];
  const rss = () =>
    Number(
      execFileSync("ps", ["-o", "rss=", "-p", pid], {
        encoding: "utf8",
      }).trim(),
    ) * 1024;
  const baseline = rss(),
    samples = [baseline],
    sampling = setInterval(() => samples.push(rss()), 50);
  try {
    await settings.locator("input[type=file]").setInputFiles(path);
    await expect(
      settings.getByRole("article", {
        name: "Library file invented-large.pdf",
      }),
    ).toBeVisible();
    const peak = Math.max(...samples, rss());
    const result = {
      bytes,
      baseline,
      peak,
      growth: peak - baseline,
      samples: samples.length,
      method:
        "100 MiB browser multipart upload; server RSS every 50 ms; extraction subprocess excluded",
    };
    await mkdir(dir, { recursive: true });
    await writeFile(
      `${dir}/upload-memory-${browserName}-fake.json`,
      JSON.stringify(result, null, 2),
    );
    expect(result.growth).toBeLessThanOrEqual(20 * 1024 ** 2);
  } finally {
    clearInterval(sampling);
    await request.delete("/api/library", { data: { confirmation: "DELETE" } });
    await rm(folder, { recursive: true, force: true });
  }
});

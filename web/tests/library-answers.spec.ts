import { test, expect, type APIRequestContext } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir } from "node:fs/promises";
import { settle } from "./helpers";

const dir = "../artifacts/phase-7/7b";
async function setup(
  request: APIRequestContext,
  theme: "light" | "dark" = "light",
) {
  await request.delete("/api/library", { data: { confirmation: "DELETE" } });
  const conn = (await (await request.get("/api/connections")).json())[0];
  await request.patch("/api/settings", {
    data: {
      auto_title: false,
      "appearance.theme": theme,
      "appearance.font": "serif",
      "appearance.size": "M",
      "appearance.reduce_motion": "system",
      default_connection_id: conn.id,
      default_model_id: "fake-chat",
      "web.default_on": false,
      "library.requires_local": true,
      "library.query_prefix": "",
      "library.document_prefix": "",
    },
  });
  await request.post("/api/library/embedding", {
    data: { embedding: { connection_id: conn.id, model_id: "fake-embedding" } },
  });
  const collection = await (
    await request.post("/api/library/collections", {
      data: { name: "Invented policies" },
    })
  ).json();
  const body = await (
    await request.post("/api/library/documents", {
      multipart: {
        collection_id: collection.id,
        file: {
          name: "Invented-handbook.pdf",
          mimeType: "application/pdf",
          buffer: await import("node:fs/promises").then((fs) =>
            fs.readFile("../server/tests/fixtures/documents/two-pages.pdf"),
          ),
        },
      },
    })
  ).json();
  await expect
    .poll(
      async () =>
        (await (await request.get("/api/library")).json()).documents.find(
          (d: { id: string }) => d.id === body.id,
        )?.status,
    )
    .toBe("ready");
  return { doc: body.id, collection, conn };
}

for (const width of [390, 1440])
  for (const theme of ["light", "dark"] as const)
    test(`7B Library scope citations retained history ${width} ${theme}`, async ({
      page,
      request,
    }, testInfo) => {
      await setup(request, theme);
      await page.setViewportSize({ width, height: 900 });
      await page.addInitScript(
        (theme) => localStorage.setItem("workbench-theme", theme),
        theme,
      );
      await page.goto("/");
      await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
      const library = page.getByRole("button", {
        name: "Library",
        exact: true,
      });
      await expect(library).toHaveAttribute("aria-disabled", "false");
      await page
        .getByRole("button", { name: "Web search", exact: true })
        .click();
      await expect(
        page.getByRole("button", { name: "Web search", exact: true }),
      ).toHaveAttribute("aria-pressed", "true");
      await library.click();
      await expect(library).toHaveAttribute("aria-pressed", "true");
      await expect(
        page.getByRole("button", { name: "Web search", exact: true }),
      ).toHaveAttribute("aria-pressed", "false");
      await page
        .getByRole("button", { name: "Choose Library collections" })
        .click();
      await page.getByRole("checkbox", { name: "Invented policies" }).check();
      await page.keyboard.press("Escape");
      const composer = page.locator(".composer textarea");
      await composer.fill("#lib What does the invented handbook say?");
      await page
        .getByRole("button", { name: "Send message", exact: true })
        .click();
      await expect(page.getByTestId("library-activity")).toContainText(
        "Searched your files",
      );
      await expect(
        page.getByRole("button", { name: "Send message", exact: true }),
      ).toBeVisible();
      const citation = page
        .getByRole("button", {
          name: "View source: Invented-handbook.pdf",
          exact: true,
        })
        .first();
      await expect(citation).toBeVisible();
      await citation.click();
      await expect(
        page.getByRole("link", { name: "Open file ↗" }),
      ).toHaveAttribute("href", /#page=1/);
      await expect(page.getByLabel("Citation sources")).toContainText(
        "Invented silver orchard",
      );
      await settle(page);
      expect(
        (await new AxeBuilder({ page }).analyze()).violations.filter((v) =>
          ["serious", "critical"].includes(v.impact ?? ""),
        ),
      ).toEqual([]);
      await mkdir(dir, { recursive: true });
      await page.screenshot({
        path: `${dir}/fake-library-card-${width}-${theme}-${testInfo.project.name}.png`,
      });
      await page.getByRole("button", { name: "Close citation" }).click();
      await page.getByRole("button", { name: /1 sources/ }).click();
      await page.getByRole("button", { name: "What the model saw" }).click();
      await expect(
        page.getByRole("dialog", { name: "Sources", exact: true }),
      ).toContainText("Invented silver orchard");
      await settle(page);
      expect(
        (await new AxeBuilder({ page }).analyze()).violations.filter((v) =>
          ["serious", "critical"].includes(v.impact ?? ""),
        ),
      ).toEqual([]);
      await page.screenshot({
        path: `${dir}/fake-library-sources-${width}-${theme}-${testInfo.project.name}.png`,
      });
      await page.keyboard.press("Escape");
      const snapshot = await (await request.get("/api/library")).json();
      await request.delete(
        `/api/library/documents/${snapshot.documents[0].id}`,
      );
      await page.reload();
      await expect(citation).toBeVisible();
      await citation.click();
      await expect(
        page.getByText(
          "Original file removed. Saved passages remain available.",
        ),
      ).toBeVisible();
      await expect(page.getByRole("link", { name: "Open file ↗" })).toHaveCount(
        0,
      );
    });

test("7B Library touch targets and reasoning toolbar fit at 320 pixels", async ({
  page,
  request,
}) => {
  await setup(request);
  await request.patch("/api/settings", {
    data: { default_model_id: "fake-reasoning" },
  });
  await page.setViewportSize({ width: 320, height: 900 });
  await page.goto("/");
  await expect(page.getByRole("button", { name: /^Think:/ })).toBeVisible();
  for (const name of ["Library", "Choose Library collections"]) {
    const button = page.getByRole("button", { name, exact: true });
    await expect(button).toBeVisible();
    const box = await button.boundingBox();
    expect(box).not.toBeNull();
    expect(box!.width).toBeGreaterThanOrEqual(44);
    expect(box!.height).toBeGreaterThanOrEqual(44);
    expect(box!.x).toBeGreaterThanOrEqual(0);
    expect(box!.x + box!.width).toBeLessThanOrEqual(320);
  }
  await page.getByRole("button", { name: "Library", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Library", exact: true }),
  ).toHaveAttribute("aria-pressed", "true");
  const send = await page
    .getByRole("button", { name: "Send message", exact: true })
    .boundingBox();
  expect(send).not.toBeNull();
  expect(send!.x + send!.width).toBeLessThanOrEqual(320);
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth),
  ).toBeLessThanOrEqual(320);
});

test("7B disabled Library can be turned off; missing files and failure notices", async ({
  page,
  request,
}, testInfo) => {
  await request.delete("/api/library", { data: { confirmation: "DELETE" } });
  await request.post("/api/library/embedding", { data: { embedding: null } });
  await page.goto("/");
  const library = page.getByRole("button", { name: "Library", exact: true });
  await expect(library).toHaveAttribute("aria-disabled", "true");
  if (testInfo.project.name === "webkit") {
    await page
      .getByRole("button", { name: "Choose Library collections" })
      .click();
    await expect(page.getByLabel("Library scope")).toContainText(
      "Choose an embedding model",
    );
    await page.keyboard.press("Escape");
  } else {
    await library.focus();
    await expect(page.getByRole("tooltip")).toContainText(
      "Choose an embedding model",
    );
  }
  const conn = (await (await request.get("/api/connections")).json())[0];
  const item = await (
    await request.post("/api/chats", {
      data: { connection_id: conn.id, model_id: "fake-chat" },
    })
  ).json();
  await request.patch(`/api/chats/${item.id}`, {
    data: { library_enabled: true },
  });
  await page.goto(`/c/${item.id}`);
  await page.locator(".composer textarea").fill("#lib Synthetic empty scope");
  await page.getByRole("button", { name: "Send message", exact: true }).click();
  await expect(page.getByTestId("library-activity")).toContainText(
    "No ready files in this scope",
  );
  await library.click();
  await expect(library).toHaveAttribute("aria-pressed", "false");
});

test("7B all synthetic answer states axe and keyboard", async ({
  page,
}, testInfo) => {
  for (const width of [390, 1440])
    for (const theme of ["light", "dark"] as const) {
      await page.setViewportSize({ width, height: 900 });
      await page.emulateMedia({ colorScheme: theme });
      await page.goto("/design");
      await page
        .getByRole("button", {
          name: theme === "light" ? "Light" : "Dark",
          exact: true,
        })
        .click();
      await page.goto("/design?library-answers");
      await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
      await mkdir(dir + "/states", { recursive: true });
      for (const state of [
        "Ready",
        "Searching",
        "Empty scope",
        "Failed",
        "Uncited",
        "Removed file",
        "No embedding",
        "No ready files",
        "Remote model",
        "Collections",
      ]) {
        await page.getByRole("button", { name: state, exact: true }).click();
        await settle(page);
        const citations = page.getByRole("button", {
          name: "View source: Invented-handbook.pdf",
          exact: true,
        });
        if (
          [
            "Searching",
            "Empty scope",
            "Failed",
            "Uncited",
            "No embedding",
            "No ready files",
            "Remote model",
          ].includes(state)
        ) {
          await expect(citations).toHaveCount(0);
        } else {
          await expect(citations).toHaveCount(1);
        }
        if (
          ["No embedding", "No ready files", "Remote model"].includes(state)
        ) {
          await expect(
            page.getByRole("button", { name: "Library", exact: true }),
          ).toHaveAttribute("aria-disabled", "true");
          await expect(page.getByTestId("library-activity")).toHaveCount(0);
        }
        if (
          [
            "Searching",
            "Empty scope",
            "Failed",
            "No embedding",
            "No ready files",
            "Remote model",
          ].includes(state)
        ) {
          await expect(
            page.getByRole("button", { name: /1 sources/ }),
          ).toHaveCount(0);
        }
        expect(
          (await new AxeBuilder({ page }).analyze()).violations.filter((v) =>
            ["serious", "critical"].includes(v.impact ?? ""),
          ),
        ).toEqual([]);
        await page.screenshot({
          path: `${dir}/states/fake-library-answer-${state.toLowerCase().replaceAll(" ", "-")}-${width}-${theme}-${testInfo.project.name}.png`,
        });
      }
      await page
        .getByRole("button", { name: "Choose Library collections" })
        .click();
      await settle(page);
      expect(
        (await new AxeBuilder({ page }).analyze()).violations.filter((v) =>
          ["serious", "critical"].includes(v.impact ?? ""),
        ),
      ).toEqual([]);
      await page.keyboard.press("Escape");
      await expect(page.getByLabel("Library scope")).toHaveCount(0);
      await expect(
        page.getByRole("button", { name: "Choose Library collections" }),
      ).toBeFocused();
      await mkdir(dir, { recursive: true });
      await page.screenshot({
        path: `${dir}/fake-library-answer-preview-${width}-${theme}-${testInfo.project.name}.png`,
      });
    }
});

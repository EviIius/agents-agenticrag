import {
  test,
  expect,
  type Page,
  type APIRequestContext,
} from "@playwright/test";
import {
  readFile,
  mkdtemp,
  open,
  rm,
  writeFile,
  mkdir,
} from "node:fs/promises";
import { tmpdir } from "node:os";
import { execFileSync } from "node:child_process";
const fixtures = "../server/tests/fixtures/documents/";
async function setup(page: Page, request: APIRequestContext) {
  const pending = await (await request.get("/api/attachments/pending")).json();
  for (const item of pending)
    await request.delete(`/api/attachments/${item.id}`);
  const conn = (await (await request.get("/api/connections")).json())[0];
  await request.patch("/api/settings", {
    data: {
      default_connection_id: conn.id,
      default_model_id: "fake-chat",
      default_preset_id: null,
      auto_title: false,
    },
  });
  for (const model of ["fake-chat", "fake-vision"])
    await request.put("/api/models/prefs", {
      data: {
        connection_id: conn.id,
        model_id: model,
        params: {},
        context_length: model === "fake-chat" ? 16384 : 32768,
        display_name: null,
      },
    });
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: "Choose model" }),
  ).toContainText("fake-chat");
}
test.beforeEach(async ({ page, request }) => setup(page, request));
test("5B document picker, extracted review, Word table, send capture and edit note", async ({
  page,
  request,
}) => {
  await page.getByRole("button", { name: "Add attachment" }).click();
  const choosing = page.waitForEvent("filechooser");
  await page
    .getByRole("menuitem", { name: "Add document (PDF, Word)", exact: true })
    .click();
  const chooser = await choosing;
  await expect(page.locator("input[type=file]")).toHaveAttribute(
    "accept",
    ".docx,.pdf",
  );
  await chooser.setFiles([fixtures + "two-pages.pdf", fixtures + "table.docx"]);
  const chips = page.locator("[data-slot=document-chip]");
  await expect(chips).toHaveCount(2);
  await expect(chips.first()).toContainText("2 pages");
  await expect(chips.last()).toContainText("Word document");
  await page
    .getByRole("button", { name: "Review document two-pages.pdf" })
    .click();
  await expect(
    page.getByRole("dialog", { name: "What the model received" }),
  ).toBeVisible();
  await expect(page.locator("pre")).toContainText("[Page 1]");
  await expect(page.locator("pre")).toContainText("[Page 2]");
  await expect(page.locator("pre")).toContainText("silver orchard");
  await expect(
    page.getByRole("button", { name: "Copy", exact: true }),
  ).toBeEnabled();
  await page.getByRole("button", { name: "Close document" }).click();
  await page
    .getByRole("button", { name: "Review document table.docx" })
    .click();
  await expect(page.locator("pre")).toContainText("Lantern\tMeadow");
  await expect(page.locator("pre")).not.toContainText("Deleted");
  await page.getByRole("button", { name: "Close document" }).click();
  await page.locator(".composer textarea").fill("Invented document question");
  await page.getByRole("button", { name: "Send message" }).click();
  await expect(page).toHaveURL(/\/c\//);
  await expect(
    page.getByRole("button", { name: "Stop generating" }),
  ).toHaveCount(0);
  await expect(chips).toHaveCount(2);
  const captures = (
    await (await request.get("http://127.0.0.1:18080/tests/state")).json()
  ).captures;
  const captured = captures.findLast(
    (c: { messages?: { content: string }[] }) =>
      c.messages?.some((m) => m.content.includes("Invented document question")),
  );
  const text = captured.messages.at(-1).content;
  expect(text).toContain('<file name="two-pages.pdf">');
  expect(text).toContain("[Page 1]");
  expect(text).toContain("[Page 2]");
  expect(text).toContain('<file name="table.docx">');
  expect(text).toContain("Lantern\tMeadow");
  await page
    .getByRole("article", { name: "user message" })
    .getByRole("button", { name: "Edit message" })
    .click();
  await expect(
    page.getByText("Attachments aren't carried over when you edit.", {
      exact: false,
    }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Cancel", exact: true }).click();
});
test("5B document context warning follows model switch and removal deletes text", async ({
  page,
  request,
}) => {
  const uploaded = page.waitForResponse(
    (r) =>
      r.url().endsWith("/api/attachments") && r.request().method() === "POST",
  );
  await page
    .locator("input[type=file]")
    .setInputFiles(fixtures + "large-text.pdf");
  const item = await (await uploaded).json();
  await expect(page.locator("[data-slot=document-chip]")).toContainText(
    "Choose a model with a larger context",
  );
  await expect(
    page.getByText(/This message and its documents may exceed/),
  ).toBeVisible();
  const tokens = await page
    .locator(".composer [role=img]")
    .getAttribute("aria-label");
  expect(Number(tokens?.split(" ")[0])).toBeGreaterThan(16000);
  await page.getByRole("button", { name: "Choose model" }).click();
  await page.getByRole("option").filter({ hasText: "fake-vision" }).click();
  await expect(
    page.getByRole("button", { name: "Choose model" }),
  ).toContainText("fake-vision");
  await expect(
    page.getByText(/This message and its documents may exceed/),
  ).toHaveCount(0);
  await expect(page.locator("[data-slot=document-chip]")).not.toContainText(
    "Choose a model with a larger context",
  );
  await page
    .getByRole("button", { name: "Remove large-text.pdf", exact: true })
    .click();
  await expect(page.locator("[data-slot=document-chip]")).toHaveCount(0);
  expect((await request.get(`/api/attachments/${item.id}/info`)).status()).toBe(
    404,
  );
});
test("5B scanned, encrypted and damaged errors retain usable composer", async ({
  page,
}) => {
  for (const [file, text] of [
    ["scanned.pdf", "This PDF has no selectable text."],
    ["encrypted.pdf", "This PDF is password-protected."],
    ["damaged.pdf", "Couldn't read this file."],
  ]) {
    await page.locator("input[type=file]").setInputFiles(fixtures + file);
    await expect(page.getByText(text, { exact: false }).first()).toBeVisible();
    await page.getByRole("button", { name: "Remove failed upload" }).click();
    await expect(page.locator("[data-slot=document-chip]")).toHaveCount(0);
  }
  await page.locator(".composer textarea").fill("Still editable");
  await expect(
    page.getByRole("button", { name: "Send message" }),
  ).toBeEnabled();
  await page.getByRole("button", { name: "Add attachment" }).click();
  const choosing = page.waitForEvent("filechooser");
  await page.getByRole("menuitem", { name: "Add text file" }).click();
  const chooser = await choosing;
  await expect(page.locator("input[type=file]")).toHaveAttribute(
    "accept",
    /\.swift/,
  );
  await chooser.setFiles({
    name: "invented.swift",
    mimeType: "text/plain",
    buffer: Buffer.from("Invented text file"),
  });
  await expect(
    page.getByRole("button", { name: "Remove invented.swift" }),
  ).toBeVisible();
});
test("5B paste and drop documents use the same upload path", async ({
  page,
}) => {
  const bytes = [...(await readFile(fixtures + "two-pages.pdf"))];
  await page.locator(".composer textarea").evaluate((node, bytes) => {
    const data = new DataTransfer();
    data.items.add(
      new File([new Uint8Array(bytes)], "two-pages.pdf", {
        type: "application/pdf",
      }),
    );
    node.dispatchEvent(
      new ClipboardEvent("paste", {
        clipboardData: data,
        bubbles: true,
        cancelable: true,
      }),
    );
  }, bytes);
  await expect(page.locator("[data-slot=document-chip]")).toHaveCount(1);
  await page.getByRole("button", { name: "Remove two-pages.pdf" }).click();
  await expect(page.locator("[data-slot=document-chip]")).toHaveCount(0);
  await page.locator(".app-main").evaluate((node, bytes) => {
    const data = new DataTransfer();
    data.items.add(
      new File([new Uint8Array(bytes)], "two-pages.pdf", {
        type: "application/pdf",
      }),
    );
    node.dispatchEvent(
      new DragEvent("dragenter", {
        dataTransfer: data,
        bubbles: true,
        cancelable: true,
      }),
    );
  }, bytes);
  await expect(
    page.getByText("Drop images, documents, text files or recordings"),
  ).toBeVisible();
  await page.locator(".app-main").evaluate((node, bytes) => {
    const data = new DataTransfer();
    data.items.add(
      new File([new Uint8Array(bytes)], "two-pages.pdf", {
        type: "application/pdf",
      }),
    );
    node.dispatchEvent(
      new DragEvent("drop", {
        dataTransfer: data,
        bubbles: true,
        cancelable: true,
      }),
    );
  }, bytes);
  await expect(page.locator("[data-slot=document-chip]")).toHaveCount(1);
});
test("5B 50 MB browser upload keeps server RSS growth below 20 MB", async ({
  page,
  browserName,
}) => {
  const folder = await mkdtemp(tmpdir() + "/workbench-document-memory-");
  const source = await readFile(fixtures + "two-pages.pdf");
  const path = folder + "/invented-large.pdf";
  const target = await open(path, "w");
  const size = 50 * 1024 ** 2;
  const tail = Buffer.from(
    source.toString().slice(source.toString().lastIndexOf("startxref")),
  );
  await target.write(source, 0, source.length, 0);
  await target.truncate(size);
  await target.write(tail, 0, tail.length, size - tail.length);
  await target.close();
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
    samples = [baseline];
  const started = Date.now();
  const sampling = setInterval(() => samples.push(rss()), 50);
  try {
    await page.locator("input[type=file]").setInputFiles(path);
    await expect(
      page.getByRole("button", { name: "Review document invented-large.pdf" }),
    ).toBeVisible();
    const peak = Math.max(...samples, rss());
    const result = {
      method:
        "50 MiB real browser XHR upload; uvicorn ps RSS sampled every 50ms; worker excluded",
      bytes: size,
      baseline,
      peak,
      growth: peak - baseline,
      samples: samples.length,
      seconds: (Date.now() - started) / 1000,
    };
    await mkdir("../artifacts/phase-5/5b", { recursive: true });
    await writeFile(
      `../artifacts/phase-5/5b/upload-memory-${browserName}-fake.json`,
      JSON.stringify(result, null, 2),
    );
    expect(result.growth).toBeLessThanOrEqual(20 * 1024 ** 2);
    await page
      .getByRole("button", { name: "Remove invented-large.pdf" })
      .click();
  } finally {
    clearInterval(sampling);
    await rm(folder, { recursive: true, force: true });
  }
});

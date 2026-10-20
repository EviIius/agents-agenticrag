import { enterImageMode } from "./helpers";
import { expect, test } from "@playwright/test";
import { mkdir, readFile } from "node:fs/promises";
import AxeBuilder from "@axe-core/playwright";
import { settle } from "./helpers";

test.beforeEach(async ({ page, request }) => {
  const connection = (await (await request.get("/api/connections")).json())[0];
  await request.patch("/api/settings", {
    data: {
      default_connection_id: connection.id,
      default_model_id: "fake-vision",
      default_preset_id: null,
      auto_title: false,
    },
  });
  await page.goto("/");
  await expect(
    page.getByRole("button", { name: "Choose model" }),
  ).toContainText("fake-vision");
});

test("image chooser accepts PNG, JPEG, WebP, GIF, HEIC and renamed HEIC", async ({
  page,
}) => {
  const heic = await readFile(
    "../server/tests/fixtures/images/fake-synthetic.heic",
  );
  const png = await readFile(
    "../server/tests/fixtures/images/fake-synthetic.png",
  );
  const cases = [
    { name: "fake-heic.heic", mimeType: "image/heic", buffer: heic },
    { name: "fake-renamed.png", mimeType: "image/png", buffer: heic },
    {
      name: "fake-empty-mime.PNG",
      mimeType: "application/octet-stream",
      buffer: png,
    },
    {
      name: "fake.gif",
      mimeType: "image/gif",
      buffer: Buffer.from(
        "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",
        "base64",
      ),
    },
  ];
  for (const mimeType of ["image/png", "image/jpeg", "image/webp"]) {
    const data = await page.evaluate((mime) => {
      const canvas = document.createElement("canvas");
      canvas.width = 24;
      canvas.height = 12;
      const ctx = canvas.getContext("2d")!;
      ctx.fillStyle = "rgb(25, 75, 150)";
      ctx.fillRect(0, 0, 24, 12);
      return canvas.toDataURL(mime).split(",")[1];
    }, mimeType);
    cases.push({
      name: "fake." + mimeType.split("/")[1],
      mimeType,
      buffer: Buffer.from(data, "base64"),
    });
  }
  for (const item of cases) {
    const uploading = page.waitForResponse(
      (response) =>
        response.url().endsWith("/api/attachments") &&
        response.request().method() === "POST",
    );
    await page.locator("input.composer-file-input").setInputFiles(item);
    const response = await uploading;
    expect(response.status()).toBe(201);
    const attachment = await response.json();
    expect(attachment.kind).toBe("image");
    expect(["image/png", "image/jpeg"]).toContain(attachment.mime_type);
    await expect(
      page
        .locator("[data-slot=attachment-chip]:not([inert] *)")
        .filter({ hasText: attachment.filename }),
    ).toBeVisible();
    await expect(
      page.locator("[data-slot=attachment-chip]:not([inert] *)"),
    ).toHaveCount(1);
    await page
      .getByRole("button", {
        name: `Remove ${attachment.filename}`,
        exact: true,
      })
      .click();
  }
  await expect(
    page.locator("[data-slot=attachment-chip]:not([inert] *)"),
  ).toHaveCount(0);
});

test("attaching an image leaves creation mode and exposes its chat chip", async ({
  page,
}) => {
  await enterImageMode(page);
  await expect(
    page.getByRole("textbox", { name: "Image prompt" }),
  ).toBeVisible();
  await page
    .locator("input.composer-file-input")
    .setInputFiles("../server/tests/fixtures/images/fake-synthetic.png");
  await expect(
    page.locator("[data-slot=attachment-chip]:not([inert] *)"),
  ).toHaveCount(1);
  await expect(
    page.getByRole("button", { name: "Leave image mode", exact: true }),
  ).not.toBeVisible();
  // Existing chat attachments do not prevent an explicit later switch back.
  await enterImageMode(page);
  await expect(
    page.getByRole("textbox", { name: "Image prompt" }),
  ).toBeVisible();
});

test("restoring a pending recording preserves explicitly requested Image mode", async ({
  page,
  request,
}) => {
  const response = await request.post("/api/attachments", {
    multipart: {
      file: {
        name: "Synthetic restored recording.wav",
        mimeType: "audio/wav",
        buffer: Buffer.from("fake"),
      },
    },
  });
  expect(response.status()).toBe(201);
  const recording = await response.json();
  try {
    await page.goto("/?image=1");
    await expect(
      page.getByRole("textbox", { name: "Image prompt", exact: true }),
    ).toBeVisible();
    await page
      .getByRole("button", { name: "Leave image mode", exact: true })
      .click();
    await expect(
      page.getByRole("button", {
        name: "Open transcript for Synthetic restored recording.wav",
        exact: true,
      }),
    ).toBeVisible();
    await enterImageMode(page);
    await expect(
      page.getByRole("textbox", { name: "Image prompt", exact: true }),
    ).toBeVisible();
    await page.reload();
    await settle(page);
    await expect(
      page.getByRole("textbox", { name: "Image prompt", exact: true }),
    ).toBeVisible();
  } finally {
    await request.delete(`/api/attachments/${recording.id}`);
  }
});

test("unreadable image gives useful upload feedback", async ({ page }) => {
  let requests = 0;
  page.on("request", (r) => {
    if (r.method() === "POST" && r.url().endsWith("/api/attachments"))
      requests++;
  });
  await page.locator("input.composer-file-input").setInputFiles({
    name: "fake-broken.png",
    mimeType: "image/png",
    buffer: Buffer.from("invalid image"),
  });
  await expect(
    page
      .getByText(
        "Couldn't open this image. Export it as a JPEG or PNG and try again.",
      )
      .first(),
  ).toBeVisible();
  await expect(
    page.locator(
      '[data-slot=attachment-chip]:not([inert] *)[data-issue="error"]',
    ),
  ).toHaveCount(1);
  expect(requests).toBe(0);
  await page
    .locator(".composer textarea")
    .fill("Synthetic request without the failed upload");
  await expect(
    page.getByRole("button", { name: "Send message", exact: true }),
  ).toBeEnabled();
});

test("HEIC paste and drop share the chooser normalization path", async ({
  page,
}) => {
  const bytes = [
    ...(await readFile("../server/tests/fixtures/images/fake-synthetic.heic")),
  ];
  await enterImageMode(page);
  for (const eventType of ["paste", "drop"]) {
    const uploading = page.waitForResponse(
      (response) =>
        response.url().endsWith("/api/attachments") &&
        response.request().method() === "POST",
    );
    const target = eventType === "paste" ? ".composer textarea" : ".app-main";
    await page.locator(target).evaluate(
      (node, { bytes, eventType }) => {
        const data = new DataTransfer();
        data.items.add(
          new File([new Uint8Array(bytes)], "fake-pasted.png", {
            type: "image/png",
          }),
        );
        node.dispatchEvent(
          eventType === "paste"
            ? new ClipboardEvent("paste", {
                clipboardData: data,
                bubbles: true,
                cancelable: true,
              })
            : new DragEvent("drop", {
                dataTransfer: data,
                bubbles: true,
                cancelable: true,
              }),
        );
      },
      { bytes, eventType },
    );
    const response = await uploading;
    expect(response.status()).toBe(201);
    expect((await response.json()).mime_type).toBe("image/png");
    await expect(
      page.locator("[data-slot=attachment-chip]:not([inert] *)"),
    ).toHaveCount(1);
    await expect(
      page.getByRole("button", { name: "Leave image mode", exact: true }),
    ).not.toBeVisible();
    await page
      .getByRole("button", {
        name:
          eventType === "paste"
            ? "Remove Pasted image 1.png"
            : "Remove fake-pasted.png",
        exact: true,
      })
      .click();
  }
});

test("synthetic upload chip and failure stay accessible in both themes and widths", async ({
  page,
}, info) => {
  const folder = "../artifacts/image-upload-heic/screenshots";
  await mkdir(folder, { recursive: true });
  for (const theme of ["light", "dark"]) {
    for (const width of [390, 1440]) {
      await page.setViewportSize({ width, height: 900 });
      await page.evaluate(
        (value) => localStorage.setItem("workbench-theme", value),
        theme,
      );
      await page.reload();
      await page
        .locator("input.composer-file-input")
        .setInputFiles("../server/tests/fixtures/images/fake-synthetic.heic");
      await expect(
        page.locator("[data-slot=attachment-chip]:not([inert] *)"),
      ).toHaveCount(1);
      await page.locator("input.composer-file-input").setInputFiles({
        name: "fake-broken.png",
        mimeType: "image/png",
        buffer: Buffer.from("invalid image"),
      });
      await expect(
        page
          .getByText(
            "Couldn't open this image. Export it as a JPEG or PNG and try again.",
          )
          .first(),
      ).toBeVisible();
      await settle(page);
      const audit = await new AxeBuilder({ page }).analyze();
      expect(
        audit.violations.filter((item) =>
          ["serious", "critical"].includes(item.impact ?? ""),
        ),
      ).toEqual([]);
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBe(true);
      await page.screenshot({
        path: `${folder}/fake-upload-${info.project.name}-${width}-${theme}.png`,
      });
      await page
        .getByRole("button", { name: "Remove fake-synthetic.png", exact: true })
        .click();
    }
  }
});

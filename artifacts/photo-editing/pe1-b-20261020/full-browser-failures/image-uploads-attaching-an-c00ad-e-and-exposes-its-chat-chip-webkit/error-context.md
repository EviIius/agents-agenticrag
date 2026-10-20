# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: image-uploads.spec.ts >> attaching an image leaves creation mode and exposes its chat chip
- Location: tests/image-uploads.spec.ts:97:1

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: locator.setInputFiles: Test timeout of 45000ms exceeded.
Call log:
  - waiting for locator('input.composer-file-input')

```

# Page snapshot

```yaml
- generic [ref=e2]:
  - main [ref=e4]:
    - generic [ref=e5]:
      - generic [ref=e6]:
        - button "Open sidebar" [ref=e7] [cursor=pointer]
        - button "Choose model" [ref=e9] [cursor=pointer]:
          - generic [aria-hidden] [ref=e10]: ●
          - generic [ref=e11]: fake-vision
      - button "Chat controls" [ref=e12] [cursor=pointer]
    - generic [ref=e13]:
      - heading "Good morning" [level=1] [ref=e14]
      - form "Message" [ref=e15]:
        - textbox "Image prompt" [active] [ref=e16]:
          - /placeholder: Describe an image…
        - generic [ref=e17]:
          - button "Leave image mode" [pressed] [ref=e18] [cursor=pointer]: Image
          - button "Image count" [ref=e19] [cursor=pointer]: 1 image
          - button "Image options" [ref=e20] [cursor=pointer]
          - generic [ref=e22]:
            - button "Create image" [disabled]
      - paragraph [ref=e23]: Your models. Your Mac.
  - region "Notifications alt+T"
```

# Test source

```ts
  4   | import AxeBuilder from "@axe-core/playwright";
  5   | import { settle } from "./helpers";
  6   | 
  7   | test.beforeEach(async ({ page, request }) => {
  8   |   const connection = (await (await request.get("/api/connections")).json())[0];
  9   |   await request.patch("/api/settings", {
  10  |     data: {
  11  |       default_connection_id: connection.id,
  12  |       default_model_id: "fake-vision",
  13  |       default_preset_id: null,
  14  |       auto_title: false,
  15  |     },
  16  |   });
  17  |   await page.goto("/");
  18  |   await expect(
  19  |     page.getByRole("button", { name: "Choose model" }),
  20  |   ).toContainText("fake-vision");
  21  | });
  22  | 
  23  | test("image chooser accepts PNG, JPEG, WebP, GIF, HEIC and renamed HEIC", async ({
  24  |   page,
  25  | }) => {
  26  |   const heic = await readFile(
  27  |     "../server/tests/fixtures/images/fake-synthetic.heic",
  28  |   );
  29  |   const png = await readFile(
  30  |     "../server/tests/fixtures/images/fake-synthetic.png",
  31  |   );
  32  |   const cases = [
  33  |     { name: "fake-heic.heic", mimeType: "image/heic", buffer: heic },
  34  |     { name: "fake-renamed.png", mimeType: "image/png", buffer: heic },
  35  |     {
  36  |       name: "fake-empty-mime.PNG",
  37  |       mimeType: "application/octet-stream",
  38  |       buffer: png,
  39  |     },
  40  |     {
  41  |       name: "fake.gif",
  42  |       mimeType: "image/gif",
  43  |       buffer: Buffer.from(
  44  |         "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7",
  45  |         "base64",
  46  |       ),
  47  |     },
  48  |   ];
  49  |   for (const mimeType of ["image/png", "image/jpeg", "image/webp"]) {
  50  |     const data = await page.evaluate((mime) => {
  51  |       const canvas = document.createElement("canvas");
  52  |       canvas.width = 24;
  53  |       canvas.height = 12;
  54  |       const ctx = canvas.getContext("2d")!;
  55  |       ctx.fillStyle = "rgb(25, 75, 150)";
  56  |       ctx.fillRect(0, 0, 24, 12);
  57  |       return canvas.toDataURL(mime).split(",")[1];
  58  |     }, mimeType);
  59  |     cases.push({
  60  |       name: "fake." + mimeType.split("/")[1],
  61  |       mimeType,
  62  |       buffer: Buffer.from(data, "base64"),
  63  |     });
  64  |   }
  65  |   for (const item of cases) {
  66  |     const uploading = page.waitForResponse(
  67  |       (response) =>
  68  |         response.url().endsWith("/api/attachments") &&
  69  |         response.request().method() === "POST",
  70  |     );
  71  |     await page.locator("input.composer-file-input").setInputFiles(item);
  72  |     const response = await uploading;
  73  |     expect(response.status()).toBe(201);
  74  |     const attachment = await response.json();
  75  |     expect(attachment.kind).toBe("image");
  76  |     expect(["image/png", "image/jpeg"]).toContain(attachment.mime_type);
  77  |     await expect(
  78  |       page
  79  |         .locator("[data-slot=attachment-chip]:not([inert] *)")
  80  |         .filter({ hasText: attachment.filename }),
  81  |     ).toBeVisible();
  82  |     await expect(
  83  |       page.locator("[data-slot=attachment-chip]:not([inert] *)"),
  84  |     ).toHaveCount(1);
  85  |     await page
  86  |       .getByRole("button", {
  87  |         name: `Remove ${attachment.filename}`,
  88  |         exact: true,
  89  |       })
  90  |       .click();
  91  |   }
  92  |   await expect(
  93  |     page.locator("[data-slot=attachment-chip]:not([inert] *)"),
  94  |   ).toHaveCount(0);
  95  | });
  96  | 
  97  | test("attaching an image leaves creation mode and exposes its chat chip", async ({
  98  |   page,
  99  | }) => {
  100 |   await enterImageMode(page);
  101 |   await expect(
  102 |     page.getByRole("textbox", { name: "Image prompt" }),
  103 |   ).toBeVisible();
> 104 |   await page
      |   ^ Error: locator.setInputFiles: Test timeout of 45000ms exceeded.
  105 |     .locator("input.composer-file-input")
  106 |     .setInputFiles("../server/tests/fixtures/images/fake-synthetic.png");
  107 |   await expect(
  108 |     page.locator("[data-slot=attachment-chip]:not([inert] *)"),
  109 |   ).toHaveCount(1);
  110 |   await expect(
  111 |     page.getByRole("button", { name: "Leave image mode", exact: true }),
  112 |   ).not.toBeVisible();
  113 |   // Existing chat attachments do not prevent an explicit later switch back.
  114 |   await enterImageMode(page);
  115 |   await expect(
  116 |     page.getByRole("textbox", { name: "Image prompt" }),
  117 |   ).toBeVisible();
  118 | });
  119 | 
  120 | test("restoring a pending recording preserves explicitly requested Image mode", async ({
  121 |   page,
  122 |   request,
  123 | }) => {
  124 |   const response = await request.post("/api/attachments", {
  125 |     multipart: {
  126 |       file: {
  127 |         name: "Synthetic restored recording.wav",
  128 |         mimeType: "audio/wav",
  129 |         buffer: Buffer.from("fake"),
  130 |       },
  131 |     },
  132 |   });
  133 |   expect(response.status()).toBe(201);
  134 |   const recording = await response.json();
  135 |   try {
  136 |     await page.goto("/?image=1");
  137 |     await expect(
  138 |       page.getByRole("textbox", { name: "Image prompt", exact: true }),
  139 |     ).toBeVisible();
  140 |     await page
  141 |       .getByRole("button", { name: "Leave image mode", exact: true })
  142 |       .click();
  143 |     await expect(
  144 |       page.getByRole("button", {
  145 |         name: "Open transcript for Synthetic restored recording.wav",
  146 |         exact: true,
  147 |       }),
  148 |     ).toBeVisible();
  149 |     await enterImageMode(page);
  150 |     await expect(
  151 |       page.getByRole("textbox", { name: "Image prompt", exact: true }),
  152 |     ).toBeVisible();
  153 |     await page.reload();
  154 |     await settle(page);
  155 |     await expect(
  156 |       page.getByRole("textbox", { name: "Image prompt", exact: true }),
  157 |     ).toBeVisible();
  158 |   } finally {
  159 |     await request.delete(`/api/attachments/${recording.id}`);
  160 |   }
  161 | });
  162 | 
  163 | test("unreadable image gives useful upload feedback", async ({ page }) => {
  164 |   let requests = 0;
  165 |   page.on("request", (r) => {
  166 |     if (r.method() === "POST" && r.url().endsWith("/api/attachments"))
  167 |       requests++;
  168 |   });
  169 |   await page.locator("input.composer-file-input").setInputFiles({
  170 |     name: "fake-broken.png",
  171 |     mimeType: "image/png",
  172 |     buffer: Buffer.from("invalid image"),
  173 |   });
  174 |   await expect(
  175 |     page
  176 |       .getByText(
  177 |         "Couldn't open this image. Export it as a JPEG or PNG and try again.",
  178 |       )
  179 |       .first(),
  180 |   ).toBeVisible();
  181 |   await expect(
  182 |     page.locator(
  183 |       '[data-slot=attachment-chip]:not([inert] *)[data-issue="error"]',
  184 |     ),
  185 |   ).toHaveCount(1);
  186 |   expect(requests).toBe(0);
  187 |   await page
  188 |     .locator(".composer textarea")
  189 |     .fill("Synthetic request without the failed upload");
  190 |   await expect(
  191 |     page.getByRole("button", { name: "Send message", exact: true }),
  192 |   ).toBeEnabled();
  193 | });
  194 | 
  195 | test("HEIC paste and drop share the chooser normalization path", async ({
  196 |   page,
  197 | }) => {
  198 |   const bytes = [
  199 |     ...(await readFile("../server/tests/fixtures/images/fake-synthetic.heic")),
  200 |   ];
  201 |   await enterImageMode(page);
  202 |   for (const eventType of ["paste", "drop"]) {
  203 |     const uploading = page.waitForResponse(
  204 |       (response) =>
```
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
  - generic [ref=e3]:
    - complementary [ref=e4]:
      - generic [ref=e5]:
        - generic [ref=e6]:
          - button "Collapse sidebar" [ref=e7] [cursor=pointer]
          - generic [ref=e8]: Aether
          - link "New chat" [ref=e9] [cursor=pointer]:
            - /url: /
        - navigation "Chat history" [ref=e10]:
          - generic [ref=e11]:
            - textbox "Search history" [ref=e12]:
              - /placeholder: Search chats…
            - generic: ⌘K
          - navigation "Workspace" [ref=e13]:
            - link "Workflows" [ref=e15] [cursor=pointer]:
              - /url: /workflows
              - text: Workflows
              - img "A workflow is waiting for you" [ref=e20]
            - link "Images" [ref=e22] [cursor=pointer]:
              - /url: /images
          - region "Folders" [ref=e28]:
            - generic [ref=e29]:
              - heading "Folders" [level=2] [ref=e30]
              - button "New folder" [ref=e31] [cursor=pointer]
            - paragraph [ref=e32]: No folders yet
          - generic [ref=e33]:
            - paragraph [ref=e34]: Today
            - generic [ref=e35]:
              - link "Synthetic mobile handoff request" [ref=e36] [cursor=pointer]:
                - /url: /c/14d40fc7c62a417e86a074e3c0c4790a
              - button "Actions for Synthetic mobile handoff request" [ref=e37] [cursor=pointer]
          - generic [ref=e39]:
            - link "Who lost the 2021 NBA Finals? Show a table." [ref=e40] [cursor=pointer]:
              - /url: /c/817d611c213e47bbb6c14b9335f6186c
            - button "Actions for Who lost the 2021 NBA Finals? Show a table." [ref=e41] [cursor=pointer]
          - generic [ref=e43]:
            - link "Synthetic handoff history 44" [ref=e44] [cursor=pointer]:
              - /url: /c/87edd38d61d6441b96f392ee84fe6ec9
            - button "Actions for Synthetic handoff history 44" [ref=e45] [cursor=pointer]
          - generic [ref=e47]:
            - link "Synthetic handoff history 43" [ref=e48] [cursor=pointer]:
              - /url: /c/653fcdc1d4a24a47b3714e3b8ee447a9
            - button "Actions for Synthetic handoff history 43" [ref=e49] [cursor=pointer]
          - generic [ref=e51]:
            - link "Synthetic handoff history 42" [ref=e52] [cursor=pointer]:
              - /url: /c/8a7a424e110c46d78017e6f8129db48a
            - button "Actions for Synthetic handoff history 42" [ref=e53] [cursor=pointer]
          - generic [ref=e55]:
            - link "Synthetic handoff history 41" [ref=e56] [cursor=pointer]:
              - /url: /c/caee46328dc64525bc1af773c06b28ee
            - button "Actions for Synthetic handoff history 41" [ref=e57] [cursor=pointer]
          - generic [ref=e59]:
            - link "Synthetic handoff history 40" [ref=e60] [cursor=pointer]:
              - /url: /c/46b3e768ebd64b1e9a542d0d1d05b85d
            - button "Actions for Synthetic handoff history 40" [ref=e61] [cursor=pointer]
          - generic [ref=e63]:
            - link "Synthetic handoff history 39" [ref=e64] [cursor=pointer]:
              - /url: /c/a140707a5828462b989f5c4ebcf43ac1
            - button "Actions for Synthetic handoff history 39" [ref=e65] [cursor=pointer]
          - generic [ref=e67]:
            - link "Synthetic handoff history 38" [ref=e68] [cursor=pointer]:
              - /url: /c/e61898bd0f3246d6942b1e8a88fca320
            - button "Actions for Synthetic handoff history 38" [ref=e69] [cursor=pointer]
          - generic [ref=e71]:
            - link "Synthetic handoff history 37" [ref=e72] [cursor=pointer]:
              - /url: /c/0bd513bce1ea4eaea0a17f188cbf14f8
            - button "Actions for Synthetic handoff history 37" [ref=e73] [cursor=pointer]
          - generic [ref=e75]:
            - link "Synthetic handoff history 36" [ref=e76] [cursor=pointer]:
              - /url: /c/46f8d8ba7e24450c8ee98fdfc65a8510
            - button "Actions for Synthetic handoff history 36" [ref=e77] [cursor=pointer]
          - generic [ref=e79]:
            - link "Synthetic handoff history 35" [ref=e80] [cursor=pointer]:
              - /url: /c/bbe2715acfc449da836f9b87445d9d6f
            - button "Actions for Synthetic handoff history 35" [ref=e81] [cursor=pointer]
          - generic [ref=e83]:
            - link "Synthetic handoff history 34" [ref=e84] [cursor=pointer]:
              - /url: /c/428a0bbfc50e4bc8a26cf87a69072ba9
            - button "Actions for Synthetic handoff history 34" [ref=e85] [cursor=pointer]
          - generic [ref=e87]:
            - link "Synthetic handoff history 33" [ref=e88] [cursor=pointer]:
              - /url: /c/8a252f0d5b3a4dea9dc35284ccd36189
            - button "Actions for Synthetic handoff history 33" [ref=e89] [cursor=pointer]
          - generic [ref=e91]:
            - link "Synthetic handoff history 32" [ref=e92] [cursor=pointer]:
              - /url: /c/5810ae68307b4b5794c9cea994680492
            - button "Actions for Synthetic handoff history 32" [ref=e93] [cursor=pointer]
          - generic [ref=e95]:
            - link "Synthetic handoff history 31" [ref=e96] [cursor=pointer]:
              - /url: /c/6752f80e63da40ff897869e9eac45f34
            - button "Actions for Synthetic handoff history 31" [ref=e97] [cursor=pointer]
          - generic [ref=e99]:
            - link "Synthetic handoff history 30" [ref=e100] [cursor=pointer]:
              - /url: /c/e40b936f2e5b414eb6f6bfd49949011b
            - button "Actions for Synthetic handoff history 30" [ref=e101] [cursor=pointer]
          - generic [ref=e103]:
            - link "Synthetic handoff history 29" [ref=e104] [cursor=pointer]:
              - /url: /c/d043bcf82ecf475eac22747331cbd3d7
            - button "Actions for Synthetic handoff history 29" [ref=e105] [cursor=pointer]
          - generic [ref=e107]:
            - link "Synthetic handoff history 28" [ref=e108] [cursor=pointer]:
              - /url: /c/89d6bf1c69d84659828bd7b7b4864c22
            - button "Actions for Synthetic handoff history 28" [ref=e109] [cursor=pointer]
          - generic [ref=e111]:
            - link "Synthetic handoff history 27" [ref=e112] [cursor=pointer]:
              - /url: /c/9c61137a75fb40f39041bf3c173192c4
            - button "Actions for Synthetic handoff history 27" [ref=e113] [cursor=pointer]
          - generic [ref=e115]:
            - link "Synthetic handoff history 26" [ref=e116] [cursor=pointer]:
              - /url: /c/2592523931064380ac9fdfefc925bcb0
            - button "Actions for Synthetic handoff history 26" [ref=e117] [cursor=pointer]
          - generic [ref=e119]:
            - link "Synthetic handoff history 25" [ref=e120] [cursor=pointer]:
              - /url: /c/a15d92a7960c4b71acd99b53bf7d9b51
            - button "Actions for Synthetic handoff history 25" [ref=e121] [cursor=pointer]
          - generic [ref=e123]:
            - link "Synthetic handoff history 24" [ref=e124] [cursor=pointer]:
              - /url: /c/99db077cb30744b28471c8bcbee74552
            - button "Actions for Synthetic handoff history 24" [ref=e125] [cursor=pointer]
          - generic [ref=e127]:
            - link "Synthetic handoff history 23" [ref=e128] [cursor=pointer]:
              - /url: /c/a014fd8736fa44528f4c289ff7d87346
            - button "Actions for Synthetic handoff history 23" [ref=e129] [cursor=pointer]
          - generic [ref=e131]:
            - link "Synthetic handoff history 22" [ref=e132] [cursor=pointer]:
              - /url: /c/b3275d241c6e450a95f770b4dcae3b3b
            - button "Actions for Synthetic handoff history 22" [ref=e133] [cursor=pointer]
          - generic [ref=e135]:
            - link "Synthetic handoff history 21" [ref=e136] [cursor=pointer]:
              - /url: /c/2a2c06f85a454144985a290d6bb8f83c
            - button "Actions for Synthetic handoff history 21" [ref=e137] [cursor=pointer]
          - generic [ref=e139]:
            - link "Synthetic handoff history 20" [ref=e140] [cursor=pointer]:
              - /url: /c/9c7c0cc2d7f4403a9c9cbe48b48fd28a
            - button "Actions for Synthetic handoff history 20" [ref=e141] [cursor=pointer]
          - generic [ref=e143]:
            - link "Synthetic handoff history 19" [ref=e144] [cursor=pointer]:
              - /url: /c/3005d9c09c8e4195b756db4066303d56
            - button "Actions for Synthetic handoff history 19" [ref=e145] [cursor=pointer]
          - generic [ref=e147]:
            - link "Synthetic handoff history 18" [ref=e148] [cursor=pointer]:
              - /url: /c/768721f9d3f14a6f93d77cd3e7b3b06c
            - button "Actions for Synthetic handoff history 18" [ref=e149] [cursor=pointer]
          - generic [ref=e151]:
            - link "Synthetic handoff history 17" [ref=e152] [cursor=pointer]:
              - /url: /c/7550cf765d9a4beb8f87f779e0ae6bc8
            - button "Actions for Synthetic handoff history 17" [ref=e153] [cursor=pointer]
          - generic [ref=e155]:
            - link "Synthetic handoff history 16" [ref=e156] [cursor=pointer]:
              - /url: /c/52a1c73f304d4b89a31a2cbc9f984e98
            - button "Actions for Synthetic handoff history 16" [ref=e157] [cursor=pointer]
          - generic [ref=e159]:
            - link "Synthetic handoff history 15" [ref=e160] [cursor=pointer]:
              - /url: /c/5da15d38b96348a3982ef036a45d9abb
            - button "Actions for Synthetic handoff history 15" [ref=e161] [cursor=pointer]
          - generic [ref=e163]:
            - link "Synthetic handoff history 14" [ref=e164] [cursor=pointer]:
              - /url: /c/8c4cc793453f47a1b633741d5dc7030e
            - button "Actions for Synthetic handoff history 14" [ref=e165] [cursor=pointer]
          - generic [ref=e167]:
            - link "Synthetic handoff history 13" [ref=e168] [cursor=pointer]:
              - /url: /c/5594a94599744e4c83155499e11736bf
            - button "Actions for Synthetic handoff history 13" [ref=e169] [cursor=pointer]
          - generic [ref=e171]:
            - link "Synthetic handoff history 12" [ref=e172] [cursor=pointer]:
              - /url: /c/cbbedea8958b4deeb50a0c3fae43ed1d
            - button "Actions for Synthetic handoff history 12" [ref=e173] [cursor=pointer]
          - generic [ref=e175]:
            - link "Synthetic handoff history 11" [ref=e176] [cursor=pointer]:
              - /url: /c/25c92b68d4fd48b4abba91ffb9accd8b
            - button "Actions for Synthetic handoff history 11" [ref=e177] [cursor=pointer]
          - generic [ref=e179]:
            - link "Synthetic handoff history 10" [ref=e180] [cursor=pointer]:
              - /url: /c/56d8cff436fd4d629d0ae641439bcc05
            - button "Actions for Synthetic handoff history 10" [ref=e181] [cursor=pointer]
          - generic [ref=e183]:
            - link "Synthetic handoff history 9" [ref=e184] [cursor=pointer]:
              - /url: /c/71e0f382ff144e0692178ae2e21e37c2
            - button "Actions for Synthetic handoff history 9" [ref=e185] [cursor=pointer]
          - generic [ref=e187]:
            - link "Synthetic handoff history 8" [ref=e188] [cursor=pointer]:
              - /url: /c/1134fe6234864622bd19c228300771b8
            - button "Actions for Synthetic handoff history 8" [ref=e189] [cursor=pointer]
          - generic [ref=e191]:
            - link "Synthetic handoff history 7" [ref=e192] [cursor=pointer]:
              - /url: /c/34bf7ea9e24940a29d049e52fd42ac22
            - button "Actions for Synthetic handoff history 7" [ref=e193] [cursor=pointer]
          - generic [ref=e195]:
            - link "Synthetic handoff history 6" [ref=e196] [cursor=pointer]:
              - /url: /c/c21200f1a05f40aa87c3e6a802076d4f
            - button "Actions for Synthetic handoff history 6" [ref=e197] [cursor=pointer]
          - generic [ref=e199]:
            - link "Synthetic handoff history 5" [ref=e200] [cursor=pointer]:
              - /url: /c/089f0f7e8f1e49fd927dc28b2412fed9
            - button "Actions for Synthetic handoff history 5" [ref=e201] [cursor=pointer]
          - generic [ref=e203]:
            - link "Synthetic handoff history 4" [ref=e204] [cursor=pointer]:
              - /url: /c/8c56d3f299224c6b8efebdad616ecca2
            - button "Actions for Synthetic handoff history 4" [ref=e205] [cursor=pointer]
          - generic [ref=e207]:
            - link "Synthetic handoff history 3" [ref=e208] [cursor=pointer]:
              - /url: /c/8b87da7611764637b0d3a8bf53d0211e
            - button "Actions for Synthetic handoff history 3" [ref=e209] [cursor=pointer]
          - generic [ref=e211]:
            - link "Synthetic handoff history 2" [ref=e212] [cursor=pointer]:
              - /url: /c/dd72d61437214ed98a849459c9c427fe
            - button "Actions for Synthetic handoff history 2" [ref=e213] [cursor=pointer]
          - generic [ref=e215]:
            - link "Synthetic handoff history 1" [ref=e216] [cursor=pointer]:
              - /url: /c/eb83d5fde653421295b7240abc2ebc05
            - button "Actions for Synthetic handoff history 1" [ref=e217] [cursor=pointer]
          - generic [ref=e219]:
            - link "Synthetic handoff history 0" [ref=e220] [cursor=pointer]:
              - /url: /c/af6705aaa6ec4df6963fbbabe07cfb42
            - button "Actions for Synthetic handoff history 0" [ref=e221] [cursor=pointer]
          - generic [ref=e223]:
            - link "Synthetic rendering fixture" [ref=e224] [cursor=pointer]:
              - /url: /c/44efa2f25c734712a380ccfdc21f4aaf
            - button "Actions for Synthetic rendering fixture" [ref=e225] [cursor=pointer]
          - generic [ref=e227]:
            - link "Synthetic rendering fixture" [ref=e228] [cursor=pointer]:
              - /url: /c/6498352642014c3fafdb1998bf542664
            - button "Actions for Synthetic rendering fixture" [ref=e229] [cursor=pointer]
          - generic [ref=e231]:
            - link "Invented document question" [ref=e232] [cursor=pointer]:
              - /url: /c/dfe235c85b444058bc1ba0b774a93779
            - button "Actions for Invented document question" [ref=e233] [cursor=pointer]
          - paragraph [ref=e235]: Loading more chats…
        - button "Settings" [ref=e237] [cursor=pointer]
    - main [ref=e238]:
      - generic [ref=e239]:
        - button "Choose model" [ref=e241] [cursor=pointer]:
          - generic [aria-hidden] [ref=e242]: ●
          - generic [ref=e243]: fake-vision
          - generic [ref=e244]: Fake runtime
        - button "Chat controls" [ref=e245] [cursor=pointer]
      - generic [ref=e246]:
        - heading "Good morning" [level=1] [ref=e247]
        - form "Message" [ref=e248]:
          - textbox "Image prompt" [active] [ref=e249]:
            - /placeholder: Describe an image…
          - generic [ref=e250]:
            - button "Leave image mode" [pressed] [ref=e251] [cursor=pointer]: Image
            - button "Image count" [ref=e252] [cursor=pointer]: 1 image
            - button "Image options" [ref=e253] [cursor=pointer]
            - generic [ref=e254]:
              - generic [ref=e255]: FLUX.2 klein 4B · 1024²
              - generic [ref=e256]:
                - button "Create image" [disabled]
        - paragraph [ref=e257]: Your models. Your Mac.
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
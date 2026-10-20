# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: cleanup.spec.ts >> 6A clean progress rejected section versions download context discard 1440
- Location: tests/cleanup.spec.ts:3:3

# Error details

```
Error: locator.setInputFiles: Error: strict mode violation: locator('input[type="file"]') resolved to 2 elements:
    1) <input hidden="" type="file" aria-label="Choose photo to edit" accept="image/png,image/jpeg,image/heic,image/heif,.png,.jpg,.jpeg,.heic,.heif"/> aka getByLabel('Choose photo to edit')
    2) <input multiple type="file" aria-label="Attach files" class="composer-file-input" accept="image/*,.heic,.heif,.docx,.pdf,.c,.cpp,.css,.csv,.go,.h,.html,.ini,.java,.js,.json,.jsx,.kt,.log,.md,.py,.rb,.rs,.sh,.sql,.srt,.swift,.tex,.toml,.ts,.tsx,.txt,.vtt,.xml,.yaml,.yml"/> aka getByTitle('Attach files · ⌘U').locator('input[type="file"]')

Call log:
  - waiting for locator('input[type="file"]')

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
            - link "Images" [ref=e21] [cursor=pointer]:
              - /url: /images
          - region "Folders" [ref=e27]:
            - generic [ref=e28]:
              - heading "Folders" [level=2] [ref=e29]
              - button "New folder" [ref=e30] [cursor=pointer]
            - paragraph [ref=e31]: No folders yet
          - generic [ref=e32]:
            - paragraph [ref=e33]: Today
            - generic [ref=e34]:
              - link "model-default-payload-check" [ref=e35] [cursor=pointer]:
                - /url: /c/bfdba8ede363419a8b616c93d3361c36
              - button "Actions for model-default-payload-check" [ref=e36] [cursor=pointer]
          - generic [ref=e38]:
            - link "first-token-latency-check" [ref=e39] [cursor=pointer]:
              - /url: /c/3ca9872cce3946298439442eb7782f95
            - button "Actions for first-token-latency-check" [ref=e40] [cursor=pointer]
          - generic [ref=e42]:
            - 'link "#long:300 #slow:100" [ref=e43] [cursor=pointer]':
              - /url: /c/49f2d47fdb794b189c61af37795861db
            - 'button "Actions for #long:300 #slow:100" [ref=e44] [cursor=pointer]'
          - generic [ref=e46]:
            - link "#stall:70" [ref=e47] [cursor=pointer]:
              - /url: /c/091ae0784e79423ba95a278e2bffaec7
            - 'button "Actions for #stall:70" [ref=e48] [cursor=pointer]'
          - generic [ref=e50]:
            - 'link "#long:1500 #slow:10" [ref=e51] [cursor=pointer]':
              - /url: /c/4164bf084d6446c0bd85d1ec7076cd7e
            - 'button "Actions for #long:1500 #slow:10" [ref=e52] [cursor=pointer]'
          - generic [ref=e54]:
            - 'link "#long:350 #slow:10" [ref=e55] [cursor=pointer]':
              - /url: /c/61c920ab080e484e8772c6a404d55afe
            - 'button "Actions for #long:350 #slow:10" [ref=e56] [cursor=pointer]'
          - generic [ref=e58]:
            - 'link "#long:500 #slow:50" [ref=e59] [cursor=pointer]':
              - /url: /c/b47f3da218df44e980c4acb2e0fd917f
            - 'button "Actions for #long:500 #slow:50" [ref=e60] [cursor=pointer]'
          - generic [ref=e62]:
            - link "Hello from the browser" [ref=e63] [cursor=pointer]:
              - /url: /c/d657f315bb8440619db89dbace89d9e5
            - button "Actions for Hello from the browser" [ref=e64] [cursor=pointer]
          - generic [ref=e66]:
            - link "Hello from the browser" [ref=e67] [cursor=pointer]:
              - /url: /c/394937ed9bc0419794cc64df945c96d3
            - button "Actions for Hello from the browser" [ref=e68] [cursor=pointer]
          - generic [ref=e70]:
            - link "Hello from the browser" [ref=e71] [cursor=pointer]:
              - /url: /c/58c2602ee09841a4801c2de2f29e5bc5
            - button "Actions for Hello from the browser" [ref=e72] [cursor=pointer]
          - generic [ref=e74]:
            - link "Hello from the browser" [ref=e75] [cursor=pointer]:
              - /url: /c/af589969e9af4c49831499c1482eebeb
            - button "Actions for Hello from the browser" [ref=e76] [cursor=pointer]
          - generic [ref=e78]:
            - link "Hello from the browser" [ref=e79] [cursor=pointer]:
              - /url: /c/17ee259181e6484fb658ebc6761c8410
            - button "Actions for Hello from the browser" [ref=e80] [cursor=pointer]
          - generic [ref=e82]:
            - link "Hello from the browser" [ref=e83] [cursor=pointer]:
              - /url: /c/8391c6047e0c4ec7bb4a2e79a20a1378
            - button "Actions for Hello from the browser" [ref=e84] [cursor=pointer]
          - generic [ref=e86]:
            - link "Hello from the browser" [ref=e87] [cursor=pointer]:
              - /url: /c/a8866105c8a040d5b91c70530ceb912e
            - button "Actions for Hello from the browser" [ref=e88] [cursor=pointer]
          - generic [ref=e90]:
            - link "Hello from the browser" [ref=e91] [cursor=pointer]:
              - /url: /c/bfa43c817c684da99aded5fe003cee8a
            - button "Actions for Hello from the browser" [ref=e92] [cursor=pointer]
        - button "Settings" [ref=e95] [cursor=pointer]
    - main [ref=e96]:
      - generic [ref=e97]:
        - button "Choose model" [ref=e99] [cursor=pointer]:
          - generic [aria-hidden] [ref=e100]: ●
          - generic [ref=e101]: fake-chat
          - generic [ref=e102]: Fake runtime
        - button "Chat controls" [ref=e103] [cursor=pointer]
      - generic [ref=e104]:
        - heading "Good morning" [level=1] [ref=e105]
        - form "Message" [ref=e106]:
          - textbox "Message fake-chat" [ref=e107]:
            - /placeholder: Message fake-chat…
          - generic [ref=e108]:
            - generic "Attach files · ⌘U" [ref=e109]:
              - button "Attach files" [ref=e110] [cursor=pointer]
            - button "Tools" [ref=e111] [cursor=pointer]
            - generic [ref=e113]:
              - img "0 of 16,384 total tokens; 12,032 input allowance; 4,096 reserved for response; 256 safety margin" [ref=e114]
              - generic [ref=e118]:
                - button "Send message" [disabled]
        - generic [ref=e119]:
          - button "Explain" [ref=e120] [cursor=pointer]
          - button "Write" [ref=e121] [cursor=pointer]
          - button "Code" [ref=e122] [cursor=pointer]
          - button "Search the web" [ref=e123] [cursor=pointer]
        - paragraph [ref=e124]: Your models. Your Mac.
  - region "Notifications alt+T"
```

# Test source

```ts
  1   | import { test, expect } from "@playwright/test";
  2   | for (const width of [390, 1440]) {
  3   |   test(`6A clean progress rejected section versions download context discard ${width}`, async ({
  4   |     page,
  5   |     request,
  6   |   }) => {
  7   |     await page.setViewportSize({ width, height: 900 });
  8   |     const connections = await (await request.get("/api/connections")).json();
  9   |     for (const item of await (
  10  |       await request.get("/api/attachments/pending")
  11  |     ).json())
  12  |       await request.delete(`/api/attachments/${item.id}`);
  13  |     await request.patch("/api/settings", {
  14  |       data: {
  15  |         default_connection_id: connections[0].id,
  16  |         default_model_id: "fake-chat",
  17  |         auto_title: false,
  18  |         "transcription.keep_audio": false,
  19  |       },
  20  |     });
  21  |     await request.put("/api/transcription/glossary", { data: { text: "" } });
  22  |     await page.goto("/");
> 23  |     await page.locator('input[type="file"]').setInputFiles({
      |     ^ Error: locator.setInputFiles: Error: strict mode violation: locator('input[type="file"]') resolved to 2 elements:
  24  |       name: "Invented cleanup recording.wav",
  25  |       mimeType: "audio/wav",
  26  |       buffer: Buffer.from("#fake:cleanup"),
  27  |     });
  28  |     const chip = page.getByTestId("audio-chip");
  29  |     await expect(chip).toContainText("Transcript saved · audio removed");
  30  |     const pending = await (
  31  |       await request.get("/api/attachments/pending")
  32  |     ).json();
  33  |     const id = pending[0].id;
  34  |     const before = await (
  35  |       await request.get(`/api/attachments/${id}/transcript`)
  36  |     ).json();
  37  |     await chip
  38  |       .getByRole("button", {
  39  |         name: "Open transcript for Invented cleanup recording.wav",
  40  |       })
  41  |       .click();
  42  |     await page
  43  |       .getByRole("button", { name: "Clean up with fake-chat", exact: true })
  44  |       .click();
  45  |     await expect(
  46  |       page.getByRole("button", { name: "Cancel clean-up", exact: true }),
  47  |     ).toBeVisible();
  48  |     await expect(chip).toContainText("Cleaning up…");
  49  |     await expect(
  50  |       page.getByRole("button", { name: "Cleaned", exact: true }),
  51  |     ).toBeVisible({ timeout: 20000 });
  52  |     await expect(
  53  |       page.getByText(/sections were left as transcribed/),
  54  |     ).toBeVisible();
  55  |     await expect(
  56  |       page.getByRole("button", { name: "Cleaned", exact: true }),
  57  |     ).toHaveAttribute("aria-pressed", "true");
  58  |     await page
  59  |       .getByRole("button", { name: "As transcribed", exact: true })
  60  |       .click();
  61  |     await expect(
  62  |       page.getByRole("button", { name: "As transcribed", exact: true }),
  63  |     ).toHaveAttribute("aria-pressed", "true");
  64  |     await page
  65  |       .getByRole("button", { name: "Raw Whisper", exact: true })
  66  |       .click();
  67  |     await page.getByRole("button", { name: "Timestamps", exact: true }).click();
  68  |     await expect(
  69  |       page.getByText("Timestamps use the original transcript."),
  70  |     ).toBeVisible();
  71  |     const value = await (
  72  |       await request.get(`/api/attachments/${id}/transcript`)
  73  |     ).json();
  74  |     expect(value.text).toBe(before.text);
  75  |     expect(value.raw_text).toBe(before.raw_text);
  76  |     expect(value.segments).toEqual(before.segments);
  77  |     expect(value.cleaned_text).toContain("FAKE-REWRITE");
  78  |     const txt = await request.get(
  79  |       `/api/attachments/${id}/transcript/download?format=txt&variant=best`,
  80  |     );
  81  |     expect(await txt.text()).toBe(value.cleaned_text);
  82  |     await page.getByRole("button", { name: "Close transcript" }).click();
  83  |     await page
  84  |       .locator(".composer textarea")
  85  |       .fill("Summarize the invented recording.");
  86  |     await page
  87  |       .getByRole("button", { name: "Send message", exact: true })
  88  |       .click();
  89  |     await expect(page).toHaveURL(/\/c\//);
  90  |     await expect(
  91  |       page.getByRole("article", { name: "assistant message" }),
  92  |     ).toContainText("Fake runtime reply.");
  93  |     const runtime = await (
  94  |       await request.get("http://127.0.0.1:18080/tests/state")
  95  |     ).json();
  96  |     const capture = runtime.captures
  97  |       .filter((b: { messages?: { content: string }[] }) =>
  98  |         b.messages?.some((m) => m.content.includes("<transcript ")),
  99  |       )
  100 |       .at(-1);
  101 |     expect(capture.messages.at(-1).content).toContain(value.cleaned_text);
  102 |     await page
  103 |       .getByRole("button", {
  104 |         name: "Open transcript for Invented cleanup recording.wav",
  105 |       })
  106 |       .click();
  107 |     await page
  108 |       .getByRole("button", { name: "Discard clean-up", exact: true })
  109 |       .click();
  110 |     await expect(
  111 |       page.getByRole("button", { name: "Cleaned", exact: true }),
  112 |     ).toHaveCount(0);
  113 |     await page.getByRole("button", { name: "Close transcript" }).click();
  114 |     const chatId = page.url().split("/c/")[1];
  115 |     await request.delete(`/api/chats/${chatId}`);
  116 |   });
  117 |   test(`6A glossary edit validation saved state and next transcription ${width}`, async ({
  118 |     page,
  119 |     request,
  120 |   }) => {
  121 |     await page.setViewportSize({ width, height: 900 });
  122 |     const old = await (await request.get("/api/transcription/glossary")).json();
  123 |     try {
```
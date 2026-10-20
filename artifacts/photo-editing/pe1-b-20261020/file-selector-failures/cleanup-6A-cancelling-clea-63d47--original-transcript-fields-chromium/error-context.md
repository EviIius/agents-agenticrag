# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: cleanup.spec.ts >> 6A cancelling clean-up preserves all original transcript fields
- Location: tests/cleanup.spec.ts:201:1

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
  118 |     page,
  119 |     request,
  120 |   }) => {
  121 |     await page.setViewportSize({ width, height: 900 });
  122 |     const old = await (await request.get("/api/transcription/glossary")).json();
  123 |     try {
  124 |       await page.goto("/");
  125 |       if (width < 640)
  126 |         await page
  127 |           .getByRole("button", { name: "Open sidebar", exact: true })
  128 |           .click();
  129 |       await page.getByRole("button", { name: "Settings", exact: true }).click();
  130 |       await page
  131 |         .getByRole("button", { name: "Transcription", exact: true })
  132 |         .click();
  133 |       const box = page.getByRole("textbox", {
  134 |         name: "Terms for transcription",
  135 |       });
  136 |       await expect(box).toBeVisible();
  137 |       await box.fill("Invented Aurora = invented aurora\nInvented Grove");
  138 |       await page
  139 |         .getByRole("button", { name: "Save glossary", exact: true })
  140 |         .click();
  141 |       await expect(
  142 |         page.getByText("Glossary saved", { exact: true }),
  143 |       ).toBeVisible();
  144 |       await expect(
  145 |         page.getByText("2 saved terms", { exact: true }),
  146 |       ).toBeVisible();
  147 |       const stored = await (
  148 |         await request.get("/api/transcription/glossary")
  149 |       ).json();
  150 |       expect(stored.terms).toEqual(["Invented Aurora", "Invented Grove"]);
  151 |       const uploaded = await request.post("/api/attachments", {
  152 |         multipart: {
  153 |           file: {
  154 |             name: "Invented glossary recording.wav",
  155 |             mimeType: "audio/wav",
  156 |             buffer: Buffer.from("fake"),
  157 |           },
  158 |         },
  159 |       });
  160 |       expect(uploaded.status()).toBe(201);
  161 |       const added = await uploaded.json();
  162 |       await expect
  163 |         .poll(async () =>
  164 |           (
  165 |             await request.get(`/api/attachments/${added.id}/transcript`)
  166 |           ).status(),
  167 |         )
  168 |         .toBe(200);
  169 |       const output = await (
  170 |         await request.get(
  171 |           `/api/attachments/${added.id}/transcript/download?format=json`,
  172 |         )
  173 |       ).json();
  174 |       expect(output.engine.prompt).toContain("Invented Aurora");
  175 |       await request.delete(`/api/attachments/${added.id}`);
  176 | 
  177 |       await box.fill("x".repeat(65537));
  178 |       await expect(
  179 |         page.getByRole("button", { name: "Save glossary", exact: true }),
  180 |       ).toBeDisabled();
  181 |       await expect(
  182 |         page.getByText(
  183 |           "Glossary can be up to 64 KB and cannot contain NUL bytes.",
  184 |           { exact: true },
  185 |         ),
  186 |       ).toBeVisible();
  187 |       const bad = await request.put("/api/transcription/glossary", {
  188 |         data: { text: "bad\u0000term" },
  189 |       });
  190 |       expect(bad.status()).toBe(422);
  191 |       expect(
  192 |         (await (await request.get("/api/transcription/glossary")).json()).text,
  193 |       ).toBe(stored.text);
  194 |     } finally {
  195 |       await request.put("/api/transcription/glossary", {
  196 |         data: { text: old.text },
  197 |       });
  198 |     }
  199 |   });
  200 | }
  201 | test("6A cancelling clean-up preserves all original transcript fields", async ({
  202 |   page,
  203 |   request,
  204 | }) => {
  205 |   const connections = await (await request.get("/api/connections")).json();
  206 |   for (const item of await (
  207 |     await request.get("/api/attachments/pending")
  208 |   ).json())
  209 |     await request.delete(`/api/attachments/${item.id}`);
  210 |   await request.patch("/api/settings", {
  211 |     data: {
  212 |       default_connection_id: connections[0].id,
  213 |       default_model_id: "fake-chat",
  214 |       auto_title: false,
  215 |     },
  216 |   });
  217 |   await page.goto("/");
> 218 |   await page.locator('input[type="file"]').setInputFiles({
      |   ^ Error: locator.setInputFiles: Error: strict mode violation: locator('input[type="file"]') resolved to 2 elements:
  219 |     name: "Invented cancellation.wav",
  220 |     mimeType: "audio/wav",
  221 |     buffer: Buffer.from("#fake:cleanup-slow"),
  222 |   });
  223 |   const chip = page.getByTestId("audio-chip");
  224 |   await expect(chip).toContainText("words");
  225 |   const id = (await (await request.get("/api/attachments/pending")).json())[0]
  226 |     .id;
  227 |   const before = await (
  228 |     await request.get(`/api/attachments/${id}/transcript`)
  229 |   ).json();
  230 |   await chip
  231 |     .getByRole("button", {
  232 |       name: "Open transcript for Invented cancellation.wav",
  233 |     })
  234 |     .click();
  235 |   await page
  236 |     .getByRole("button", { name: "Clean up with fake-chat", exact: true })
  237 |     .click();
  238 |   await page
  239 |     .getByRole("button", { name: "Cancel clean-up", exact: true })
  240 |     .click();
  241 |   await expect(
  242 |     page.getByText("Clean-up cancelled. The transcript is unchanged.", {
  243 |       exact: true,
  244 |     }),
  245 |   ).toBeVisible();
  246 |   const after = await (
  247 |     await request.get(`/api/attachments/${id}/transcript`)
  248 |   ).json();
  249 |   expect(after.text).toBe(before.text);
  250 |   expect(after.raw_text).toBe(before.raw_text);
  251 |   expect(after.segments).toEqual(before.segments);
  252 |   expect(after.cleaned_text).toBeNull();
  253 |   await request.delete(`/api/attachments/${id}`);
  254 | });
  255 | 
```
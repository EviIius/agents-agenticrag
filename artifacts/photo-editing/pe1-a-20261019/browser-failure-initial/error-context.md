# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: attachments-thread.spec.ts >> an accepted earlier send preserves a newer paste and undo remains available during streaming
- Location: tests/attachments-thread.spec.ts:270:1

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: locator.click: Test timeout of 45000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'Send message', exact: true })
    - locator resolved to <button type="submit" data-size="icon" data-slot="button" data-variant="default" aria-label="Send message" class="inline-flex shrink-0 items-center justify-center gap-2 text-sm font-medium whitespace-nowrap outline-none disabled:pointer-events-none aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4 hover:bg-primary/90 size-11 rounded-full disabled:bg-surface-3 disabled:…>…</button>
  - attempting click action
    - waiting for element to be visible, enabled and stable
    - element is not stable
  - retrying click action
    - waiting for element to be visible, enabled and stable
    - element is visible, enabled and stable
    - scrolling into view if needed
    - done scrolling
    - performing click action
    - <li tabindex="0" data-index="0" class="font-sans" data-front="true" data-styled="true" data-mounted="true" data-swiped="false" data-visible="true" data-sonner-toast="" data-promise="false" data-removed="false" data-swiping="false" data-expanded="false" data-swipe-out="false" data-x-position="right" data-dismissible="true" data-y-position="bottom">…</li> from <section tabindex="-1" aria-live="polite" aria-atomic="false" aria-relevant="additions text" aria-label="Notifications alt+T" data-react-aria-top-layer="true">…</section> subtree intercepts pointer events
  - retrying click action
    - waiting 20ms
    - waiting for element to be visible, enabled and stable
    - element is visible, enabled and stable
    - scrolling into view if needed
    - done scrolling
    - <li tabindex="0" data-index="0" class="font-sans" data-front="true" data-styled="true" data-mounted="true" data-swiped="false" data-visible="true" data-sonner-toast="" data-promise="false" data-removed="false" data-swiping="false" data-expanded="true" data-swipe-out="false" data-x-position="right" data-dismissible="true" data-y-position="bottom">…</li> from <section tabindex="-1" aria-live="polite" aria-atomic="false" aria-relevant="additions text" aria-label="Notifications alt+T" data-react-aria-top-layer="true">…</section> subtree intercepts pointer events
  2 × retrying click action
      - waiting 100ms
      - waiting for element to be visible, enabled and stable
      - element is visible, enabled and stable
      - scrolling into view if needed
      - done scrolling
      - <div class="" data-title="">Brief to images is waiting for you.</div> from <section tabindex="-1" aria-live="polite" aria-atomic="false" aria-relevant="additions text" aria-label="Notifications alt+T" data-react-aria-top-layer="true">…</section> subtree intercepts pointer events
  84 × retrying click action
       - waiting 500ms
       - waiting for element to be visible, enabled and stable
       - element is visible, enabled and stable
       - scrolling into view if needed
       - done scrolling
       - <div class="" data-title="">Brief to images is waiting for you.</div> from <section tabindex="-1" aria-live="polite" aria-atomic="false" aria-relevant="additions text" aria-label="Notifications alt+T" data-react-aria-top-layer="true">…</section> subtree intercepts pointer events
  - retrying click action
    - waiting 500ms

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
              - link "Who lost the 2021 NBA Finals? Show a table." [ref=e36] [cursor=pointer]:
                - /url: /c/147535b526dd4aa0844651710329916f
              - button "Actions for Who lost the 2021 NBA Finals? Show a table." [ref=e37] [cursor=pointer]
          - generic [ref=e39]:
            - link "Who lost the 2021 NBA Finals? Show a table." [ref=e40] [cursor=pointer]:
              - /url: /c/3e3baf429d964aabb803d79a754d0a85
            - button "Actions for Who lost the 2021 NBA Finals? Show a table." [ref=e41] [cursor=pointer]
          - generic [ref=e43]:
            - link "Who lost the 2021 NBA Finals? Show a table." [ref=e44] [cursor=pointer]:
              - /url: /c/ea11e5fcc40249e8a4ac88a2136dc6a2
            - button "Actions for Who lost the 2021 NBA Finals? Show a table." [ref=e45] [cursor=pointer]
          - generic [ref=e47]:
            - link "Who lost the 2021 NBA Finals? Show a table." [ref=e48] [cursor=pointer]:
              - /url: /c/e71e01b6dc954f7a88a04be8f00295f6
            - button "Actions for Who lost the 2021 NBA Finals? Show a table." [ref=e49] [cursor=pointer]
          - generic [ref=e51]:
            - link "Who lost the 2021 NBA Finals? Show a table." [ref=e52] [cursor=pointer]:
              - /url: /c/9f1831078eb842d29a7f35562162dd94
            - button "Actions for Who lost the 2021 NBA Finals? Show a table." [ref=e53] [cursor=pointer]
          - generic [ref=e55]:
            - link "Who lost the 2021 NBA Finals? Show a table." [ref=e56] [cursor=pointer]:
              - /url: /c/7e60573eaece4019ba3597ce39b5783c
            - button "Actions for Who lost the 2021 NBA Finals? Show a table." [ref=e57] [cursor=pointer]
          - generic [ref=e59]:
            - link "Synthetic budget request" [ref=e60] [cursor=pointer]:
              - /url: /c/c46cd57279dd497a9a0bbed9dd8b378d
            - button "Actions for Synthetic budget request" [ref=e61] [cursor=pointer]
          - generic [ref=e63]:
            - link "Summarize this recording." [ref=e64] [cursor=pointer]:
              - /url: /c/ff89f9d202dd4ad3942ee32c91f45358
            - button "Actions for Summarize this recording." [ref=e65] [cursor=pointer]
          - generic [ref=e67]:
            - link "#think Review this interface" [ref=e68] [cursor=pointer]:
              - /url: /c/6b12c28e6c514686871ed11836827c5e
            - 'button "Actions for #think Review this interface" [ref=e69] [cursor=pointer]'
          - generic [ref=e71]:
            - link "#think Review this interface" [ref=e72] [cursor=pointer]:
              - /url: /c/5a670c6d0f9c4c3aaefff4d970412e71
            - 'button "Actions for #think Review this interface" [ref=e73] [cursor=pointer]'
          - generic [ref=e75]:
            - link "#think Review this interface" [ref=e76] [cursor=pointer]:
              - /url: /c/ee7e0306cd694266a637e8666258d644
            - 'button "Actions for #think Review this interface" [ref=e77] [cursor=pointer]'
          - generic [ref=e79]:
            - link "#think Review this interface" [ref=e80] [cursor=pointer]:
              - /url: /c/7ddb9bfc7d1b4dcbae152434b8d53831
            - 'button "Actions for #think Review this interface" [ref=e81] [cursor=pointer]'
          - generic [ref=e83]:
            - link "Synthetic renamed checkpoint" [ref=e84] [cursor=pointer]:
              - /url: /c/a4962c8bc6364859ac3c20e89acc314d
            - button "Actions for Synthetic renamed checkpoint" [ref=e85] [cursor=pointer]
          - generic [ref=e87]:
            - link "Synthetic question after model switch" [ref=e88] [cursor=pointer]:
              - /url: /c/22ff1ecf42e649a2bdab0fd8250f6eac
            - button "Actions for Synthetic question after model switch" [ref=e89] [cursor=pointer]
          - generic [ref=e91]:
            - 'link "#think #long:100 #slow:1 #stall:120 Synthetic cancellation" [ref=e92] [cursor=pointer]':
              - /url: /c/855b1a15a2f34c4680826b88ad83f228
            - 'button "Actions for #think #long:100 #slow:1 #stall:120 Synthetic cancellation" [ref=e93] [cursor=pointer]'
          - generic [ref=e95]:
            - link "Synthetic preserved title" [ref=e96] [cursor=pointer]:
              - /url: /c/253e00ee65184913b167df8f65cac6d7
            - button "Actions for Synthetic preserved title" [ref=e97] [cursor=pointer]
          - generic [ref=e99]:
            - link "Synthetic server-default request" [ref=e100] [cursor=pointer]:
              - /url: /c/27358bed9a7f4fa5aced7808a54c2517
            - button "Actions for Synthetic server-default request" [ref=e101] [cursor=pointer]
          - generic [ref=e103]:
            - link "Synthetic explicit None" [ref=e104] [cursor=pointer]:
              - /url: /c/8297c60c6159430693f2cb262b642d57
            - button "Actions for Synthetic explicit None" [ref=e105] [cursor=pointer]
          - generic [ref=e107]:
            - link "Synthetic preset request 1440 chromium" [ref=e108] [cursor=pointer]:
              - /url: /c/1909c1f98d03449ea0bff2ea2766057c
            - button "Actions for Synthetic preset request 1440 chromium" [ref=e109] [cursor=pointer]
          - generic [ref=e111]:
            - link "Synthetic preset request 390 chromium" [ref=e112] [cursor=pointer]:
              - /url: /c/35216494d6bb47b6973497dcd713152c
            - button "Actions for Synthetic preset request 390 chromium" [ref=e113] [cursor=pointer]
          - generic [ref=e115]:
            - 'link "#long:100 #slow:10" [ref=e116] [cursor=pointer]':
              - /url: /c/160e02a1768e4091a36d979152eaf871
            - 'button "Actions for #long:100 #slow:10" [ref=e117] [cursor=pointer]'
          - generic [ref=e119]:
            - link "Who lost the 2021 NBA Finals? Show a table." [ref=e120] [cursor=pointer]:
              - /url: /c/dcaab2cbb2f640f199c96f8a222634a9
            - button "Actions for Who lost the 2021 NBA Finals? Show a table." [ref=e121] [cursor=pointer]
          - generic [ref=e123]:
            - 'link "#long:50 #slow:10" [ref=e124] [cursor=pointer]':
              - /url: /c/eb05e5c561904d39abdc944820aef507
            - 'button "Actions for #long:50 #slow:10" [ref=e125] [cursor=pointer]'
          - generic [ref=e127]:
            - link "Parameter payload 1440 chromium" [ref=e128] [cursor=pointer]:
              - /url: /c/b89d03bbd561441bb716a9d1b91fc930
            - button "Actions for Parameter payload 1440 chromium" [ref=e129] [cursor=pointer]
          - generic [ref=e131]:
            - link "Parameter payload 390 chromium" [ref=e132] [cursor=pointer]:
              - /url: /c/b84e899d4f284019864dca9bc362e07a
            - button "Actions for Parameter payload 390 chromium" [ref=e133] [cursor=pointer]
          - generic [ref=e135]:
            - link "Synthetic mobile request" [ref=e136] [cursor=pointer]:
              - /url: /c/8c956e7757f24c589032abc96a7d9dee
            - button "Actions for Synthetic mobile request" [ref=e137] [cursor=pointer]
          - generic [ref=e139]:
            - link "Context payload 1440 true chromium" [ref=e140] [cursor=pointer]:
              - /url: /c/317699f3881b4208b6213f8e14213e4d
            - button "Actions for Context payload 1440 true chromium" [ref=e141] [cursor=pointer]
          - generic [ref=e143]:
            - link "Context payload 1440 false chromium" [ref=e144] [cursor=pointer]:
              - /url: /c/cef28f2eca5f47dfa853709039118728
            - button "Actions for Context payload 1440 false chromium" [ref=e145] [cursor=pointer]
          - generic [ref=e147]:
            - link "Context payload 390 true chromium" [ref=e148] [cursor=pointer]:
              - /url: /c/8168d7fe2c4d44e6a3fdceb320a56970
            - button "Actions for Context payload 390 true chromium" [ref=e149] [cursor=pointer]
          - generic [ref=e151]:
            - link "Context payload 390 false chromium" [ref=e152] [cursor=pointer]:
              - /url: /c/0701995fca874a2d92cc5d752fdefd26
            - button "Actions for Context payload 390 false chromium" [ref=e153] [cursor=pointer]
          - generic [ref=e155]:
            - link "#lib Synthetic empty scope" [ref=e156] [cursor=pointer]:
              - /url: /c/f4d6149b67f647faa2fce2e886882580
            - 'button "Actions for #lib Synthetic empty scope" [ref=e157] [cursor=pointer]'
          - generic [ref=e159]:
            - link "#lib What does the invented handbook say?" [ref=e160] [cursor=pointer]:
              - /url: /c/08e7e82a097d43e5a6c8c2774c40997a
            - 'button "Actions for #lib What does the invented handbook say?" [ref=e161] [cursor=pointer]'
          - generic [ref=e163]:
            - link "#lib What does the invented handbook say?" [ref=e164] [cursor=pointer]:
              - /url: /c/5e5c07de10004e8a87ac6a052c56369b
            - 'button "Actions for #lib What does the invented handbook say?" [ref=e165] [cursor=pointer]'
          - generic [ref=e167]:
            - link "#lib What does the invented handbook say?" [ref=e168] [cursor=pointer]:
              - /url: /c/bbb621bb71ac4ba1a5e41b7d4a37f5be
            - 'button "Actions for #lib What does the invented handbook say?" [ref=e169] [cursor=pointer]'
          - generic [ref=e171]:
            - link "#lib What does the invented handbook say?" [ref=e172] [cursor=pointer]:
              - /url: /c/cb7c7799b6eb4977bb90ccbcc8342076
            - 'button "Actions for #lib What does the invented handbook say?" [ref=e173] [cursor=pointer]'
          - generic [ref=e175]:
            - 'link "Synthetic browser image #slow" [ref=e176] [cursor=pointer]':
              - /url: /c/1826aa57cf924ad5ac71bad926c31da7
            - 'button "Actions for Synthetic browser image #slow" [ref=e177] [cursor=pointer]'
          - generic [ref=e179]:
            - link "Synthetic mobile handoff request" [ref=e180] [cursor=pointer]:
              - /url: /c/e893aea484574964b21a6b2155989d79
            - button "Actions for Synthetic mobile handoff request" [ref=e181] [cursor=pointer]
          - generic [ref=e183]:
            - link "Who lost the 2021 NBA Finals? Show a table." [ref=e184] [cursor=pointer]:
              - /url: /c/2caed9ef186448d9800c7b6ea7b4b001
            - button "Actions for Who lost the 2021 NBA Finals? Show a table." [ref=e185] [cursor=pointer]
          - generic [ref=e187]:
            - link "Synthetic handoff history 44" [ref=e188] [cursor=pointer]:
              - /url: /c/c5a0c7c1a248457485fb9254e4b4363b
            - button "Actions for Synthetic handoff history 44" [ref=e189] [cursor=pointer]
          - generic [ref=e191]:
            - link "Synthetic handoff history 43" [ref=e192] [cursor=pointer]:
              - /url: /c/838d1a311ce944e49791498866fbf95e
            - button "Actions for Synthetic handoff history 43" [ref=e193] [cursor=pointer]
          - generic [ref=e195]:
            - link "Synthetic handoff history 42" [ref=e196] [cursor=pointer]:
              - /url: /c/07d721bfe89a4df78948f378bd0ce0ab
            - button "Actions for Synthetic handoff history 42" [ref=e197] [cursor=pointer]
          - generic [ref=e199]:
            - link "Synthetic handoff history 41" [ref=e200] [cursor=pointer]:
              - /url: /c/e9dd865b5edf4deb9e79504f07ba76ae
            - button "Actions for Synthetic handoff history 41" [ref=e201] [cursor=pointer]
          - generic [ref=e203]:
            - link "Synthetic handoff history 40" [ref=e204] [cursor=pointer]:
              - /url: /c/b4d67a39c086403fb8fa2810d99a29d8
            - button "Actions for Synthetic handoff history 40" [ref=e205] [cursor=pointer]
          - generic [ref=e207]:
            - link "Synthetic handoff history 39" [ref=e208] [cursor=pointer]:
              - /url: /c/793f2be78f214f9ba67068a293f9475f
            - button "Actions for Synthetic handoff history 39" [ref=e209] [cursor=pointer]
          - generic [ref=e211]:
            - link "Synthetic handoff history 38" [ref=e212] [cursor=pointer]:
              - /url: /c/4c1c0ac6ae644c8992c6df0fcb96bf10
            - button "Actions for Synthetic handoff history 38" [ref=e213] [cursor=pointer]
          - generic [ref=e215]:
            - link "Synthetic handoff history 37" [ref=e216] [cursor=pointer]:
              - /url: /c/dba4413a57274a3995016a1a674d4c99
            - button "Actions for Synthetic handoff history 37" [ref=e217] [cursor=pointer]
          - generic [ref=e219]:
            - link "Synthetic handoff history 36" [ref=e220] [cursor=pointer]:
              - /url: /c/fa3cf6a5f79c4aa98ab63e8ce82a81f3
            - button "Actions for Synthetic handoff history 36" [ref=e221] [cursor=pointer]
          - generic [ref=e223]:
            - link "Synthetic handoff history 35" [ref=e224] [cursor=pointer]:
              - /url: /c/9b9119de9e1643449fed237a12d942b4
            - button "Actions for Synthetic handoff history 35" [ref=e225] [cursor=pointer]
          - generic [ref=e227]:
            - link "Synthetic handoff history 34" [ref=e228] [cursor=pointer]:
              - /url: /c/cacbb38b833e4ccea925a1e32cb501cb
            - button "Actions for Synthetic handoff history 34" [ref=e229] [cursor=pointer]
          - generic [ref=e231]:
            - link "Synthetic handoff history 33" [ref=e232] [cursor=pointer]:
              - /url: /c/c81a28e29fdb472884af15a03857b690
            - button "Actions for Synthetic handoff history 33" [ref=e233] [cursor=pointer]
          - paragraph [ref=e235]: Loading more chats…
        - button "Settings" [ref=e237] [cursor=pointer]
    - main [ref=e238]:
      - generic [ref=e239]:
        - button "Choose model" [ref=e241] [cursor=pointer]:
          - generic [aria-hidden] [ref=e242]: ●
          - generic [ref=e243]: fake-vision
          - generic [ref=e244]: Fake runtime
        - generic "Double-click to rename" [ref=e245]: New chat
        - button "Chat controls" [ref=e246] [cursor=pointer]
        - button "Actions for New chat" [ref=e247] [cursor=pointer]
      - status [ref=e248]
      - log "Conversation" [ref=e249]
      - generic [ref=e251]:
        - button [aria-hidden] [ref=e252] [cursor=pointer]
        - form "Message" [ref=e253]:
          - textbox "Message fake-vision" [active] [ref=e254]:
            - /placeholder: Message fake-vision…
            - text: "#long:600 #slow:50 Synthetic fake earlier send."
          - generic [ref=e255]:
            - generic "Attach files · ⌘U" [ref=e256]:
              - button "Attach files" [ref=e257] [cursor=pointer]
            - button "Tools" [ref=e258] [cursor=pointer]
            - generic [ref=e260]:
              - img "28 of 32,768 total tokens; 24,320 input allowance; 8,192 reserved for response; 256 safety margin" [ref=e261]
              - button "Send message" [ref=e266] [cursor=pointer]
  - region "Notifications alt+T":
    - list:
      - listitem [ref=e268]:
        - button "Close toast" [ref=e269] [cursor=pointer]
        - generic [ref=e273]: Brief to images is waiting for you.
        - button "Open" [ref=e275] [cursor=pointer]
```

# Test source

```ts
  187 |     }),
  188 |   ).toBeVisible();
  189 |   await expect(page.locator(".attachment-meta")).toContainText(
  190 |     `${raw.length.toLocaleString()} characters`,
  191 |   );
  192 |   await field.fill("New typing: ");
  193 |   const removed = page.waitForResponse(
  194 |     (r) =>
  195 |       r.url().endsWith(`/api/attachments/${file.id}`) &&
  196 |       r.request().method() === "DELETE",
  197 |   );
  198 |   await page.getByRole("button", { name: "Keep as text", exact: true }).click();
  199 |   expect((await removed).ok()).toBe(true);
  200 |   await expect(field).toHaveValue("New typing: " + raw);
  201 |   await expect(field).toBeFocused();
  202 |   await expect(
  203 |     page.getByRole("button", {
  204 |       name: "Review file Pasted text 1.txt",
  205 |       exact: true,
  206 |     }),
  207 |   ).toHaveCount(0);
  208 |   expect(
  209 |     await (await request.get(`/api/attachments/${file.id}/info`)).status(),
  210 |   ).toBe(404);
  211 | });
  212 | test("long-paste undo cancels an in-flight upload, restores the selection and expires after ten seconds", async ({
  213 |   page,
  214 |   request,
  215 | }) => {
  216 |   await page.clock.install();
  217 |   await setup(page, request);
  218 |   let release!: () => void;
  219 |   const gate = new Promise<void>((resolve) => {
  220 |     release = resolve;
  221 |   });
  222 |   await page.route("**/api/attachments", async (route) => {
  223 |     if (route.request().method() !== "POST") return route.continue();
  224 |     await gate;
  225 |     await route.continue().catch(() => undefined);
  226 |   });
  227 |   const field = page.locator(".composer textarea");
  228 |   await field.fill("Before selected after");
  229 |   await field.evaluate((el) => {
  230 |     el.focus();
  231 |     (el as HTMLTextAreaElement).setSelectionRange(7, 15);
  232 |   });
  233 |   const raw = "Synthetic fake text. ".repeat(250);
  234 |   await clipboard(page, raw);
  235 |   await expect(
  236 |     page.getByRole("button", {
  237 |       name: "Cancel upload Pasted text 1.txt",
  238 |       exact: true,
  239 |     }),
  240 |   ).toBeVisible();
  241 |   await page.getByRole("button", { name: "Keep as text", exact: true }).click();
  242 |   await expect(field).toHaveValue("Before " + raw + " after");
  243 |   await expect(
  244 |     page.getByRole("button", {
  245 |       name: "Cancel upload Pasted text 1.txt",
  246 |       exact: true,
  247 |     }),
  248 |   ).toHaveCount(0);
  249 |   release();
  250 |   await page.unroute("**/api/attachments");
  251 |   await field.fill("Review synthetic fake text.");
  252 |   await clipboard(page, raw);
  253 |   await expect(
  254 |     page.getByRole("button", {
  255 |       name: "Review file Pasted text 2.txt",
  256 |       exact: true,
  257 |     }),
  258 |   ).toBeVisible();
  259 |   await page.clock.runFor(10500);
  260 |   await expect(
  261 |     page.getByRole("button", { name: "Keep as text", exact: true }),
  262 |   ).toHaveCount(0);
  263 |   await expect(
  264 |     page.getByRole("button", {
  265 |       name: "Review file Pasted text 2.txt",
  266 |       exact: true,
  267 |     }),
  268 |   ).toBeVisible();
  269 | });
  270 | test("an accepted earlier send preserves a newer paste and undo remains available during streaming", async ({
  271 |   page,
  272 |   request,
  273 | }) => {
  274 |   await page.clock.install();
  275 |   const chat = await setup(page, request);
  276 |   let release!: () => void;
  277 |   const gate = new Promise<void>((resolve) => {
  278 |     release = resolve;
  279 |   });
  280 |   await page.route(`**/api/chats/${chat}/messages`, async (route) => {
  281 |     await gate;
  282 |     await route.continue();
  283 |   });
  284 |   const field = page.locator(".composer textarea");
  285 |   const original = "#long:600 #slow:50 Synthetic fake earlier send.";
  286 |   await field.fill(original);
> 287 |   await page.getByRole("button", { name: "Send message", exact: true }).click();
      |                                                                         ^ Error: locator.click: Test timeout of 45000ms exceeded.
  288 |   await expect(page.getByTestId("optimistic-send")).toBeVisible();
  289 |   await field.fill("New draft: ");
  290 |   const raw = "Synthetic later paste fake. ".repeat(200);
  291 |   await clipboard(page, raw);
  292 |   await expect(
  293 |     page.getByRole("button", {
  294 |       name: "Review file Pasted text 1.txt",
  295 |       exact: true,
  296 |     }),
  297 |   ).toBeVisible();
  298 |   const keep = page.getByRole("button", { name: "Keep as text", exact: true });
  299 |   await expect(keep).toBeDisabled();
  300 |   await page.clock.runFor(10500);
  301 |   await expect(keep).toBeVisible();
  302 |   const sent = page.waitForResponse(
  303 |     (r) =>
  304 |       r.url().endsWith(`/api/chats/${chat}/messages`) &&
  305 |       r.request().method() === "POST",
  306 |   );
  307 |   release();
  308 |   const response = await sent;
  309 |   expect(response.request().postDataJSON().content).toBe(original);
  310 |   expect(response.request().postDataJSON().attachment_ids).toEqual([]);
  311 |   await expect(
  312 |     page.getByRole("button", { name: "Stop generating", exact: true }),
  313 |   ).toBeVisible();
  314 |   await expect(keep).toBeEnabled();
  315 |   await keep.click();
  316 |   await expect(field).toHaveValue("New draft: " + raw);
  317 |   await page
  318 |     .getByRole("button", { name: "Stop generating", exact: true })
  319 |     .click();
  320 | });
  321 | test("optimistic and confirmed attachments retain previews, real request fields and durable history", async ({
  322 |   page,
  323 |   request,
  324 | }) => {
  325 |   const chat = await setup(page, request);
  326 |   let releaseImages!: () => void, releaseSend!: () => void;
  327 |   const images = new Promise<void>((resolve) => {
  328 |     releaseImages = resolve;
  329 |   });
  330 |   const send = new Promise<void>((resolve) => {
  331 |     releaseSend = resolve;
  332 |   });
  333 |   await page.route("**/api/attachments/*", async (route) => {
  334 |     if (route.request().resourceType() === "image") await images;
  335 |     await route.continue().catch(() => undefined);
  336 |   });
  337 |   await page.route(`**/api/chats/${chat}/messages`, async (route) => {
  338 |     await send;
  339 |     await route.continue();
  340 |   });
  341 |   const png = await readFile(
  342 |     "../server/tests/fixtures/images/fake-synthetic.png",
  343 |   );
  344 |   const uploaded = page.waitForResponse(
  345 |     (r) =>
  346 |       r.url().endsWith("/api/attachments") && r.request().method() === "POST",
  347 |   );
  348 |   await page.locator('input[type="file"]').setInputFiles({
  349 |     name: "Harbor-send-fake.png",
  350 |     mimeType: "image/png",
  351 |     buffer: png,
  352 |   });
  353 |   const attachment = await (await uploaded).json();
  354 |   await expect(
  355 |     page.getByRole("button", {
  356 |       name: `Open photo ${attachment.filename}`,
  357 |       exact: true,
  358 |     }),
  359 |   ).toBeVisible();
  360 |   await page
  361 |     .locator(".composer textarea")
  362 |     .fill("Describe the synthetic fake photo.");
  363 |   await page.getByRole("button", { name: "Send message", exact: true }).click();
  364 |   const optimistic = page.getByTestId("optimistic-send");
  365 |   await expect(optimistic.locator(".message-photo img")).toBeVisible();
  366 |   const preview = await optimistic
  367 |     .locator(".message-photo img")
  368 |     .getAttribute("src");
  369 |   expect(preview).toMatch(/^blob:/);
  370 |   const sent = page.waitForResponse(
  371 |     (r) =>
  372 |       r.url().endsWith(`/api/chats/${chat}/messages`) &&
  373 |       r.request().method() === "POST",
  374 |   );
  375 |   releaseSend();
  376 |   const response = await sent;
  377 |   expect(response.ok()).toBe(true);
  378 |   const body = response.request().postDataJSON();
  379 |   expect(body).toEqual({
  380 |     content: "Describe the synthetic fake photo.",
  381 |     parent_id: null,
  382 |     attachment_ids: [attachment.id],
  383 |     web: false,
  384 |   });
  385 |   await expect(optimistic).toHaveCount(0);
  386 |   const photo = page
  387 |     .getByRole("article", { name: "user message", exact: true })
```
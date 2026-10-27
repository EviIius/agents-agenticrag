# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat-state.spec.ts >> image-mode followup shows its source, pins that branch and never silently generates on reference failure
- Location: web/tests/chat-state.spec.ts:102:1

# Error details

```
Test timeout of 45000ms exceeded.
```

```
Error: locator.click: Test timeout of 45000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'Edit image', exact: true })

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
              - link "Synthetic Part B image" [ref=e35] [cursor=pointer]:
                - /url: /c/3eff3365af6d4ca59ba2c9bd16c40cf1
              - button "Actions for Synthetic Part B image" [ref=e36] [cursor=pointer]
          - generic [ref=e38]:
            - link "Synthetic Part B image" [ref=e39] [cursor=pointer]:
              - /url: /c/d695b0518cfb4ec2928bf982b50f7c95
            - button "Actions for Synthetic Part B image" [ref=e40] [cursor=pointer]
        - button "Settings" [ref=e43] [cursor=pointer]
    - main [ref=e44]:
      - generic [ref=e45]:
        - button "Choose model" [ref=e47] [cursor=pointer]:
          - generic [aria-hidden] [ref=e48]: ●
          - generic [ref=e49]: fake-chat
          - generic [ref=e50]: Fake runtime
        - generic "Double-click to rename" [ref=e51]: Synthetic Part B image
        - button "Chat controls" [ref=e52] [cursor=pointer]
        - button "Actions for Synthetic Part B image" [ref=e53] [cursor=pointer]
      - status [ref=e54]
      - log "Conversation" [ref=e55]:
        - generic [ref=e56]:
          - article "user message" [ref=e57]:
            - heading "You said" [level=2] [ref=e58]
            - generic [ref=e59]:
              - paragraph [ref=e61]: Create image
              - paragraph [ref=e66]: Synthetic Part B image
            - button "Copy message" [ref=e70] [cursor=pointer]:
              - status [ref=e71]
          - article "assistant message" [ref=e72]:
            - heading "Assistant replied" [level=2] [ref=e73]
            - generic [ref=e74]:
              - paragraph [ref=e75]: FLUX.2 klein 4B · Generated image
              - group "Images in this turn" [ref=e76]:
                - generic [ref=e77]:
                  - button "Open image 1" [ref=e78] [cursor=pointer]:
                    - img "Synthetic Part B image" [ref=e79]
                  - generic [ref=e80]:
                    - button "Save image" [ref=e81] [cursor=pointer]
                    - button "More like this" [ref=e82] [cursor=pointer]
                    - button "Refine image" [ref=e83] [cursor=pointer]
                    - button "Copy image prompt" [ref=e84] [cursor=pointer]:
                      - status [ref=e85]
                    - button "Image details" [ref=e86] [cursor=pointer]
                    - button "More image actions" [ref=e87] [cursor=pointer]
              - status [ref=e88]:
                - generic [ref=e89]: 1 image · 0 s
              - generic [ref=e90]:
                - button "Try again" [ref=e91] [cursor=pointer]
                - button "Copy prompt" [ref=e92] [cursor=pointer]:
                  - status [ref=e93]
                  - text: Copy prompt
          - article "user message" [ref=e94]:
            - heading "You said" [level=2] [ref=e95]
            - generic [ref=e96]:
              - generic [ref=e97]:
                - paragraph [ref=e98]: Edit photo · Photo reference
                - button "View source photo" [ref=e103] [cursor=pointer]:
                  - img "Source photo used for this edit" [ref=e104]
              - paragraph [ref=e105]: Add a synthetic hat
            - generic [ref=e108]:
              - button "Copy message" [ref=e109] [cursor=pointer]:
                - status [ref=e110]
              - button "Previous branch" [ref=e111] [cursor=pointer]
              - generic [ref=e112]: 2 / 2
              - button "Next branch" [disabled]
          - article "assistant message" [ref=e113]:
            - heading "Assistant replied" [level=2] [ref=e114]
            - generic [ref=e115]:
              - paragraph [ref=e116]: FLUX.2 klein 4B · Photo edit
              - group "Images in this turn" [ref=e117]:
                - generic [ref=e118]:
                  - button "Open image 1" [ref=e119] [cursor=pointer]:
                    - img "Add a synthetic hat" [ref=e120]
                  - generic [ref=e121]:
                    - button "Save image" [ref=e122] [cursor=pointer]
                    - button "More like this" [ref=e123] [cursor=pointer]
                    - button "Refine image" [ref=e124] [cursor=pointer]
                    - button "Copy image prompt" [ref=e125] [cursor=pointer]:
                      - status [ref=e126]
                    - button "Image details" [ref=e127] [cursor=pointer]
                    - button "More image actions" [ref=e128] [cursor=pointer]
              - status [ref=e129]:
                - generic [ref=e130]: 1 image · 0 s
              - generic [ref=e131]:
                - button "Try again" [ref=e132] [cursor=pointer]
                - button "Copy prompt" [ref=e133] [cursor=pointer]:
                  - status [ref=e134]
                  - text: Copy prompt
          - article "user message" [ref=e135]:
            - heading "You said" [level=2] [ref=e136]
            - generic [ref=e137]:
              - paragraph [ref=e139]: Create image
              - paragraph [ref=e144]: Create a separate synthetic scene
            - button "Copy message" [ref=e148] [cursor=pointer]:
              - status [ref=e149]
          - article "assistant message" [ref=e150]:
            - heading "Assistant replied" [level=2] [ref=e151]
            - generic [ref=e152]:
              - paragraph [ref=e153]: FLUX.2 klein 4B · Generated image
              - group "Images in this turn" [ref=e154]:
                - generic [ref=e155]:
                  - button "Open image 1" [ref=e156] [cursor=pointer]:
                    - img "Create a separate synthetic scene" [ref=e157]
                  - generic [ref=e158]:
                    - button "Save image" [ref=e159] [cursor=pointer]
                    - button "More like this" [ref=e160] [cursor=pointer]
                    - button "Refine image" [ref=e161] [cursor=pointer]
                    - button "Copy image prompt" [ref=e162] [cursor=pointer]:
                      - status [ref=e163]
                    - button "Image details" [ref=e164] [cursor=pointer]
                    - button "More image actions" [ref=e165] [cursor=pointer]
              - status [ref=e166]:
                - generic [ref=e167]: 1 image · 0 s
              - generic [ref=e168]:
                - button "Try again" [ref=e169] [cursor=pointer]
                - button "Copy prompt" [ref=e170] [cursor=pointer]:
                  - status [ref=e171]
                  - text: Copy prompt
      - generic [ref=e172]:
        - button [aria-hidden] [ref=e173] [cursor=pointer]
        - form "Message" [ref=e174]:
          - textbox "Image prompt" [active] [ref=e175]:
            - /placeholder: Describe an image…
            - text: An edit that cannot find its source
          - generic [ref=e176]:
            - button "Leave image mode" [pressed] [ref=e177] [cursor=pointer]: Create image
            - button "Image count" [ref=e178] [cursor=pointer]: 1 image
            - button "Image options" [ref=e179] [cursor=pointer]
            - generic [ref=e180]:
              - generic [ref=e181]: FLUX.2 klein 4B · 1024²
              - button "Create image" [ref=e183] [cursor=pointer]
  - region "Notifications alt+T"
```

# Test source

```ts
  78  |     .first()
  79  |     .getByRole("button", { name: "View source photo" })
  80  |     .click();
  81  |   await expect(
  82  |     page.getByRole("dialog", { name: "Image viewer" }),
  83  |   ).toBeVisible();
  84  |   await page.getByRole("button", { name: "Close image viewer" }).click();
  85  |   await page.reload();
  86  |   await expect(sources.first()).toContainText("Edit photo");
  87  |   expect(
  88  |     (
  89  |       await request.post("/api/images/references/clear", {
  90  |         data: { confirm: true },
  91  |       })
  92  |     ).ok(),
  93  |   ).toBeTruthy();
  94  |   await page.reload();
  95  |   await expect(sources.first()).toContainText("Source photo unavailable");
  96  |   await expect(sources.first().getByRole("img")).toHaveCount(0);
  97  |   await expect(
  98  |     page.locator('[data-slot="image-turn"] img.is-loaded'),
  99  |   ).toHaveCount(2);
  100 | });
  101 | 
  102 | test("image-mode followup shows its source, pins that branch and never silently generates on reference failure", async ({
  103 |   page,
  104 |   request,
  105 | }) => {
  106 |   const { chat } = await setup(request);
  107 |   const first = await image(request, chat.id);
  108 |   const second = await image(request, chat.id);
  109 |   await request.patch(`/api/chats/${chat.id}`, {
  110 |     data: { current_leaf_id: first.assistant.id },
  111 |   });
  112 |   await page.goto(`/c/${chat.id}?image=1`);
  113 |   const followup = page.locator('[data-slot="image-followup"]');
  114 |   await expect(followup).toContainText("Edit last image");
  115 |   await expect(followup.getByRole("img")).toHaveAttribute(
  116 |     "src",
  117 |     `/api/images/jobs/${first.assistant.images[0].id}/output/png`,
  118 |   );
  119 |   await expect(page.getByRole("button", { name: "Image count" })).toHaveCount(
  120 |     0,
  121 |   );
  122 |   const bodies: Record<string, unknown>[] = [];
  123 |   await page.route(
  124 |     `**/api/chats/${chat.id}/image-references/from-job`,
  125 |     async (route) => {
  126 |       const response = await route.fetch();
  127 |       // Simulate another client changing the branch while the clone is in flight.
  128 |       await request.patch(`/api/chats/${chat.id}`, {
  129 |         data: { current_leaf_id: second.assistant.id },
  130 |       });
  131 |       await route.fulfill({ response });
  132 |     },
  133 |   );
  134 |   await page.route(`**/api/chats/${chat.id}/images`, async (route) => {
  135 |     bodies.push(route.request().postDataJSON());
  136 |     await route.continue();
  137 |   });
  138 |   await page
  139 |     .getByRole("textbox", { name: "Image prompt" })
  140 |     .fill("Add a synthetic hat");
  141 |   await page.getByRole("button", { name: "Edit image", exact: true }).click();
  142 |   await expect.poll(() => bodies.length).toBe(1);
  143 |   expect(bodies[0]).toMatchObject({ parent_id: first.assistant.id, count: 1 });
  144 |   expect(bodies[0].reference_id).toEqual(expect.any(String));
  145 |   await expect(page.locator('[data-slot="image-turn"]').last()).toContainText(
  146 |     "Photo edit",
  147 |   );
  148 |   await expect(
  149 |     page.locator('[data-slot="image-turn"]').last().locator("img.is-loaded"),
  150 |   ).toBeVisible();
  151 |   await page.unroute(`**/api/chats/${chat.id}/image-references/from-job`);
  152 |   await followup.getByRole("button", { name: "Create image instead" }).click();
  153 |   await expect(followup).toHaveCount(0);
  154 |   await expect(page.getByRole("button", { name: "Image count" })).toBeVisible();
  155 |   await page
  156 |     .getByRole("textbox", { name: "Image prompt" })
  157 |     .fill("Create a separate synthetic scene");
  158 |   await page.getByRole("button", { name: "Create image", exact: true }).click();
  159 |   await expect.poll(() => bodies.length).toBe(2);
  160 |   expect(bodies[1]).not.toHaveProperty("reference_id");
  161 |   await expect(
  162 |     page.locator('[data-slot="image-turn"]').last().locator("img.is-loaded"),
  163 |   ).toBeVisible();
  164 |   await page.route(
  165 |     `**/api/chats/${chat.id}/image-references/from-job`,
  166 |     (route) =>
  167 |       route.fulfill({
  168 |         status: 404,
  169 |         contentType: "application/json",
  170 |         body: JSON.stringify({
  171 |           error: { code: "not_found", message: "Synthetic source unavailable" },
  172 |         }),
  173 |       }),
  174 |   );
  175 |   await page
  176 |     .getByRole("textbox", { name: "Image prompt" })
  177 |     .fill("An edit that cannot find its source");
> 178 |   await page.getByRole("button", { name: "Edit image", exact: true }).click();
      |                                                                       ^ Error: locator.click: Test timeout of 45000ms exceeded.
  179 |   await expect(page.getByRole("alert")).toContainText(
  180 |     "Synthetic source unavailable",
  181 |   );
  182 |   expect(bodies).toHaveLength(2);
  183 |   await expect(page.getByRole("textbox", { name: "Image prompt" })).toHaveValue(
  184 |     "An edit that cannot find its source",
  185 |   );
  186 | });
  187 | 
  188 | test("stopped and empty replies are visible, Continue names its parent and preserves the unsent draft", async ({
  189 |   page,
  190 |   request,
  191 | }) => {
  192 |   const { connection, chat } = await setup(request);
  193 |   const model = {
  194 |     connection_id: connection.id,
  195 |     model_id: "fake-chat",
  196 |     display_name: "fake-chat",
  197 |   };
  198 |   const rows = [
  199 |     {
  200 |       id: "stopped-synthetic",
  201 |       chat_id: chat.id,
  202 |       role: "assistant",
  203 |       status: "stopped",
  204 |       content: "I'd begin",
  205 |       model,
  206 |       created_at: chat.created_at,
  207 |     },
  208 |     {
  209 |       id: "empty-synthetic",
  210 |       chat_id: chat.id,
  211 |       parent_id: "stopped-synthetic",
  212 |       role: "assistant",
  213 |       status: "complete",
  214 |       content: "",
  215 |       reasoning: "Synthetic reasoning without a final answer",
  216 |       model,
  217 |       created_at: chat.created_at,
  218 |     },
  219 |   ];
  220 |   await page.route(`**/api/chats/${chat.id}`, (route) =>
  221 |     route.fulfill({
  222 |       contentType: "application/json",
  223 |       body: JSON.stringify({
  224 |         chat: { ...chat, current_leaf_id: "empty-synthetic" },
  225 |         messages: rows,
  226 |       }),
  227 |     }),
  228 |   );
  229 |   let body: Record<string, unknown> | undefined;
  230 |   await page.route(`**/api/chats/${chat.id}/messages`, (route) => {
  231 |     body = route.request().postDataJSON();
  232 |     return route.fulfill({
  233 |       status: 503,
  234 |       contentType: "application/json",
  235 |       body: JSON.stringify({
  236 |         error: {
  237 |           code: "unavailable",
  238 |           message: "Synthetic rejected continuation",
  239 |         },
  240 |       }),
  241 |     });
  242 |   });
  243 |   await page.goto(`/c/${chat.id}`);
  244 |   const stopped = page.locator('[data-message-id="stopped-synthetic"]');
  245 |   const empty = page.locator('[data-message-id="empty-synthetic"]');
  246 |   await expect(stopped.locator('[data-slot="reply-outcome"]')).toContainText(
  247 |     "Stopped",
  248 |   );
  249 |   await expect(
  250 |     stopped.getByRole("button", { name: "Retry", exact: true }),
  251 |   ).toHaveCount(1);
  252 |   await expect(
  253 |     stopped.getByRole("button", { name: "Regenerate answer", exact: true }),
  254 |   ).toHaveCount(0);
  255 |   await expect(empty.locator('[data-slot="reply-outcome"]')).toContainText(
  256 |     "No answer",
  257 |   );
  258 |   await page.locator(".composer textarea").fill("An unsent draft");
  259 |   await stopped.getByRole("button", { name: "Continue", exact: true }).click();
  260 |   await expect(page.getByRole("alert")).toContainText(
  261 |     "Synthetic rejected continuation",
  262 |   );
  263 |   expect(body).toMatchObject({
  264 |     content: "Continue your previous answer.",
  265 |     parent_id: "stopped-synthetic",
  266 |     attachment_ids: [],
  267 |   });
  268 |   await expect(page.locator(".composer textarea")).toHaveValue(
  269 |     "An unsent draft",
  270 |   );
  271 |   await expect(stopped).toContainText("I'd begin");
  272 | });
  273 | 
  274 | test("one Save retains reasoning, saves only changed scopes, and retries a partial failure without repeating the chat save", async ({
  275 |   page,
  276 |   request,
  277 | }) => {
  278 |   const { connection, chat } = await setup(request);
```
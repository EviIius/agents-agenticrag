# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: workflow-studio-editor.spec.ts >> Design catalogue exposes every editing panel and Quick add in both themes and sizes
- Location: tests/workflow-studio-editor.spec.ts:522:1

# Error details

```
Error: 390/light/setup-transcribe

expect(received).toEqual(expected) // deep equality

- Expected  -   1
+ Received  + 105

- Array []
+ Array [
+   Object {
+     "description": "Ensure the contrast between foreground and background colors meets WCAG 2 AA minimum contrast ratio thresholds",
+     "help": "Elements must meet minimum color contrast ratio thresholds",
+     "helpUrl": "https://dequeuniversity.com/rules/axe/4.13/color-contrast?application=playwright",
+     "id": "color-contrast",
+     "impact": "serious",
+     "nodes": Array [
+       Object {
+         "all": Array [],
+         "any": Array [
+           Object {
+             "data": Object {
+               "bgColor": "#fdfcfb",
+               "contrastRatio": 3.32,
+               "expectedContrastRatio": "4.5:1",
+               "fgColor": "#8c8b88",
+               "fontSize": "10.5pt (14px)",
+               "fontWeight": "normal",
+               "messageKey": null,
+             },
+             "id": "color-contrast",
+             "impact": "serious",
+             "message": "Element has insufficient color contrast of 3.32 (foreground color: #8c8b88, background color: #fdfcfb, font size: 10.5pt (14px), font weight: normal). Expected contrast ratio of 4.5:1",
+             "relatedNodes": Array [
+               Object {
+                 "html": "<div class=\"wf-outline-row\" data-disabled=\"true\" data-selected=\"false\">",
+                 "target": Array [
+                   "div[data-disabled=\"true\"]",
+                 ],
+               },
+               Object {
+                 "html": "<div class=\"wf-studio\" tabindex=\"-1\">",
+                 "target": Array [
+                   ".wf-studio",
+                 ],
+               },
+             ],
+           },
+         ],
+         "failureSummary": "Fix any of the following:
+   Element has insufficient color contrast of 3.32 (foreground color: #8c8b88, background color: #fdfcfb, font size: 10.5pt (14px), font weight: normal). Expected contrast ratio of 4.5:1",
+         "html": "<span class=\"block truncate font-medium\">Clean up transcript</span>",
+         "impact": "serious",
+         "none": Array [],
+         "target": Array [
+           "button[aria-label=\"Configure Clean up transcript\"] > .min-w-0.flex-1 > .block.truncate",
+         ],
+       },
+       Object {
+         "all": Array [],
+         "any": Array [
+           Object {
+             "data": Object {
+               "bgColor": "#fdfcfb",
+               "contrastRatio": 2.34,
+               "expectedContrastRatio": "4.5:1",
+               "fgColor": "#a9a7a2",
+               "fontSize": "9.0pt (12px)",
+               "fontWeight": "normal",
+               "messageKey": null,
+             },
+             "id": "color-contrast",
+             "impact": "serious",
+             "message": "Element has insufficient color contrast of 2.34 (foreground color: #a9a7a2, background color: #fdfcfb, font size: 9.0pt (12px), font weight: normal). Expected contrast ratio of 4.5:1",
+             "relatedNodes": Array [
+               Object {
+                 "html": "<div class=\"wf-outline-row\" data-disabled=\"true\" data-selected=\"false\">",
+                 "target": Array [
+                   "div[data-disabled=\"true\"]",
+                 ],
+               },
+               Object {
+                 "html": "<div class=\"wf-studio\" tabindex=\"-1\">",
+                 "target": Array [
+                   ".wf-studio",
+                 ],
+               },
+             ],
+           },
+         ],
+         "failureSummary": "Fix any of the following:
+   Element has insufficient color contrast of 2.34 (foreground color: #a9a7a2, background color: #fdfcfb, font size: 9.0pt (12px), font weight: normal). Expected contrast ratio of 4.5:1",
+         "html": "<span class=\"wf-summary\">Disabled · skipped when the workflow runs</span>",
+         "impact": "serious",
+         "none": Array [],
+         "target": Array [
+           "button[aria-label=\"Configure Clean up transcript\"] > .min-w-0.flex-1 > .wf-summary",
+         ],
+       },
+     ],
+     "tags": Array [
+       "cat.color",
+       "wcag2aa",
+       "wcag143",
+       "TTv5",
+       "TT13.c",
+       "EN-301-549",
+       "EN-9.1.4.3",
+       "ACT",
+       "RGAAv4",
+       "RGAA-3.2.1",
+     ],
+   },
+ ]
```

# Page snapshot

```yaml
- generic [active]:
  - generic:
    - generic [aria-hidden]:
      - main:
        - generic:
          - generic:
            - button
            - generic:
              - button:
                - generic [aria-hidden]: ●
                - generic: fake-chat
          - generic:
            - button
            - button
        - generic:
          - generic:
            - generic:
              - paragraph: Workflow Studio · fake runtime states
              - button: light
              - button: dark
              - button: canvas
              - button: empty
              - button: selected
              - button: problems
              - button: conflict
              - button: outline
              - button: non-nestable
              - button: settings
              - button: run-inputs
              - button: cards
              - button: home-cards
              - button: quick-add
              - button: setup-start
              - button: setup-generate
              - button: setup-transcribe
              - button: setup-clean_transcript
              - button: setup-generate_image
              - button: setup-review
              - button: setup-output
            - generic:
              - generic:
                - button
                - link:
                  - /url: /workflows
                - button: Synthetic image workflow
                - button
                - button: Run
              - generic:
                - generic:
                  - generic:
                    - generic:
                      - button:
                        - generic:
                          - generic: Start
                          - generic: "Inputs: Recording"
                      - button
                    - generic:
                      - button
                  - generic:
                    - generic:
                      - button:
                        - generic:
                          - generic: Transcribe recording
                          - generic: "{{start.recording}}"
                      - button
                    - generic:
                      - button
                  - generic:
                    - generic:
                      - button:
                        - generic:
                          - generic: Clean up transcript
                          - generic: Disabled · skipped when the workflow runs
                      - button
                    - generic:
                      - button
                  - generic:
                    - generic:
                      - button:
                        - generic:
                          - generic: Draft meeting pack
                          - generic: fake-chat · Markdown
                      - button
                    - generic:
                      - button
                  - generic:
                    - generic:
                      - button:
                        - generic:
                          - generic: Save results
                          - generic: Markdown, JSON · 1 items
                      - button
              - button
    - region "Notifications alt+T"
  - dialog [ref=f13e2]:
    - heading "Transcribe recording" [level=2] [ref=f13e4]
    - paragraph [ref=f13e5]: Edit this workflow's settings.
    - generic [ref=f13e6]:
      - banner [ref=f13e7]:
        - generic [ref=f13e10]:
          - textbox "Block name" [ref=f13e11]: Transcribe recording
          - paragraph [ref=f13e12]: Transcribe recording
        - button "Actions for Transcribe recording" [ref=f13e13] [cursor=pointer]
        - button "Close Inspector" [ref=f13e14] [cursor=pointer]
      - generic [ref=f13e15]:
        - tablist "Block settings" [ref=f13e16]:
          - tab "Setup" [selected] [ref=f13e17] [cursor=pointer]
          - tab "Output" [ref=f13e18] [cursor=pointer]
        - tabpanel "Setup" [ref=f13e19]:
          - generic [ref=f13e20]:
            - generic [ref=f13e21]: Recording
            - generic [ref=f13e22]:
              - generic [aria-hidden]:
                - mark: "{{start.recording}}"
              - textbox "Recording" [ref=f13e23]: "{{start.recording}}"
              - button "Insert a variable in Recording" [ref=f13e24] [cursor=pointer]: "{x}"
            - paragraph [ref=f13e25]: A Recording input from Start. Uses your glossary from Settings.
          - region "Connections" [ref=f13e26]:
            - heading "GETS INPUT FROM" [level=3] [ref=f13e27]
            - generic [ref=f13e28]:
              - generic [ref=f13e29]: Start
              - button "Remove input connection e_start_transcript" [ref=f13e30] [cursor=pointer]
            - generic [ref=f13e31]:
              - generic [ref=f13e32]: Add an input connection
              - combobox "Add an input connection" [ref=f13e33] [cursor=pointer]:
                - generic: Add connection…
            - heading "SENDS OUTPUT TO" [level=3] [ref=f13e34]
            - generic [ref=f13e35]:
              - generic [ref=f13e36]: Clean up transcript
              - button "Remove output connection e_transcript_clean" [ref=f13e37] [cursor=pointer]
            - generic [ref=f13e38]:
              - generic [ref=f13e39]: Draft meeting pack
              - button "Remove output connection e_transcript_pack" [ref=f13e40] [cursor=pointer]
            - generic [ref=f13e41]:
              - generic [ref=f13e42]: Add an output connection
              - combobox "Add an output connection" [ref=f13e43] [cursor=pointer]:
                - generic: Add connection…
          - generic [ref=f13e44]:
            - heading "PRODUCES" [level=3] [ref=f13e45]
            - generic [ref=f13e46]:
              - button "Copy reference transcript.transcript" [ref=f13e47] [cursor=pointer]: "{{transcript.transcript}}"
              - button "Copy reference transcript.text" [ref=f13e48] [cursor=pointer]: "{{transcript.text}}"
              - button "Copy reference transcript.timestamped_text" [ref=f13e49] [cursor=pointer]: "{{transcript.timestamped_text}}"
              - button "Copy reference transcript.segments" [ref=f13e50] [cursor=pointer]: "{{transcript.segments}}"
              - button "Copy reference transcript.filename" [ref=f13e51] [cursor=pointer]: "{{transcript.filename}}"
          - group [ref=f13e52]:
            - generic "Advanced" [ref=f13e53] [cursor=pointer]
```

# Test source

```ts
  474 |     );
  475 |     detached.id = "n_detached";
  476 |     detached.key = "detached";
  477 |     detached.title = "Synthetic detached";
  478 |     branched.nodes.push(detached);
  479 |     await put(branched);
  480 |     await page.reload();
  481 |     await expect(
  482 |       page.getByText(
  483 |         "Part of this workflow is easier to change on a larger screen. Settings still open here.",
  484 |       ),
  485 |     ).toBeVisible();
  486 |     await expect(
  487 |       page.getByRole("button", { name: "Insert after Start", exact: true }),
  488 |     ).toBeDisabled();
  489 |     await page
  490 |       .getByRole("button", {
  491 |         name: "Actions for Synthetic detached",
  492 |         exact: true,
  493 |       })
  494 |       .tap();
  495 |     await expect(
  496 |       page.getByRole("menuitem", { name: "Duplicate", exact: true }),
  497 |     ).toHaveAttribute("aria-disabled", "true");
  498 |     await expect(
  499 |       page.getByRole("menuitem", { name: "Delete", exact: true }),
  500 |     ).toHaveAttribute("aria-disabled", "true");
  501 |     await page.keyboard.press("Escape");
  502 |     await page
  503 |       .getByRole("button", {
  504 |         name: "Configure Synthetic detached",
  505 |         exact: true,
  506 |       })
  507 |       .tap();
  508 |     await page
  509 |       .getByRole("textbox", { name: "Block name", exact: true })
  510 |       .fill("Synthetic edited on phone");
  511 |     await page
  512 |       .getByRole("button", { name: "Close Inspector", exact: true })
  513 |       .tap();
  514 |     await saved(page);
  515 |     expect(
  516 |       (await def(request, d.id)).graph.nodes.find((n) => n.id === detached.id)!
  517 |         .title,
  518 |     ).toBe("Synthetic edited on phone");
  519 |   });
  520 | });
  521 | 
  522 | test("Design catalogue exposes every editing panel and Quick add in both themes and sizes", async ({
  523 |   page,
  524 |   request,
  525 |   browserName,
  526 | }) => {
  527 |   test.setTimeout(240000);
  528 |   await request.patch("/api/settings", {
  529 |     data: { "appearance.reduce_motion": "system" },
  530 |   });
  531 |   const states = [
  532 |     "empty",
  533 |     "selected",
  534 |     "problems",
  535 |     "conflict",
  536 |     "outline",
  537 |     "non-nestable",
  538 |     "settings",
  539 |     "run-inputs",
  540 |     "cards",
  541 |     "home-cards",
  542 |     "quick-add",
  543 |     ...[
  544 |       "start",
  545 |       "generate",
  546 |       "transcribe",
  547 |       "clean_transcript",
  548 |       "generate_image",
  549 |       "review",
  550 |       "output",
  551 |     ].map((k) => "setup-" + k),
  552 |   ];
  553 |   const results = [];
  554 |   await mkdir(dir, { recursive: true });
  555 |   for (const width of [390, 1440]) {
  556 |     await page.setViewportSize({ width, height: 900 });
  557 |     for (const theme of ["light", "dark"]) {
  558 |       for (const state of states) {
  559 |         await page.goto(`/design?studio&state=${state}`);
  560 |         await expect(
  561 |           page.getByText("Workflow Studio · fake runtime states"),
  562 |         ).toBeVisible();
  563 |         await page.evaluate(
  564 |           (v) => (document.documentElement.dataset.theme = v),
  565 |           theme,
  566 |         );
  567 |         await settle(page);
  568 |         const scan = await new AxeBuilder({ page }).analyze();
  569 |         expect(
  570 |           scan.violations.filter((v) =>
  571 |             ["serious", "critical"].includes(v.impact ?? ""),
  572 |           ),
  573 |           `${width}/${theme}/${state}`,
> 574 |         ).toEqual([]);
      |           ^ Error: 390/light/setup-transcribe
  575 |         expect(
  576 |           await page.evaluate(
  577 |             () => document.documentElement.scrollWidth <= innerWidth,
  578 |           ),
  579 |           `${width}/${theme}/${state} overflow`,
  580 |         ).toBe(true);
  581 |         results.push({ width, theme, state, seriousCritical: 0 });
  582 |         await page.screenshot({
  583 |           path: `${dir}/design-${state}-${width}-${theme}-${browserName}-fake.png`,
  584 |         });
  585 |       }
  586 |     }
  587 |   }
  588 |   await writeFile(
  589 |     `${dir}/axe-design-${browserName}.json`,
  590 |     JSON.stringify(results, null, 2),
  591 |   );
  592 | });
  593 | 
```
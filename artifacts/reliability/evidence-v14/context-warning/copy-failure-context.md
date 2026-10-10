# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: conversation-motion.spec.ts >> code and transcript copy show a local check and clear it after 1.5 seconds
- Location: tests/conversation-motion.spec.ts:623:1

# Error details

```
Error: expect(locator).toBeInViewport() failed

Locator:  getByRole('region', { name: 'Conversation motion', exact: true }).locator('[data-streamdown="code-block-copy-button"]').first()
Expected: in viewport
Received: viewport ratio 0
Timeout:  5000ms

Call log:
  - Expect "toBeInViewport" getByRole('region', { name: 'Conversation motion', exact: true }).locator('[data-streamdown="code-block-copy-button"]').first() with timeout 5000ms
  - waiting for getByRole('region', { name: 'Conversation motion', exact: true }).locator('[data-streamdown="code-block-copy-button"]').first()
    13 × locator resolved to <button type="button" title="Copy Code" aria-label="Copy Code" data-streamdown="code-block-copy-button" class="cursor-pointer p-1 text-muted-foreground transition-all hover:text-foreground disabled:cursor-not-allowed disabled:opacity-50">…</button>
       - unexpected value "viewport ratio 0"

```

```yaml
- button "Copy Code"
```

# Test source

```ts
  552 |           "appearance.theme": theme,
  553 |           "appearance.reduce_motion": "system",
  554 |         },
  555 |       });
  556 |       await page.setViewportSize({ width, height: 900 });
  557 |       await page.goto("/design");
  558 |       await page
  559 |         .locator(".design-page > header")
  560 |         .getByRole("button", {
  561 |           name: theme === "dark" ? "Dark" : "Light",
  562 |           exact: true,
  563 |         })
  564 |         .click();
  565 |       const preview = page.getByRole("region", {
  566 |         name: "Conversation motion",
  567 |         exact: true,
  568 |       });
  569 |       const results: { state: string; violations: string[] }[] = [];
  570 |       for (const state of [
  571 |         "optimistic",
  572 |         "waiting",
  573 |         "reasoning",
  574 |         "streaming",
  575 |         "search",
  576 |         "complete",
  577 |       ]) {
  578 |         await preview
  579 |           .getByRole("button", { name: `Preview ${state}`, exact: true })
  580 |           .click();
  581 |         await settle(page);
  582 |         const axe = await new AxeBuilder({ page })
  583 |           .include('[aria-label="Conversation motion"]')
  584 |           .analyze();
  585 |         const violations = axe.violations.filter((item) =>
  586 |           ["serious", "critical"].includes(item.impact ?? ""),
  587 |         );
  588 |         results.push({ state, violations: violations.map((item) => item.id) });
  589 |         expect(violations).toEqual([]);
  590 |       }
  591 |       await page
  592 |         .getByRole("button", { name: "Preview JSON export", exact: true })
  593 |         .click();
  594 |       const dialog = page.getByRole("dialog", {
  595 |         name: "Export chat",
  596 |         exact: true,
  597 |       });
  598 |       await settle(page);
  599 |       await expect(
  600 |         dialog.getByRole("button", { name: "Cancel", exact: true }),
  601 |       ).toBeInViewport({ ratio: 1 });
  602 |       const axe = await new AxeBuilder({ page }).analyze();
  603 |       const violations = axe.violations.filter((item) =>
  604 |         ["serious", "critical"].includes(item.impact ?? ""),
  605 |       );
  606 |       results.push({
  607 |         state: "export-json",
  608 |         violations: violations.map((item) => item.id),
  609 |       });
  610 |       expect(violations).toEqual([]);
  611 |       await mkdir("../artifacts/phase-4/4c", { recursive: true });
  612 |       await page.screenshot({
  613 |         path: `../artifacts/phase-4/4c/export-${width}-${theme}-${test.info().project.name}-fake.png`,
  614 |         animations: "disabled",
  615 |       });
  616 |       await writeFile(
  617 |         `../artifacts/phase-4/4c/axe-${width}-${theme}-${test.info().project.name}-fake.json`,
  618 |         JSON.stringify(results, null, 2),
  619 |       );
  620 |     });
  621 |   }
  622 | 
  623 | test("code and transcript copy show a local check and clear it after 1.5 seconds", async ({
  624 |   page,
  625 | }) => {
  626 |   await page.goto("/design");
  627 |   await page.evaluate(() =>
  628 |     Object.defineProperty(navigator, "clipboard", {
  629 |       configurable: true,
  630 |       value: { writeText: async () => {} },
  631 |     }),
  632 |   );
  633 |   const preview = page.getByRole("region", {
  634 |     name: "Conversation motion",
  635 |     exact: true,
  636 |   });
  637 |   await preview
  638 |     .getByRole("button", { name: "Preview complete", exact: true })
  639 |     .click();
  640 |   const code = preview
  641 |     .locator('[data-streamdown="code-block-copy-button"]')
  642 |     .first();
  643 |   // WebKit's automatic nearest scrolling left this control below the viewport
  644 |   // on the expanded /design page. Exercise a visible control after user scrolling.
  645 |   await code.evaluate((element) =>
  646 |     element.scrollIntoView({
  647 |       block: "center",
  648 |       inline: "center",
  649 |       behavior: "instant",
  650 |     }),
  651 |   );
> 652 |   await expect(code).toBeInViewport();
      |                      ^ Error: expect(locator).toBeInViewport() failed
  653 |   await code.click();
  654 |   await expect(code.locator('[data-slot="copy-check"]')).toBeVisible();
  655 |   await expect(
  656 |     preview.getByRole("status").filter({ hasText: "Copied" }),
  657 |   ).toContainText("Copied");
  658 |   await expect(code.locator('[data-slot="copy-check"]')).toHaveCount(0);
  659 |   await page
  660 |     .getByRole("button", { name: "Preview transcript panel", exact: true })
  661 |     .click();
  662 |   const transcript = page.getByRole("dialog", {
  663 |     name: "Synthetic recording.wav",
  664 |     exact: true,
  665 |   });
  666 |   await transcript.getByRole("button", { name: "Copy", exact: true }).click();
  667 |   await expect(transcript.locator('[data-slot="copy-check"]')).toBeVisible();
  668 |   await expect(
  669 |     transcript.getByRole("status").filter({ hasText: "Copied" }),
  670 |   ).toHaveText("Copied");
  671 |   await expect(transcript.locator('[data-slot="copy-check"]')).toHaveCount(0);
  672 |   await expect(page.locator("[data-sonner-toast]")).toHaveCount(0);
  673 | });
  674 | 
  675 | // Capture short-lived flags on the page clock so automation latency cannot miss them.
  676 | test("new-chat send waits for confirmation; edit and regenerate animate only newly confirmed rows", async ({
  677 |   page,
  678 |   request,
  679 | }) => {
  680 |   await existing(page, request);
  681 |   await page.goto("/");
  682 |   await page.addInitScript(() => {
  683 |     document.addEventListener("DOMContentLoaded", () => {
  684 |       const seen: Set<string> = new Set();
  685 |       Object.defineProperty(window, "freshSeen", { value: seen });
  686 |       const inspect = () =>
  687 |         document
  688 |           .querySelectorAll('article[data-fresh="true"]')
  689 |           .forEach((element) =>
  690 |             seen.add(element.getAttribute("data-message-id")!),
  691 |           );
  692 |       new MutationObserver(inspect).observe(document, {
  693 |         subtree: true,
  694 |         attributes: true,
  695 |         childList: true,
  696 |       });
  697 |     });
  698 |   });
  699 |   await page.reload();
  700 |   await page.route("**/api/chats/*/messages", async (route) => {
  701 |     await new Promise((resolve) => setTimeout(resolve, 500));
  702 |     await route.continue();
  703 |   });
  704 |   const field = page.locator(".composer textarea");
  705 |   await field.fill("Synthetic first message #long:30 #slow:30");
  706 |   await page.getByRole("button", { name: "Send message", exact: true }).click();
  707 |   await expect(field).toHaveValue("Synthetic first message #long:30 #slow:30");
  708 |   await expect(page.getByTestId("optimistic-send")).toHaveCount(0);
  709 |   await expect(page).toHaveURL(/\/c\//);
  710 |   const id = page.url().split("/c/")[1];
  711 |   await expect(
  712 |     page.getByRole("button", { name: "Stop generating", exact: true }),
  713 |   ).not.toBeVisible({ timeout: 10000 });
  714 |   let detail = await (await request.get(`/api/chats/${id}`)).json();
  715 |   let seen = await page.evaluate(() => [
  716 |     ...(window as unknown as { freshSeen: Set<string> }).freshSeen,
  717 |   ]);
  718 |   for (const message of detail.messages) expect(seen).toContain(message.id);
  719 |   await page
  720 |     .getByRole("button", { name: "Regenerate answer", exact: true })
  721 |     .click();
  722 |   await expect(
  723 |     page.getByRole("button", { name: "Stop generating", exact: true }),
  724 |   ).toBeVisible();
  725 |   await expect(
  726 |     page.getByRole("button", { name: "Stop generating", exact: true }),
  727 |   ).not.toBeVisible({ timeout: 10000 });
  728 |   detail = await (await request.get(`/api/chats/${id}`)).json();
  729 |   seen = await page.evaluate(() => [
  730 |     ...(window as unknown as { freshSeen: Set<string> }).freshSeen,
  731 |   ]);
  732 |   for (const message of detail.messages) expect(seen).toContain(message.id);
  733 |   await page.getByRole("button", { name: "Edit message", exact: true }).click();
  734 |   await page
  735 |     .getByRole("textbox", { name: "Edit message", exact: true })
  736 |     .fill("Synthetic edited message #long:30 #slow:30");
  737 |   await page.getByRole("button", { name: "Send", exact: true }).click();
  738 |   await expect(
  739 |     page.getByRole("button", { name: "Stop generating", exact: true }),
  740 |   ).toBeVisible();
  741 |   await expect(
  742 |     page.getByRole("button", { name: "Stop generating", exact: true }),
  743 |   ).not.toBeVisible({ timeout: 10000 });
  744 |   detail = await (await request.get(`/api/chats/${id}`)).json();
  745 |   seen = await page.evaluate(() => [
  746 |     ...(window as unknown as { freshSeen: Set<string> }).freshSeen,
  747 |   ]);
  748 |   for (const message of detail.messages) expect(seen).toContain(message.id);
  749 |   await page.reload();
  750 |   await expect(page.getByRole("article")).toHaveCount(2);
  751 |   expect(await page.locator('article[data-fresh="true"]').count()).toBe(0);
  752 | });
```
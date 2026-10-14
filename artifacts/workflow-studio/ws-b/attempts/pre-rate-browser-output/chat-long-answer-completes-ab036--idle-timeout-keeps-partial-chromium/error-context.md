# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: chat.spec.ts >> long answer completes beyond 90 seconds; idle timeout keeps partial
- Location: tests/chat.spec.ts:112:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText(/token1499/)
Expected: visible
Error: element(s) not found

Call log:
  - Expect "toBeVisible" getByText(/token1499/) with timeout 180000ms
  - waiting for getByText(/token1499/)
  - Test ended.

```

```yaml
- complementary:
  - button "Collapse sidebar"
  - text: Atelier
  - link "New chat":
    - /url: /
  - navigation "Chat history":
    - textbox "Search history":
      - /placeholder: Search chats…
    - text: ⌘K
    - navigation "Workspace":
      - link "Workflows":
        - /url: /workflows
      - link "Images":
        - /url: /images
    - region "Folders":
      - heading "Folders" [level=2]
      - button "New folder"
      - paragraph: No folders yet
    - paragraph: Today
    - 'link "#long:1500 #slow:10"':
      - /url: /c/b9ca050c11e646d494e9e2c00f2fd275
    - img "Generating response"
    - 'button "Actions for #long:1500 #slow:10"'
    - 'link "#long:350 #slow:10"':
      - /url: /c/21dce0cf280949a0ba5de3c2b8c2a962
    - 'button "Actions for #long:350 #slow:10"'
    - 'link "#long:500 #slow:50"':
      - /url: /c/dea52eda10c24866ab0a7742d11b945d
    - 'button "Actions for #long:500 #slow:50"'
    - link "Hello from the browser":
      - /url: /c/c9484559e9074933824fe8211ef0edb9
    - button "Actions for Hello from the browser"
    - link "Hello from the browser":
      - /url: /c/3f6b1fe10c9e4087afb80e5261e4a232
    - button "Actions for Hello from the browser"
    - link "Hello from the browser":
      - /url: /c/274acfa95f8a43198ceb71d290b7f9b6
    - button "Actions for Hello from the browser"
    - link "Hello from the browser":
      - /url: /c/dab5c8c114d941138cb4f2cecf51c88a
    - button "Actions for Hello from the browser"
    - link "Hello from the browser":
      - /url: /c/03eadc06cd444bb6a3150ecdfbe93949
    - button "Actions for Hello from the browser"
    - link "Hello from the browser":
      - /url: /c/49d5d623f57e4d99984ef55aca3624da
    - button "Actions for Hello from the browser"
    - link "Hello from the browser":
      - /url: /c/96d696688f14438b8a0f3f5b9a40eb22
    - button "Actions for Hello from the browser"
    - link "Hello from the browser":
      - /url: /c/a7f3da02e5e147f19b417413752bf20e
    - button "Actions for Hello from the browser"
  - button "Settings"
- main:
  - button "Choose model": fake-chat Fake runtime
  - text: "#long:1500 #slow:10"
  - button "Chat controls"
  - 'button "Actions for #long:1500 #slow:10"'
  - status: Generating response
  - log "Conversation":
    - article "user message":
      - heading "You said" [level=2]
      - paragraph: "#long:1500 #slow:10"
      - button "Copy message":
        - status
      - button "Edit message"
    - article "assistant message":
      - heading "fake-chat replied" [level=2]
      - paragraph: fake-chat
      - status
      - paragraph: token0 token1 token2 token3 token4 token5 token6 token7 token8 token9 token10 token11 token12 token13 token14 token15 token16 token17 token18 token19 token20 token21 token22 token23 token24 token25 token26 token27 token28 token29 token30 token31 token32 token33 token34 token35 token36 token37 token38 token39 token40 token41 token42 token43 token44 token45 token46 token47 token48 token49 token50 token51 token52 token53 token54 token55 token56 token57 token58 token59 token60 token61 token62 token63 token64 token65 token66 token67 token68 token69 token70 token71 token72 token73 token74 token75 token76 token77 token78 token79 token80 token81 token82 token83 token84 token85 token86 token87 token88 token89 token90 token91 token92 token93 token94 token95 token96 token97 token98 token99 token100 token101 token102 token103 token104 token105 token106 token107 token108 token109 token110 token111 token112 token113 token114 token115 token116 token117 token118 token119 token120 token121 token122 token123 token124 token125 token126 token127 token128 token129 token130 token131 token132 token133 token134 token135 token136 token137 token138 token139 token140 token141 token142 token143 token144 token145 token146 token147 token148 token149 token150 token151 token152 token153 token154 token155 token156 token157 token158 token159 token160 token161 token162 token163 token164 token165 token166 token167 token168 token169 token170 token171 token172 token173 token174 token175 token176 token177 token178 token179 token180 token181 token182 token183 token184 token185 token186 token187 token188 token189 token190 token191 token192 token193 token194 token195 token196 token197 token198 token199 token200 token201 token202 token203 token204 token205 token206 token207 token208 token209 token210 token211 token212 token213 token214 token215 token216 token217 token218 token219 token220 token221 token222 token223 token224 token225 token226 token227 token228 token229 token230 token231 token232 token233 token234 token235 token236 token237 token238 token239 token240 token241 token242 token243 token244 token245 token246 token247 token248 token249 token250 token251 token252 token253 token254 token255 token256 token257 token258 token259 token260 token261 token262 token263 token264 token265 token266 token267 token268 token269 token270 token271 token272 token273 token274 token275 token276 token277 token278 token279 token280 token281 token282 token283 token284 token285 token286 token287 token288 token289 token290 token291 token292 token293 token294 token295 token296 token297 token298 token299 token300 token301 token302 token303 token304 token305 token306 token307 token308 token309 token310 token311 token312 token313 token314 token315 token316 token317 token318 token319 token320 token321 token322 token323 token324 token325 token326 token327 token328 token329 token330 token331 token332 token333 token334 token335 token336 token337 token338 token339 token340 token341 token342 token343 token344 token345 token346 token347 token348 token349 token350 token351 token352 token353 token354 token355 token356 token357 token358 token359 token360 token361 token362 token363 token364 token365 token366 token367 token368 token369 token370 token371 token372 token373 token374 token375 token376 token377 token378 token379 token380 token381 token382 token383 token384 token385 token386 token387 token388 token389 token390 token391 token392 token393 token394 token395 token396 token397 token398 token399 token400 token401 token402 token403 token404 token405 token406 token407 token408 token409 token410 token411 token412 token413 token414 token415 token416 token417 token418 token419 token420 token421 token422 token423 token424 token425 token426 token427 token428 token429 token430 token431 token432 token433 token434 token435 token436 token437 token438 token439 token440 token441 token442 token443 token444 token445 token446 token447 token448 token449 token450 token451 token452 token453 token454 token455 token456 token457 token458 token459 token460 token461 token462 token463 token464 token465 token466 token467 token468 token469 token470 token471 token472 token473 token474 token475 token476 token477 token478 token479 token480 token481 token482 token483 token484 token485 token486 token487 token488 token489 token490 token491 token492 token493 token494 token495 token496 token497 token498 token499 token500 token501 token502 token503 token504 token505 token506 token507 token508 token509 token510 token511 token512 token513 token514 token515 token516 token517 token518 token519 token520 token521 token522 token523 token524 token525 token526 token527 token528 token529 token530 token531 token532 token533 token534 token535 token536 token537 token538 token539 token540 token541 token542 token543 token544 token545 token546 token547 token548 token549 token550 token551 token552 token553 token554 token555 token556 token557 token558 token559 token560 token561 token562 token563 token564 token565 token566 token567 token568 token569 token570 token571 token572 token573 token574 token575 token576 token577 token578 token579 token580 token581 token582 token583 token584 token585 token586 token587 token588 token589 token590 token591 token592 token593 token594 token595 token596 token597 token598 token599 token600 token601 token602 token603 token604 token605 token606 token607 token608 token609 token610 token611 token612 token613 token614 token615 token616 token617 token618 token619 token620 token621 token622 token623 token624 token625 token626 token627 token628 token629 token630 token631 token632 token633 token634 token635 token636 token637 token638 token639 token640 token641 token642 token643 token644 token645 token646 token647 token648 token649 token650 token651 token652 token653 token654 token655 token656 token657 token658 token659 token660 token661 token662 token663 token664 token665 token666 token667 token668 token669 token670 token671 token672 token673 token674 token675 token676 token677 token678 token679 token680 token681 token682 token683 token684 token685 token686 token687 token688 token689 token690 token691 token692 token693 token694 token695 token696 token697 token698 token699 token700 token701 token702 token703 token704 token705 token706 token707 token708 token709 token710 token711 token712 token713 token714 token715 token716 token717 token718 token719 token720 token721 token722 token723 token724 token725 token726 token727 token728 token729 token730 token731 token732 token733 token734 token735 token736 token737 token738 token739 token740 token741 token742 token743 token744 token745 token746 token747 token748 token749 token750 token751 token752 token753 token754 token755 token756 token757 token758 token759 token760 token761 token762 token763 token764 token765 token766 token767 token768 token769 token770 token771 token772 token773 token774 token775 token776 token777 token778 token779 token780 token781 token782 token783 token784 token785 token786 token787 token788 token789 token790 token791 token792 token793 token794 token795 token796 token797 token798 token799 token800 token801 token802 token803 token804 token805 token806 token807 token808 token809 token810 token811 token812 token813 token814 token815 token816 token817 token818 token819 token820 token821 token822 token823 token824 token825 token826 token827 token828 token829 token830 token831 token832 token833 token834 token835 token836 token837 token838 token839 token840 token841 token842 token843 token844 token845 token846 token847 token848 token849 token850 token851 token852 token853 token854 token855 token856 token857 token858 token859 token860 token861 token862 token863 token864 token865 token866 token867 token868 token869 token870 token871 token872 token873 token874 token875 token876 token877 token878 token879 token880 token881 token882 token883 token884 token885 token886 token887 token888 token889 token890 token891 token892 token893 token894 token895 token896 token897 token898 token899 token900 token901 token902 token903 token904 token905 token906 token907 token908 token909 token910 token911 token912 token913 token914 token915 token916 token917 token918 token919 token920 token921 token922 token923 token924 token925 token926 token927 token928 token929 token930 token931 token932 token933 token934 token935 token936 token937 token938 token939 token940 token941 token942 token943 token944 token945 token946 token947 token948 token949 token950 token951 token952 token953 token954 token955 token956 token957 token958 token959 token960 token961 token962 token963 token964 token965 token966 token967 token968 token969 token970 token971 token972 token973 token974 token975 token976 token977 token978 token979 token980 token981 token982 token983 token984 token985 token986 token987 token988 token989 token990 token991 token992 token993 token994 token995 token996 token997 token998 token999 token1000 token1001 token1002 token1003 token1004 token1005 token1006 token1007 token1008 token1009 token1010 token1011 token1012 token1013 token1014 token1015 token1016 token1017 token1018 token1019 token1020 token1021 token1022 token1023 token1024 token1025 token1026 token1027 token1028 token1029 token1030 token1031 token1032 token1033 token1034 token1035 token1036 token1037 token1038 token1039 token1040 token1041 token1042 token1043 token1044 token1045 token1046 token1047 token1048 token1049 token1050 token1051 token1052 token1053 token1054 token1055 token1056 token1057 token1058 token1059 token1060 token1061 token1062 token1063 token1064 token1065 token1066 token1067 token1068 token1069 token1070 token1071 token1072 token1073 token1074 token1075 token1076 token1077 token1078 token1079 token1080 token1081 token1082 token1083 token1084 token1085 token1086 token1087 token1088 token1089 token1090 token1091 token1092 token1093 token1094 token1095 token1096 token1097 token1098 token1099 token1100 token1101 token1102 token1103 token1104 token1105 token1106 token1107 token1108 token1109 token1110 token1111 token1112 token1113 token1114 token1115
  - form "Message":
    - textbox "Message fake-chat":
      - /placeholder: Message fake-chat…
    - button "Add attachment"
    - button "Web search": Search
    - button "Create image": Image
    - button "Library" [disabled]
    - button "Choose Library collections"
    - img "21 of 16,384 total tokens; 12,032 input allowance; 4,096 reserved for response; 256 safety margin"
    - button "Stop generating"
- region "Notifications alt+T"
```

# Test source

```ts
  22  |       await page.setViewportSize({ width, height: width < 640 ? 844 : 900 });
  23  |       await page.addInitScript(
  24  |         (value) => localStorage.setItem("workbench-theme", value),
  25  |         theme,
  26  |       );
  27  |       await send(page, "Hello from the browser");
  28  |       await expect(
  29  |         page.getByText("Fake runtime reply.", { exact: false }),
  30  |       ).toBeVisible();
  31  |       await expect(
  32  |         page.getByRole("button", { name: "Stop generating" }),
  33  |       ).not.toBeVisible();
  34  |       expect(
  35  |         await page.evaluate(
  36  |           () => document.documentElement.scrollWidth <= innerWidth,
  37  |         ),
  38  |       ).toBeTruthy();
  39  |       const thread = await page.getByTestId("thread").boundingBox(),
  40  |         composer = await page.getByTestId("composer-row").boundingBox();
  41  |       expect(thread!.y + thread!.height).toBeLessThanOrEqual(composer!.y + 1);
  42  |       await mkdir(dir, { recursive: true });
  43  |       await settle(page);
  44  |       await page.screenshot({
  45  |         path: `${dir}/chat-${width}-${theme}-fake-runtime.png`,
  46  |       });
  47  |       await settle(page);
  48  |       const result = await new AxeBuilder({ page }).analyze();
  49  |       expect(
  50  |         result.violations.filter((v) =>
  51  |           ["serious", "critical"].includes(v.impact ?? ""),
  52  |         ),
  53  |       ).toEqual([]);
  54  |       await page.reload();
  55  |       await expect(
  56  |         page
  57  |           .getByRole("article", { name: "user message" })
  58  |           .getByText("Hello from the browser", { exact: true }),
  59  |       ).toBeVisible();
  60  |     });
  61  | test("Stop persists partial text and closes runtime connection", async ({
  62  |   page,
  63  |   request,
  64  | }) => {
  65  |   const before = (
  66  |     await (await request.get("http://127.0.0.1:18080/tests/state")).json()
  67  |   ).disconnected;
  68  |   await send(page, "#long:500 #slow:50");
  69  |   await expect(page.getByText(/token0 token1/)).toBeVisible();
  70  |   await page.getByRole("button", { name: "Stop generating" }).click();
  71  |   await expect(
  72  |     page.locator(".meta").filter({ hasText: /stopped/i }),
  73  |   ).toBeVisible();
  74  |   await expect
  75  |     .poll(
  76  |       async () =>
  77  |         (await (await request.get("http://127.0.0.1:18080/tests/state")).json())
  78  |           .disconnected,
  79  |     )
  80  |     .toBeGreaterThan(before);
  81  |   const text = await page.locator(".prose-answer").innerText();
  82  |   await page.reload();
  83  |   await expect(page.locator(".prose-answer")).toHaveText(text);
  84  | });
  85  | test("close tab and reopen after 20 seconds resumes exactly", async ({
  86  |   page,
  87  |   context,
  88  |   request,
  89  | }) => {
  90  |   test.setTimeout(65000);
  91  |   await send(page, "#long:350 #slow:10");
  92  |   await expect(page.getByText(/token0 token1/)).toBeVisible();
  93  |   const url = page.url();
  94  |   await page.close();
  95  |   await new Promise((resolve) => setTimeout(resolve, 20000));
  96  |   const reopened = await context.newPage();
  97  |   await reopened.goto(url);
  98  |   await expect(
  99  |     reopened.getByRole("button", { name: "Stop generating" }),
  100 |   ).toBeVisible();
  101 |   await expect(
  102 |     reopened.getByRole("button", { name: "Stop generating" }),
  103 |   ).not.toBeVisible({ timeout: 25000 });
  104 |   const data = await (
  105 |     await request.get("/api/chats/" + url.split("/").pop())
  106 |   ).json();
  107 |   expect(await reopened.locator(".prose-answer").innerText()).toBe(
  108 |     data.messages.findLast((m: { role: string }) => m.role === "assistant")
  109 |       .content,
  110 |   );
  111 | });
  112 | test("long answer completes beyond 90 seconds; idle timeout keeps partial", async ({
  113 |   page,
  114 |   request,
  115 | }) => {
  116 |   test.skip(
  117 |     test.info().project.name !== "chromium",
  118 |     "Run the real-time timeout gate once",
  119 |   );
  120 |   test.setTimeout(240000);
  121 |   await send(page, "#long:1500 #slow:10");
> 122 |   await expect(page.getByText(/token1499/)).toBeVisible({ timeout: 180000 });
      |                                             ^ Error: expect(locator).toBeVisible() failed
  123 |   await expect(
  124 |     page.getByRole("button", { name: "Stop generating" }),
  125 |   ).not.toBeVisible();
  126 |   const url = page.url();
  127 |   const data = await (
  128 |     await request.get("/api/chats/" + url.split("/").pop())
  129 |   ).json();
  130 |   expect(
  131 |     data.messages.findLast((m: { role: string }) => m.role === "assistant")
  132 |       .status,
  133 |   ).toBe("complete");
  134 |   expect(
  135 |     data.messages.findLast((m: { role: string }) => m.role === "assistant")
  136 |       .stats.total_ms,
  137 |   ).toBeGreaterThan(150000);
  138 |   await send(page, "#stall:70");
  139 |   await expect(
  140 |     page.getByText("The model stopped responding. The partial answer is kept."),
  141 |   ).toBeVisible({ timeout: 75000 });
  142 |   const id = page.url().split("/").pop();
  143 |   const error = await (await request.get("/api/chats/" + id)).json();
  144 |   expect(
  145 |     error.messages.findLast((m: { role: string }) => m.role === "assistant")
  146 |       .error.code,
  147 |   ).toBe("idle_timeout");
  148 |   expect(
  149 |     error.messages.findLast((m: { role: string }) => m.role === "assistant")
  150 |       .content.length,
  151 |   ).toBeGreaterThan(0);
  152 | });
  153 | test("100 tokens/s render frame trace", async ({ page }) => {
  154 |   const cdp =
  155 |     test.info().project.name === "chromium"
  156 |       ? await page.context().newCDPSession(page)
  157 |       : null;
  158 |   if (cdp)
  159 |     await cdp.send("Tracing.start", {
  160 |       categories: "devtools.timeline,blink.user_timing",
  161 |       transferMode: "ReturnAsStream",
  162 |     });
  163 |   await page.addInitScript(() => {
  164 |     const times: number[] = [];
  165 |     (window as unknown as { frames: number[] }).frames = times;
  166 |     let previous = performance.now();
  167 |     const frame = (now: number) => {
  168 |       times.push(now - previous);
  169 |       previous = now;
  170 |       requestAnimationFrame(frame);
  171 |     };
  172 |     requestAnimationFrame(frame);
  173 |   });
  174 |   await send(page, "#long:300 #slow:100");
  175 |   await expect(page.getByText(/token0 token1/)).toBeVisible();
  176 |   await page.evaluate(() => {
  177 |     (window as unknown as { frames: number[] }).frames.length = 0;
  178 |   });
  179 |   await expect(page.getByText(/token299/)).toBeVisible();
  180 |   const times = await page.evaluate(
  181 |     () => (window as unknown as { frames: number[] }).frames,
  182 |   );
  183 |   await mkdir(dir, { recursive: true });
  184 |   await writeFile(
  185 |     `${dir}/frames-${test.info().project.name}.json`,
  186 |     JSON.stringify(times),
  187 |   );
  188 |   if (cdp) {
  189 |     const finished = new Promise<string>((resolve, reject) =>
  190 |       cdp.once("Tracing.tracingComplete", (event) =>
  191 |         event.stream
  192 |           ? resolve(event.stream)
  193 |           : reject(new Error("Chrome trace stream missing")),
  194 |       ),
  195 |     );
  196 |     await cdp.send("Tracing.end");
  197 |     const handle = await finished;
  198 |     let trace = "";
  199 |     for (;;) {
  200 |       const part = await cdp.send("IO.read", { handle });
  201 |       trace += part.data;
  202 |       if (part.eof) break;
  203 |     }
  204 |     await cdp.send("IO.close", { handle });
  205 |     await writeFile(`${dir}/streaming-chromium-trace.json.gz`, gzipSync(trace));
  206 |   }
  207 |   const sorted = times.filter((n) => n < 100).sort((a, b) => a - b);
  208 |   expect(sorted[Math.floor(sorted.length * 0.5)]).toBeLessThan(20);
  209 | });
  210 | 
  211 | test("first-token render delay under 150ms", async ({ page, request }) => {
  212 |   await page.addInitScript(() => {
  213 |     const listener = new MutationObserver(() => {
  214 |       if (
  215 |         document
  216 |           .querySelector('[aria-label="assistant message"] .prose-answer')
  217 |           ?.textContent?.includes("Fake")
  218 |       ) {
  219 |         (window as unknown as { firstRendered: number }).firstRendered =
  220 |           performance.timeOrigin + performance.now();
  221 |         listener.disconnect();
  222 |       }
```
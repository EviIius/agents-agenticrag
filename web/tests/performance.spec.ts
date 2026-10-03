import { test, expect } from "@playwright/test";
import { writeFile, mkdir } from "node:fs/promises";
test("300 messages scroll and only the streaming row renders at 100 tokens per second", async ({
  page,
  request,
}) => {
  const connection = (await (await request.get("/api/connections")).json())[0];
  const chat = await (
    await request.post("/api/chats", {
      data: { connection_id: connection.id, model_id: "fake-chat" },
    })
  ).json();
  try {
    expect(
      (
        await request.post(`http://127.0.0.1:8787/tests/long-chat/${chat.id}`)
      ).ok(),
    ).toBe(true);
    await page.addInitScript(() => {
      const records: { id: string; phase: string; actualDuration: number }[] =
        [];
      (window as unknown as { renderRecords: typeof records }).renderRecords =
        records;
      window.addEventListener("workbench:message-render", (event) =>
        records.push((event as CustomEvent).detail),
      );
    });
    await page.goto(`/c/${chat.id}`);
    await expect(page.getByRole("article")).toHaveCount(300);
    await expect(
      page.getByText("Fake history item 299. Synthetic."),
    ).toBeVisible();
    const frames = await page.evaluate(async () => {
      const scroller = document.querySelector('[data-testid="thread"]')!;
      const times: number[] = [];
      let previous = 0;
      for (let i = 0; i < 120; i++)
        await new Promise<void>((resolve) =>
          requestAnimationFrame((now) => {
            if (previous) times.push(now - previous);
            previous = now;
            scroller.scrollTop =
              (scroller.scrollHeight - scroller.clientHeight) * (1 - i / 119);
            resolve();
          }),
        );
      return times;
    });
    await page.locator(".composer textarea").fill("#long:300 #slow:100");
    await page
      .getByRole("button", { name: "Send message", exact: true })
      .click();
    await expect(page.getByText(/token0 token1/)).toBeVisible();
    await page.evaluate(() => {
      (window as unknown as { renderRecords: unknown[] }).renderRecords.length =
        0;
    });
    await expect(page.getByText(/token249/)).toBeVisible();
    const records = await page.evaluate(
      () =>
        (
          window as unknown as {
            renderRecords: { id: string; actualDuration: number }[];
          }
        ).renderRecords,
    );
    await expect(page.getByText(/token299/)).toBeVisible();
    const byId: Record<string, number> = {};
    for (const row of records) byId[row.id] = (byId[row.id] ?? 0) + 1;
    const times = records
      .map((row) => row.actualDuration)
      .sort((a, b) => a - b);
    const sortedFrames = [...frames].sort((a, b) => a - b);
    const report = {
      history_messages: 300,
      tokens_per_second: 100,
      render_samples: times.length,
      render_p95_ms: times[Math.floor(times.length * 0.95)],
      render_max_ms: times.at(-1),
      rendered_rows: byId,
      scroll_samples: frames.length,
      scroll_median_ms: sortedFrames[Math.floor(frames.length * 0.5)],
      scroll_p95_ms: sortedFrames[Math.floor(frames.length * 0.95)],
    };
    await mkdir("../artifacts/phase-3", { recursive: true });
    await writeFile(
      `../artifacts/phase-3/performance-${test.info().project.name}.json`,
      JSON.stringify(report, null, 2),
    );
    expect(times.length).toBeGreaterThan(50);
    expect(Object.keys(byId)).toHaveLength(1);
    expect(report.render_p95_ms).toBeLessThanOrEqual(8);
    expect(report.scroll_median_ms).toBeLessThan(20);
  } finally {
    await request.delete(`/api/chats/${chat.id}`);
  }
});

// Synthetic fixture endpoints only. Never run this against a production runtime.
import { writeFile } from "node:fs/promises";
const app = "http://127.0.0.1:8787/api";
const connection = (await (await fetch(app + "/connections")).json())[0];
if (connection.name !== "Fake runtime")
  throw new Error("This measurement requires the isolated fake server.");
const first = async (response, sse) => {
  if (!response.ok)
    throw new Error(`Synthetic measurement failed: ${response.status}`);
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  try {
    for (;;) {
      const { value, done } = await reader.read();
      if (done) throw new Error("No first token");
      buffer += decoder.decode(value, { stream: true });
      if (
        sse
          ? buffer.includes("event: text.delta")
          : buffer.split("\n").some((line) => {
              try {
                return JSON.parse(line).message?.content;
              } catch {
                return false;
              }
            })
      )
        return;
    }
  } finally {
    await reader.cancel();
  }
};
const samples = [];
for (let i = 0; i < 5; i++) {
  const prompt = `Synthetic Phase 3 latency sample ${i}`;
  const began = performance.now();
  await first(
    await fetch("http://127.0.0.1:18080/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "fake-chat",
        messages: [{ role: "user", content: prompt }],
        stream: true,
      }),
    }),
    false,
  );
  const raw = performance.now() - began;
  const chat = await (
    await fetch(app + "/chats", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        connection_id: connection.id,
        model_id: "fake-chat",
        web_enabled: false,
      }),
    })
  ).json();
  try {
    const start = performance.now();
    const run = await (
      await fetch(`${app}/chats/${chat.id}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: prompt, web: false }),
      })
    ).json();
    await first(await fetch(`${app}/runs/${run.run_id}/events`), true);
    samples.push({
      raw_ms: raw,
      app_ms: performance.now() - start,
      overhead_ms: performance.now() - start - raw,
    });
  } finally {
    await fetch(`${app}/chats/${chat.id}`, { method: "DELETE" });
  }
}
const sorted = samples.map((row) => row.overhead_ms).sort((a, b) => a - b);
await writeFile(
  "../artifacts/phase-3/ttft-overhead.json",
  JSON.stringify(
    {
      method:
        "paired local HTTP first-token latency; five synthetic raw Ollama versus app SSE requests; no web search; excludes browser rendering",
      samples,
      median_overhead_ms: sorted[2],
      max_overhead_ms: sorted.at(-1),
      budget_ms: 150,
    },
    null,
    2,
  ),
);
if (sorted.at(-1) > 150)
  throw new Error("First-token overhead budget exceeded");

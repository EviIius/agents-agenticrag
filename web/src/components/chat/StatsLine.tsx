import type { Message } from "@/lib/api";
export function StatsLine({ message }: { message: Message }) {
  const s = message.stats;
  if (!s)
    return message.status === "stopped" ? (
      <p className="meta">Stopped</p>
    ) : null;
  return (
    <p className="meta break-words">
      {message.model?.display_name} · {s.tokens_estimated ? "≈" : ""}
      {s.tokens_per_sec.toFixed(1)} tok/s · {s.completion_tokens} tokens ·{" "}
      {((s.ttft_ms ?? 0) / 1000).toFixed(1)}s to first token
      {s.finish_reason !== "stop"
        ? ` · ${s.finish_reason === "length" ? "Output limit reached" : s.finish_reason === "stopped" ? "Stopped" : s.finish_reason}`
        : ""}
    </p>
  );
}

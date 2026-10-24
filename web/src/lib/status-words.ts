import type { Message } from "./api";

export const STATUS_WORDS = [
  "Spelunking",
  "Pondering",
  "Mulling",
  "Percolating",
  "Noodling",
  "Tinkering",
  "Musing",
  "Ruminating",
  "Brewing",
  "Simmering",
  "Untangling",
  "Sketching",
  "Priming the canvas",
  "Mixing pigments",
  "Stretching canvas",
  "Blocking in shapes",
  "Sharpening pencils",
  "Composing",
  "Framing",
  "Underpainting",
  "Glazing",
  "Shading",
  "Drafting",
  "Whittling",
  "Weaving",
  "Distilling",
  "Marinating",
  "Assembling",
  "Calibrating",
  "Deliberating",
  "Contemplating",
  "Puzzling",
  "Conjuring",
  "Doodling",
  "Polishing",
  "Rummaging",
] as const;

/** A stable shuffle per message. `list` is the palette's own words (TH2). */
export function statusSequence(
  id: string,
  list: readonly string[] = STATUS_WORDS,
): string[] {
  let seed = 2166136261;
  for (const char of id) seed = Math.imul(seed ^ char.charCodeAt(0), 16777619);
  const words: string[] = [...list];
  for (let i = words.length - 1; i > 0; i--) {
    seed += 0x6d2b79f5;
    let value = Math.imul(seed ^ (seed >>> 15), seed | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    const j = Math.floor(
      (((value ^ (value >>> 14)) >>> 0) / 4294967296) * (i + 1),
    );
    [words[i], words[j]] = [words[j], words[i]];
  }
  return words;
}

export function thoughtTail(text: string): string {
  const compact = text.trimEnd().slice(-400).replace(/\s+/g, " ").trim();
  if (compact.length <= 160) return compact;
  const tail = compact.slice(-160);
  const boundary = tail.indexOf(" ");
  return boundary >= 0 ? tail.slice(boundary + 1) : tail;
}

export type WorkingPhase = {
  kind: "queued" | "loading" | "search" | "working" | "thinking";
  label: string;
  announcement: string;
};
export type SearchStep = { label: string; detail: string; status: string };

export function workingPhase(
  message: Pick<
    Message,
    "status" | "content" | "reasoning" | "model" | "library"
  >,
  stage?: string,
  steps: SearchStep[] = [],
  position?: number,
): WorkingPhase | null {
  if (message.status !== "streaming" || message.content) return null;
  const model =
    message.model?.display_name || message.model?.model_id || "model";
  if (stage === "queued")
    return {
      kind: "queued",
      label: `Waiting for ${model}${position ? ` · #${position} in line` : ""}`,
      announcement: `Waiting for ${model}`,
    };
  if (stage === "loading-model")
    return {
      kind: "loading",
      label: `Loading ${model}…`,
      announcement: `Loading ${model}`,
    };
  if (stage === "search") {
    const library = !!message.library;
    let label = library ? "Searching your files" : "Searching the web";
    const latest = steps.at(-1);
    if (!library && latest?.label === "planning") label = "Planning the search";
    if (!library && ["reading", "read"].includes(latest?.label ?? "")) {
      const started = new Set(
        steps
          .filter((s) => s.label === "reading" && s.detail)
          .map((s) => s.detail),
      );
      const finished = new Set(
        steps
          .filter((s) => s.label === "read" && s.detail)
          .map((s) => s.detail),
      );
      const active = [...started].filter((url) => !finished.has(url)).length;
      const readable = new Set(
        steps
          .filter(
            (s) => s.label === "read" && s.status !== "failed" && s.detail,
          )
          .map((s) => s.detail),
      );
      if (active) label = `Reading ${active} page${active === 1 ? "" : "s"}`;
      else if (readable.size)
        label = `Read ${readable.size} page${readable.size === 1 ? "" : "s"}`;
      else if (finished.size) label = "Pages couldn't be read";
    }
    return {
      kind: "search",
      label,
      announcement: library ? "Searching your files" : "Searching the web",
    };
  }
  if (message.reasoning)
    return { kind: "thinking", label: "Thinking", announcement: "Thinking" };
  return { kind: "working", label: "Working", announcement: "Working" };
}

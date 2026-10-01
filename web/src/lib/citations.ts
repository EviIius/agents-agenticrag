import type { Source } from "./api";
const code = /(```[\s\S]*?(?:```|$)|`[^`\n]*`)/g;
export function outsideCode(text: string, transform: (t: string) => string) {
  return text
    .split(code)
    .map((p, i) => (i % 2 ? p : transform(p)))
    .join("");
}
export function cited(text: string): Set<number> {
  const ids = new Set<number>();
  outsideCode(text, (part) => {
    for (const match of part.matchAll(/\[(\d+)\](?!\()/g))
      ids.add(Number(match[1]));
    return part;
  });
  return ids;
}
export function normalize(text: string, n: number) {
  return outsideCode(text, (t) => {
    t = t
      .replace(/【(\d+)(?:†[^】]*)?】/g, "[$1]")
      .replace(/\[\^(\d+)\]/g, "[$1]")
      .replace(/\[(?:source|src|s)\s*:?\s*(\d+)\]/gi, "[$1]")
      .replace(/\((?:source|src)\s*:?\s*(\d+)\)/gi, "[$1]")
      .replace(/\[(\d+(?:\s*[,;]\s*\d+)+)\]/g, (_, s: string) =>
        s
          .split(/[,;]/)
          .map((v) => `[${v.trim()}]`)
          .join(""),
      )
      .replace(/\[(\d+)\s*[-–]\s*(\d+)\]/g, (all, a: string, b: string) =>
        +b - +a >= 0 && +b - +a <= 9
          ? Array.from({ length: +b - +a + 1 }, (_, i) => `[${+a + i}]`).join(
              "",
            )
          : all,
      )
      .replace(/\s?\[(\d+)\](?!\()/g, (all, id: string) =>
        +id >= 1 && +id <= n ? all : "",
      );
    for (;;) {
      const next = t.replace(/\[(\d+)\]\[\1\](?!\()/g, "[$1]");
      if (next === t) return t;
      t = next;
    }
  });
}
export function renderCitations(text: string, n: number) {
  return outsideCode(normalize(text, n), (t) =>
    t.replace(
      /(?:\[\d+\](?!\())+/g,
      (group) =>
        `[cite](#cite-${[...group.matchAll(/\[(\d+)\]/g)].map((m) => m[1]).join("-")})`,
    ),
  );
}
const stop = new Set(
  "a an and are as at be by for from has have how in is it its of on or that the this to was were what when where which who why will with did does do about into than then there their they".split(
    " ",
  ),
);
function words(text: string) {
  return new Set(
    (text.toLowerCase().match(/[a-z0-9]+/g) ?? []).filter(
      (w) => w.length >= 3 && !stop.has(w),
    ),
  );
}
export function bestPassage(source: Source, sentence: string) {
  const query = words(sentence);
  let best = source.passages[0]?.text ?? "",
    top = -1;
  for (const p of source.passages) {
    const tokens = words(p.text),
      score =
        [...query].filter((w) => tokens.has(w)).length /
        Math.sqrt(p.text.length || 1);
    if (score > top) {
      top = score;
      best = p.text;
    }
  }
  return best.length > 280 ? best.slice(0, 279) + "…" : best;
}

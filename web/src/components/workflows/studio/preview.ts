import type { Block, Doc, Run } from "./types";
import { references } from "./graph";
const escape = (v: string) =>
  v
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#x27;");
export function renderPreview(
  text: string,
  values: Record<string, Record<string, unknown>>,
  skipped = new Set<string>(),
): string {
  references(text);
  if (text.includes("\0"))
    throw new Error("Text cannot contain null characters.");
  const marker = "\0EMPTY_TAG\0";
  let result = text.replace(/(?<!\\)\{\{(.*?)\}\}/gs, (whole: string) => {
    const ref = references(whole)[0];
    let value: unknown;
    if (skipped.has(ref.key)) value = "";
    else if (!(ref.key in values) || !(ref.field in values[ref.key]))
      throw new Error(
        `Run once or set an input default to preview ${ref.key}.${ref.field}.`,
      );
    else value = values[ref.key][ref.field];
    const literal =
      typeof value === "string"
        ? value
        : value == null
          ? ""
          : JSON.stringify(value);
    if (literal.includes("\0"))
      throw new Error("Text cannot contain null characters.");
    return ref.tag
      ? literal
        ? `<${ref.tag}>\n${escape(literal)}\n</${ref.tag}>`
        : marker
      : literal;
  });
  const quoted = marker.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  result = result
    .replace(new RegExp(`^(?:[ \\t]*${quoted}[ \\t]*\\n)+`), "")
    .replace(new RegExp(`(?:\\n)?[ \\t]*${quoted}[ \\t]*(?=\\n|$)`, "g"), "");
  return result.replaceAll(marker, "").replaceAll("\\{{", "{{");
}
export function promptPreview(
  doc: Doc,
  node: Extract<Block, { kind: "generate" }>,
  latest?: Run,
) {
  const values = Object.fromEntries(
    doc.nodes.map((n) => [
      n.key,
      n.kind === "start"
        ? {
            ...Object.fromEntries(
              n.config.fields
                .filter((f) => f.default != null)
                .map((f) => [f.name, f.default]),
            ),
            ...(latest?.inputs ?? {}),
          }
        : (latest?.nodes[n.id]?.output ?? {}),
    ]),
  );
  const skipped = new Set(
    doc.nodes
      .filter((n) => n.disabled || latest?.nodes[n.id]?.state === "skipped")
      .map((n) => n.key),
  );
  const system = renderPreview(node.config.instructions, values, skipped),
    user = renderPreview(node.config.prompt, values, skipped);
  return [
    ...(system ? [{ role: "system", content: system }] : []),
    { role: "user", content: user },
  ];
}

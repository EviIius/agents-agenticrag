import type { Message } from "./api";
export function visiblePath(
  messages: Message[],
  leaf: string | null,
): Message[] {
  const byId = new Map(messages.map((m) => [m.id, m]));
  const out: Message[] = [];
  const seen = new Set<string>();
  while (leaf && byId.has(leaf) && !seen.has(leaf)) {
    seen.add(leaf);
    const m = byId.get(leaf)!;
    out.push(m);
    leaf = m.parent_id ?? null;
  }
  return out.reverse();
}
export function siblings(messages: Message[], message: Message): Message[] {
  return messages
    .filter((m) => m.parent_id === message.parent_id && m.role === message.role)
    .sort(
      (a, b) =>
        a.created_at.localeCompare(b.created_at) || a.id.localeCompare(b.id),
    );
}
export function latestLeaf(messages: Message[], root: string): string {
  const seen = new Set<string>();
  while (!seen.has(root)) {
    seen.add(root);
    const children = messages
      .filter((m) => m.parent_id === root)
      .sort(
        (a, b) =>
          b.created_at.localeCompare(a.created_at) || b.id.localeCompare(a.id),
      );
    if (!children.length) break;
    root = children[0]!.id;
  }
  return root;
}

import type { Block, Doc, Edge, Issue, Kind, Point } from "./types";
import { defaults, outputs, ports, registry } from "./registry";
export const newId = (prefix = "n") =>
  prefix + "_" + crypto.randomUUID().replaceAll("-", "").slice(0, 12);
export const clone = <T>(value: T): T => structuredClone(value);
export function ancestors(doc: Doc, id: string): Set<string> {
  const seen = new Set<string>();
  let changed = true;
  while (changed) {
    changed = false;
    for (const edge of doc.edges)
      if (
        (edge.target === id || seen.has(edge.target)) &&
        !seen.has(edge.source)
      ) {
        seen.add(edge.source);
        changed = true;
      }
  }
  return seen;
}
export function topoOrder(doc: Doc): string[] {
  const remaining = new Set(doc.nodes.map((n) => n.id));
  const result: string[] = [];
  while (remaining.size) {
    const ready = [...remaining]
      .filter(
        (id) =>
          !doc.edges.some((e) => e.target === id && remaining.has(e.source)),
      )
      .sort();
    if (!ready.length) throw new Error("Workflow connections contain a cycle");
    result.push(...ready);
    ready.forEach((id) => remaining.delete(id));
  }
  return result;
}
const token = /(?<!\\)\{\{(.*?)\}\}/gs;
const grammar =
  /^\s*([a-z][a-z0-9_]{0,31})\.([a-z][a-z0-9_]{0,31})(?:\s*\|\s*tagged:([a-z][a-z0-9_]{0,31}))?\s*$/;
export function references(text: string) {
  if (
    text
      .replace(/\\\{\{/g, "")
      .replace(token, "")
      .includes("{{")
  )
    throw new Error("Unclosed reference");
  return [...text.matchAll(token)].map((m) => {
    const r = grammar.exec(m[1]);
    if (!r) throw new Error("Invalid reference");
    return { key: r[1], field: r[2], tag: r[3], literal: m[0] };
  });
}
export function fields(node: Block): [string, boolean][] {
  switch (node.kind) {
    case "generate":
      return [
        [node.config.instructions, false],
        [node.config.prompt, false],
      ];
    case "transcribe":
      return [[node.config.recording, true]];
    case "clean_transcript":
      return [[node.config.transcript, true]];
    case "generate_image":
      return [[node.config.prompt, false]];
    case "review":
      return [[node.config.show, false]];
    case "output":
      return node.config.include.map((i) => [i.ref, true]);
    default:
      return [];
  }
}
export function validate(doc: Doc): Issue[] {
  const issues: Issue[] = [];
  const add = (
    code: string,
    message: string,
    node_id: string | null = null,
    severity: Issue["severity"] = "error",
  ) => issues.push({ code, message, node_id, severity });
  const ids = doc.nodes.map((n) => n.id),
    keys = doc.nodes.map((n) => n.key);
  if (new Set(ids).size !== ids.length || new Set(keys).size !== keys.length)
    add("duplicate", "Each block needs its own ID and reference name.");
  if (
    new Set(doc.edges.map((e) => e.id)).size !== doc.edges.length ||
    new Set(doc.notes.map((n) => n.id)).size !== doc.notes.length
  )
    add("duplicate", "Connection and note IDs must be unique.");
  const starts = doc.nodes.filter((n) => n.kind === "start");
  if (starts.length !== 1 || starts[0].disabled)
    add("start", "Keep exactly one enabled Start block.");
  const byId = new Map(doc.nodes.map((n) => [n.id, n]));
  if (
    new Set(
      doc.edges.map((e) => JSON.stringify([e.source, e.source_port, e.target])),
    ).size !== doc.edges.length
  )
    add(
      "duplicate_connection",
      "Keep one connection per output-to-input pair.",
    );
  for (const e of doc.edges) {
    const source = byId.get(e.source),
      target = byId.get(e.target);
    if (!source || !target) {
      add("edge", "A connection points to a missing block.");
      continue;
    }
    if (target.kind === "start")
      add("edge", "Start cannot have an incoming connection.", target.id);
    if (!ports(source).includes(e.source_port))
      add("port", "Choose an output port offered by this block.", source.id);
  }
  try {
    topoOrder(doc);
  } catch {
    add("cycle", "Connections cannot lead back to an earlier block.");
  }
  if (
    doc.nodes.reduce(
      (total, n) => total + (n.kind === "generate_image" ? n.config.count : 0),
      0,
    ) > 12
  )
    add("images", "Use at most 12 images per run.");
  const byKey = new Map(doc.nodes.map((n) => [n.key, n]));
  for (const node of doc.nodes) {
    if (node.kind !== "start" && !doc.edges.some((e) => e.target === node.id))
      add("disconnected", "Connect this block to Start.", node.id);
    if (
      node.kind === "start" &&
      new Set(node.config.fields.map((f) => f.name)).size !==
        node.config.fields.length
    )
      add("duplicate_field", "Start input names must be unique.", node.id);
    if (node.kind === "generate") {
      const names = node.config.json_fields.map((f) => f.name);
      if (
        node.config.format === "json" &&
        (!names.length ||
          names.includes("text") ||
          new Set(names).size !== names.length)
      )
        add(
          "json_fields",
          "Choose unique JSON fields apart from the reserved text output.",
          node.id,
        );
      if (node.config.format !== "json" && names.length)
        add(
          "json_fields",
          "Choose JSON output before adding JSON fields.",
          node.id,
        );
    }
    if (
      !node.disabled &&
      (node.kind === "generate" ||
        node.kind === "generate_image" ||
        node.kind === "review")
    ) {
      const text =
        node.kind === "review" ? node.config.show : node.config.prompt;
      if (!text.trim())
        add(
          "required_setting",
          "Add the required text for this block.",
          node.id,
        );
    }
    for (const [text, typed] of fields(node)) {
      let refs: ReturnType<typeof references>;
      try {
        refs = references(text);
      } catch {
        add(
          "reference_syntax",
          "Use {{block.field}} references or the tagged filter.",
          node.id,
        );
        continue;
      }
      if (
        typed &&
        (refs.length !== 1 || refs[0].literal !== text.trim() || refs[0].tag)
      )
        add("reference_type", "Choose one typed output reference.", node.id);
      for (const ref of refs) {
        const source = byKey.get(ref.key);
        if (!source || !(ref.field in outputs(source)))
          add("reference", "A referenced output does not exist.", node.id);
        else if (!ancestors(doc, node.id).has(source.id))
          add(
            "reference_order",
            "Connect the referenced block upstream first.",
            node.id,
          );
        else if (
          !typed &&
          [
            "recording",
            "document",
            "image",
            "image_list",
            "transcript",
          ].includes(outputs(source)[ref.field])
        )
          add(
            "reference_type",
            "Use a text field rather than a file or media reference.",
            node.id,
          );
        else if (typed) {
          const expected =
            node.kind === "transcribe"
              ? "recording"
              : node.kind === "clean_transcript"
                ? "transcript"
                : null;
          if (expected && outputs(source)[ref.field] !== expected)
            add(
              "reference_type",
              "Choose an output of the required file type.",
              node.id,
            );
        }
        if (source?.disabled && !ref.tag)
          add(
            "empty_reference",
            "This output is empty while its block is disabled.",
            node.id,
            "warning",
          );
      }
    }
    if (node.disabled)
      add("disabled", "This block is skipped while disabled.", node.id, "info");
    if (node.kind === "review")
      for (const port of ["approved", "rejected"])
        if (
          !doc.edges.some((e) => e.source === node.id && e.source_port === port)
        )
          add("branch_ends", `The ${port} path ends here.`, node.id, "warning");
  }
  if (!doc.nodes.some((n) => n.kind === "output" && !n.disabled))
    add("no_results", "This workflow does not save anything.", null, "warning");
  return issues;
}
export function canConnect(
  doc: Doc,
  source: string,
  target: string,
  source_port = "out",
): boolean {
  const s = doc.nodes.find((n) => n.id === source),
    t = doc.nodes.find((n) => n.id === target);
  if (
    !s ||
    !t ||
    source === target ||
    t.kind === "start" ||
    !ports(s).includes(source_port) ||
    doc.edges.some(
      (e) =>
        e.source === source &&
        e.source_port === source_port &&
        e.target === target,
    ) ||
    ancestors(doc, source).has(target)
  )
    return false;
  if (t.kind === "transcribe" || t.kind === "clean_transcript") {
    const expected = t.kind === "transcribe" ? "recording" : "transcript";
    const upstream = new Set([source, ...ancestors(doc, source)]);
    if (
      !doc.nodes.some(
        (n) =>
          upstream.has(n.id) && Object.values(outputs(n)).includes(expected),
      )
    )
      return false;
  }
  return true;
}
export function connect(
  doc: Doc,
  source: string,
  target: string,
  source_port = "out",
): Doc {
  if (!canConnect(doc, source, target, source_port)) return doc;
  return {
    ...doc,
    edges: [
      ...doc.edges,
      {
        id: newId("e"),
        source,
        target,
        source_port: source_port as Edge["source_port"],
        target_port: "in",
      },
    ],
  };
}
export function uniqueKey(key: string, existing: Set<string>) {
  const base = key.replace(/[^a-z0-9_]/g, "_").slice(0, 27) || "block";
  let next = base;
  let i = 2;
  while (existing.has(next)) next = base + "_" + i++;
  return next;
}
export function rewrite<T>(value: T, names: Record<string, string>): T {
  if (typeof value === "string")
    return value.replace(token, (whole: string, body: string) => {
      const match = grammar.exec(body);
      return match && names[match[1]]
        ? whole.replace(match[1] + ".", names[match[1]] + ".")
        : whole;
    }) as T;
  if (Array.isArray(value)) return value.map((v) => rewrite(v, names)) as T;
  if (value && typeof value === "object")
    return Object.fromEntries(
      Object.entries(value).map(([k, v]) => [k, rewrite(v, names)]),
    ) as T;
  return value;
}
export function renameKey(doc: Doc, old: string, next: string): Doc {
  if (
    !/^[a-z][a-z0-9_]{0,31}$/.test(next) ||
    doc.nodes.some((n) => n.key === next && n.key !== old)
  )
    return doc;
  return {
    ...doc,
    nodes: doc.nodes.map(
      (n) =>
        ({
          ...n,
          key: n.key === old ? next : n.key,
          config: rewrite(n.config, { [old]: next }),
        }) as Block,
    ),
  };
}
export function pasteRemap(
  doc: Doc,
  fragment: Pick<Doc, "nodes" | "edges" | "notes">,
  point?: Point,
): Doc {
  const names: Record<string, string> = {},
    ids: Record<string, string> = {};
  const existing = new Set(doc.nodes.map((n) => n.key));
  for (const n of fragment.nodes) {
    if (n.kind === "start") continue;
    ids[n.id] = newId();
    names[n.key] = uniqueKey(n.key, existing);
    existing.add(names[n.key]);
  }
  if (doc.nodes.length + Object.keys(ids).length > 40) return doc;
  const min = {
    x: Math.min(
      ...fragment.nodes.map((n) => n.position.x),
      ...fragment.notes.map((n) => n.position.x),
    ),
    y: Math.min(
      ...fragment.nodes.map((n) => n.position.y),
      ...fragment.notes.map((n) => n.position.y),
    ),
  };
  const offset = point
    ? { x: point.x - min.x, y: point.y - min.y }
    : { x: 32, y: 32 };
  return {
    ...doc,
    nodes: [
      ...doc.nodes,
      ...fragment.nodes
        .filter((n) => ids[n.id])
        .map(
          (n) =>
            ({
              ...clone(n),
              id: ids[n.id],
              key: names[n.key],
              position: {
                x: n.position.x + offset.x,
                y: n.position.y + offset.y,
              },
              config: rewrite(n.config, names),
            }) as Block,
        ),
    ],
    edges: [
      ...doc.edges,
      ...fragment.edges
        .filter((e) => ids[e.source] && ids[e.target])
        .map((e) => ({
          ...e,
          id: newId("e"),
          source: ids[e.source],
          target: ids[e.target],
        })),
    ],
    notes: [
      ...doc.notes,
      ...fragment.notes.map((n) => ({
        ...clone(n),
        id: newId("note"),
        position: { x: n.position.x + offset.x, y: n.position.y + offset.y },
      })),
    ],
  };
}
export function remove(doc: Doc, selected: string[]): Doc {
  const ids = new Set(
    selected.filter(
      (id) => doc.nodes.find((n) => n.id === id)?.kind !== "start",
    ),
  );
  const heals: Edge[] = [];
  // Heal a whole selected straight segment, retaining the incoming branch port.
  for (const first of doc.edges.filter(
    (e) => !ids.has(e.source) && ids.has(e.target),
  )) {
    let at = first.target;
    const visited = new Set<string>();
    let target: string | undefined;
    while (ids.has(at) && !visited.has(at)) {
      visited.add(at);
      const incoming = doc.edges.filter((e) => e.target === at),
        outgoing = doc.edges.filter((e) => e.source === at);
      if (incoming.length !== 1 || outgoing.length !== 1) break;
      at = outgoing[0].target;
      if (!ids.has(at)) target = at;
    }
    if (target && target !== first.source)
      heals.push({ ...first, id: newId("e"), target });
  }
  const edges = doc.edges.filter(
    (e) => !ids.has(e.source) && !ids.has(e.target) && !ids.has(e.id),
  );
  for (const h of heals)
    if (
      !edges.some(
        (e) =>
          e.source === h.source &&
          e.source_port === h.source_port &&
          e.target === h.target,
      )
    )
      edges.push(h);
  return {
    ...doc,
    nodes: doc.nodes.filter((n) => !ids.has(n.id)),
    edges,
    notes: doc.notes.filter((n) => !ids.has(n.id)),
  };
}
export function addBlock(
  doc: Doc,
  kind: Kind,
  point: Point,
  selected?: string,
  insertEdge?: string,
): Doc {
  if (
    doc.nodes.length >= 40 ||
    (kind === "start" && doc.nodes.some((n) => n.kind === "start"))
  )
    return doc;
  const node = {
    id: newId(),
    kind,
    key: uniqueKey(kind, new Set(doc.nodes.map((n) => n.key))),
    title: registry[kind].label,
    position: {
      x: Math.round(point.x / 16) * 16,
      y: Math.round(point.y / 16) * 16,
    },
    disabled: false,
    config: defaults(kind),
  } as Block;
  let next = { ...doc, nodes: [...doc.nodes, node] };
  const edge = doc.edges.find((e) => e.id === insertEdge);
  const previous = edge?.source ?? selected;
  if (previous)
    next = connect(
      next,
      previous,
      node.id,
      edge?.source_port ?? ports(doc.nodes.find((n) => n.id === previous)!)[0],
    );
  if (edge && next.edges.some((e) => e.target === node.id)) {
    if (canConnect(next, node.id, edge.target, ports(node)[0])) {
      next = { ...next, edges: next.edges.filter((e) => e.id !== edge.id) };
      next = connect(next, node.id, edge.target, ports(node)[0]);
      const below = new Set([
        edge.target,
        ...next.nodes
          .filter((n) => ancestors(next, n.id).has(edge.target))
          .map((n) => n.id),
      ]);
      next = {
        ...next,
        nodes: next.nodes.map((n) =>
          below.has(n.id)
            ? { ...n, position: { ...n.position, y: n.position.y + 192 } }
            : n,
        ),
      };
    }
  }
  // Offer a useful reference without introducing hidden text or model defaults.
  const upstream = ancestors(next, node.id);
  const sources = next.nodes.filter((n) => upstream.has(n.id)).reverse();
  const want =
    kind === "transcribe"
      ? "recording"
      : kind === "clean_transcript"
        ? "transcript"
        : "text";
  const source = sources.find((n) =>
    Object.values(outputs(n)).some(
      (t) =>
        t === want ||
        (want === "text" && ["long_text", "short_text"].includes(t)),
    ),
  );
  if (source) {
    const field = Object.keys(outputs(source)).find(
      (f) =>
        outputs(source)[f] === want ||
        (want === "text" &&
          ["long_text", "short_text"].includes(outputs(source)[f])),
    )!;
    const ref = `{{${source.key}.${field}}}`;
    if (node.kind === "generate" || node.kind === "generate_image")
      node.config.prompt = ref;
    else if (node.kind === "transcribe") node.config.recording = ref;
    else if (node.kind === "clean_transcript") node.config.transcript = ref;
    else if (node.kind === "review") node.config.show = ref;
  }
  return next;
}
export function layout(doc: Doc): Doc {
  let order: string[];
  try {
    order = topoOrder(doc);
  } catch {
    return doc;
  }
  const levels = new Map<string, number>();
  for (const id of order)
    levels.set(
      id,
      Math.max(
        0,
        ...doc.edges
          .filter((e) => e.target === id)
          .map((e) => (levels.get(e.source) ?? 0) + 1),
      ),
    );
  const positions = new Map<string, Point>();
  const max = Math.max(0, ...levels.values());
  for (let level = 0; level <= max; level++) {
    const layer = order
      .filter((id) => levels.get(id) === level)
      .sort((a, b) => {
        const mean = (id: string) => {
          const ps = doc.edges
            .filter((e) => e.target === id)
            .map((e) => positions.get(e.source)?.x ?? 0);
          return ps.length ? ps.reduce((s, x) => s + x, 0) / ps.length : 0;
        };
        return mean(a) - mean(b) || a.localeCompare(b);
      });
    const parentXs = layer.flatMap((id) =>
      doc.edges
        .filter((e) => e.target === id)
        .map((e) => positions.get(e.source)?.x ?? 0),
    );
    const center = parentXs.length
      ? parentXs.reduce((s, x) => s + x, 0) / parentXs.length
      : 0;
    layer.forEach((id, i) =>
      positions.set(id, {
        x: center + (i - (layer.length - 1) / 2) * 352,
        y: level * 208,
      }),
    );
  }
  return {
    ...doc,
    nodes: doc.nodes.map((n) => ({ ...n, position: positions.get(n.id)! })),
    notes: doc.notes.map((note) => {
      const nearest = [...doc.nodes].sort(
        (a, b) =>
          Math.hypot(
            a.position.x - note.position.x,
            a.position.y - note.position.y,
          ) -
          Math.hypot(
            b.position.x - note.position.x,
            b.position.y - note.position.y,
          ),
      )[0];
      const at = nearest && positions.get(nearest.id);
      return at
        ? {
            ...note,
            position: {
              x: at.x + note.position.x - nearest.position.x,
              y: at.y + note.position.y - nearest.position.y,
            },
          }
        : note;
    }),
  };
}
export type OutlineEntry = {
  id: string;
  branches?: {
    label: string;
    edgeId?: string;
    source: string;
    port: string;
    entries: OutlineEntry[];
  }[];
  then?: boolean;
};
export function outlineTree(doc: Doc): OutlineEntry[] | null {
  let order: string[];
  try {
    order = topoOrder(doc);
  } catch {
    return null;
  }
  const start = doc.nodes.find((n) => n.kind === "start");
  if (!start) return null;
  const seen = new Set<string>();
  let invalid = false;
  const descend = (id: string, until?: string): OutlineEntry[] => {
    const entries: OutlineEntry[] = [];
    let at: string | undefined = id;
    while (at && at !== until) {
      if (seen.has(at)) {
        invalid = true;
        break;
      }
      seen.add(at);
      const node = doc.nodes.find((n) => n.id === at)!;
      const entry: OutlineEntry = { id: at };
      entries.push(entry);
      const nextEdges = doc.edges.filter((e) => e.source === at);
      const targets = [...new Set(nextEdges.map((e) => e.target))];
      if (targets.length <= 1) {
        at = targets[0];
        continue;
      }
      if (node.kind !== "review") {
        // Optional bypass of a straight chain (the original clean-up template).
        const first = targets.sort(
          (a, b) => order.indexOf(a) - order.indexOf(b),
        )[0];
        if (targets.every((t) => t === first || ancestors(doc, t).has(first))) {
          at = first;
          continue;
        }
        invalid = true;
        break;
      }
      const join = order.find((candidate) =>
        targets.every(
          (t) => t === candidate || ancestors(doc, candidate).has(t),
        ),
      );
      entry.branches = ports(node).map((port) => ({
        label: port === "approved" ? "If approved" : "If rejected",
        source: node.id,
        edgeId: nextEdges.find((e) => e.source_port === port)?.id,
        port,
        entries: nextEdges
          .filter((e) => e.source_port === port)
          .flatMap((e) => descend(e.target, join)),
      }));
      at = join;
      if (at)
        entries.push(
          ...descend(at, until).map((e, i) => ({ ...e, then: i === 0 })),
        );
      at = undefined;
    }
    return entries;
  };
  const result = descend(start.id);
  return invalid || seen.size !== doc.nodes.length ? null : result;
}
export function moveChain(doc: Doc, id: string, direction: -1 | 1): Doc {
  const n = doc.nodes.find((n) => n.id === id);
  if (!n || n.kind === "start") return doc;
  const ins = doc.edges.filter((e) => e.target === id),
    outs = doc.edges.filter((e) => e.source === id);
  if (ins.length !== 1 || outs.length !== 1) return doc;
  const otherId = direction === -1 ? ins[0].source : outs[0].target;
  const other = doc.nodes.find((n) => n.id === otherId);
  if (
    !other ||
    ["start", "output", "review"].includes(other.kind) ||
    n.kind === "review"
  )
    return doc;
  const otherIns = doc.edges.filter((e) => e.target === otherId),
    otherOuts = doc.edges.filter((e) => e.source === otherId);
  if (otherIns.length !== 1 || otherOuts.length !== 1) return doc;
  const first = direction === -1 ? other : n,
    second = direction === -1 ? n : other;
  const before = doc.edges.find((e) => e.target === first.id)!,
    between = doc.edges.find((e) => e.source === first.id)!,
    after = doc.edges.find((e) => e.source === second.id)!;
  return {
    ...doc,
    edges: doc.edges.map((e) =>
      e.id === before.id
        ? { ...e, target: second.id }
        : e.id === between.id
          ? { ...e, source: second.id, target: first.id }
          : e.id === after.id
            ? { ...e, source: first.id }
            : e,
    ),
    nodes: doc.nodes.map((b) =>
      b.id === first.id
        ? { ...b, position: second.position }
        : b.id === second.id
          ? { ...b, position: first.position }
          : b,
    ),
  };
}

export function blankDoc(): Doc {
  return {
    schema: "atelier.workflow/1",
    nodes: [
      {
        id: "n_start",
        key: "start",
        kind: "start",
        title: "Start",
        disabled: false,
        position: { x: 0, y: 0 },
        config: { fields: [] },
      },
      {
        id: "n_save",
        key: "save",
        kind: "output",
        title: "Save results",
        disabled: false,
        position: { x: 0, y: 208 },
        config: { include: [], formats: ["md", "json"], include_sources: true },
      },
    ],
    edges: [
      {
        id: "e_start_save",
        source: "n_start",
        source_port: "out",
        target: "n_save",
        target_port: "in",
      },
    ],
    notes: [],
    viewport: null,
    settings: { default_model: null, keep_test_runs_days: 7 },
  };
}
export function renameField(
  doc: Doc,
  key: string,
  old: string,
  next: string,
): Doc {
  const replace = (value: unknown): unknown => {
    if (typeof value === "string")
      return value.replace(token, (whole, body: string) => {
        const r = grammar.exec(body);
        return r && r[1] === key && r[2] === old
          ? whole.replace(key + "." + old, key + "." + next)
          : whole;
      });
    if (Array.isArray(value)) return value.map(replace);
    if (value && typeof value === "object")
      return Object.fromEntries(
        Object.entries(value).map(([k, v]) => [k, replace(v)]),
      );
    return value;
  };
  return {
    ...doc,
    nodes: doc.nodes.map((n) =>
      n.kind === "start" && n.key === key
        ? {
            ...n,
            config: {
              fields: n.config.fields.map((f) =>
                f.name === old ? { ...f, name: next } : f,
              ),
            },
          }
        : ({ ...n, config: replace(n.config) } as Block),
    ),
  };
}

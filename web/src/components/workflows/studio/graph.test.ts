import { describe, it, expect } from "vitest";
import cases from "../../../../../shared/workflow_graph_cases.json";
import {
  addBlock,
  ancestors,
  blankDoc,
  canConnect,
  clone,
  layout,
  moveChain,
  outlineTree,
  pasteRemap,
  remove,
  renameKey,
  renameField,
  topoOrder,
  validate,
} from "./graph";
import { createStudioStore, asDraft } from "./store";
import type { Doc, Definition } from "./types";
const images = () => clone(cases[0].graph) as Doc;
const meeting = () => clone(cases[1].graph) as Doc;
function definition(graph: Doc): Definition {
  return {
    id: "synthetic",
    name: "Synthetic workflow",
    description: "",
    icon: "workflow",
    graph,
    version: 1,
    template_id: null,
    graph_hash: "fake-hash",
    archived_at: null,
    created_at: "2026-10-12",
    updated_at: "2026-10-12",
  };
}
describe("Shared server validation", () => {
  for (const c of cases)
    it(c.name, () => expect(validate(c.graph as Doc)).toEqual(c.issues));
});
describe("Workflow editing", () => {
  it("orders independently of positions; layout is deterministic and preserves executions", () => {
    const doc = meeting();
    const order = topoOrder(doc);
    doc.nodes.reverse();
    doc.edges.reverse();
    doc.nodes.forEach((n, i) => (n.position = { x: i * 970, y: -i * 1200 }));
    expect(topoOrder(doc)).toEqual(order);
    expect(layout(doc)).toEqual(layout(clone(doc)));
    expect(topoOrder(layout(doc))).toEqual(order);
    expect(ancestors(doc, "n_pack")).toEqual(
      new Set(["n_start", "n_transcript", "n_clean"]),
    );
  });
  it("prevents cycles, duplicates, backwards types and incoming Start", () => {
    const doc = images();
    expect(canConnect(doc, "n_images", "n_start")).toBe(false);
    expect(canConnect(doc, "n_images", "n_draft")).toBe(false);
    expect(canConnect(doc, "n_draft", "n_review")).toBe(false);
    expect(canConnect(meeting(), "n_start", "n_clean")).toBe(false);
  });
  it("inserts on a branch port, moves descendants and heals once on deletion", () => {
    const doc = images();
    const edge = doc.edges.find((e) => e.source === "n_review")!;
    const next = addBlock(
      doc,
      "generate",
      { x: 320, y: 400 },
      undefined,
      edge.id,
    );
    const n = next.nodes.at(-1)!;
    expect(next.edges.find((e) => e.target === n.id)?.source_port).toBe(
      "approved",
    );
    expect(
      next.edges.some((e) => e.source === n.id && e.target === "n_images"),
    ).toBe(true);
    expect(next.nodes.find((n) => n.id === "n_images")!.position.y).toBe(
      doc.nodes.find((n) => n.id === "n_images")!.position.y + 192,
    );
    const healed = remove(next, [n.id]);
    expect(
      healed.edges.some(
        (e) =>
          e.source === "n_review" &&
          e.source_port === "approved" &&
          e.target === "n_images",
      ),
    ).toBe(true);
    expect(remove(doc, ["n_start"]).nodes).toEqual(doc.nodes);
  });
  it("copy/paste gives new IDs/keys, remaps internal references and leaves external ones", () => {
    const doc = images();
    const fragment = {
      nodes: doc.nodes.filter((n) => ["n_draft", "n_review"].includes(n.id)),
      edges: doc.edges.filter((e) => e.source === "n_draft"),
      notes: [],
    };
    const pasted = pasteRemap(doc, fragment);
    const [draft, review] = pasted.nodes.slice(-2);
    expect(draft.key).toBe("draft_2");
    expect(review.key).toBe("review_2");
    expect(draft.id).not.toBe("n_draft");
    if (draft.kind === "generate" && review.kind === "review") {
      expect(draft.config.prompt).toBe("{{start.brief}}");
      expect(review.config.show).toBe("{{draft_2.text}}");
    }
    const renamed = renameKey(doc, "draft", "draft_new");
    expect(
      renamed.nodes.find((n) => n.kind === "review")?.config,
    ).toMatchObject({ show: "{{draft_new.text}}" });
    const input = renameField(doc, "start", "brief", "idea");
    expect(
      input.nodes.find((n) => n.kind === "generate")?.config,
    ).toMatchObject({ prompt: "{{start.idea}}" });
  });
  it("phone lanes support review branches, joins and optional bypass; crossing joins are refused", () => {
    const doc = images();
    expect(outlineTree(doc)).not.toBeNull();
    expect(outlineTree(meeting())).not.toBeNull();
    const bad = addBlock(doc, "generate", { x: 100, y: 100 });
    bad.edges.push({
      id: "unstructured",
      source: "n_start",
      source_port: "out",
      target: bad.nodes.at(-1)!.id,
      target_port: "in",
    });
    expect(outlineTree(bad)).toBeNull();
  });
  it("twenty mixed actions undo/redo exactly; drag and typing group into one step", () => {
    const s = createStudioStore(definition(images()));
    const original = clone(s.getState().draft);
    for (let i = 0; i < 20; i++) {
      s.getState().edit((d) => ({
        ...d,
        name: "Synthetic " + i,
        graph:
          i % 2
            ? layout(d.graph)
            : {
                ...d.graph,
                notes: [
                  ...d.graph.notes,
                  {
                    id: "note_" + i,
                    position: { x: i, y: i },
                    size: { w: 160, h: 100 },
                    tone: "neutral",
                    text: "Fake",
                  },
                ],
              },
      }));
    }
    const final = clone(s.getState().draft);
    for (let i = 0; i < 20; i++) s.getState().undo();
    expect(s.getState().draft).toEqual(original);
    for (let i = 0; i < 20; i++) s.getState().redo();
    expect(s.getState().draft).toEqual(final);
    const before = s.getState().past.length;
    s.getState().beginDrag();
    s.getState().drag({ n_draft: { x: 16, y: 16 } });
    s.getState().drag({ n_draft: { x: 32, y: 32 } });
    s.getState().endDrag();
    expect(s.getState().past).toHaveLength(before + 1);
    s.getState().edit((d) => ({ ...d, name: "Typing one" }), "name");
    s.getState().edit((d) => ({ ...d, name: "Typing two" }), "name");
    expect(s.getState().past).toHaveLength(before + 2);
  });
  it("accepts server defaults without resave loops, preserving newer typing and history", () => {
    const def = definition(blankDoc()),
      s = createStudioStore(def);
    const sent = clone(s.getState().draft);
    s.getState().edit((d) => ({ ...d, name: "Newer draft" }));
    s.getState().accepted({ ...def, version: 2 }, sent);
    expect(s.getState().draft.name).toBe("Newer draft");
    expect(s.getState().version).toBe(2);
    expect(s.getState().saved).toBe(JSON.stringify(sent));
    expect(s.getState().saveState).toBe("saving");
    const newer = clone(s.getState().draft);
    s.getState().accepted({ ...def, ...newer, version: 3 }, newer);
    expect(JSON.stringify(s.getState().draft)).toBe(s.getState().saved);
    expect(s.getState().past).toHaveLength(1);
    expect(asDraft(def)).toEqual(sent);
  });
  it("only moves a straight chain; references remain explicit problems after moving", () => {
    const doc = images();
    expect(moveChain(doc, "n_review", -1)).toBe(doc);
    expect(moveChain(doc, "n_start", 1)).toBe(doc);
    const chain = remove(doc, ["n_review"]);
    expect(moveChain(chain, "n_images", -1)).not.toBe(chain);
  });
});

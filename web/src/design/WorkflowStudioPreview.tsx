import { useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { useUI } from "@/stores/ui";
import cases from "../../../shared/workflow_graph_cases.json";
import { StudioEditor } from "@/components/workflows/studio/Studio";
import {
  StudioContext,
  createStudioStore,
} from "@/components/workflows/studio/store";
import { blankDoc, clone, newId } from "@/components/workflows/studio/graph";
import { BlockCard } from "@/components/workflows/studio/BlockNode";
import { registry } from "@/components/workflows/studio/registry";
import { WorkflowCard } from "@/components/workflows/home/WorkflowsHome";
import type { Definition, Doc, Run } from "@/components/workflows/studio/types";
const states = [
  "canvas",
  "empty",
  "selected",
  "problems",
  "conflict",
  "outline",
  "non-nestable",
  "settings",
  "run-inputs",
  "run-running",
  "run-paused",
  "run-complete",
  "run-failed",
  "run-interrupted",
  "run-reused",
  "run-skipped",
  "pick-paused",
  "block-test",
  "cards",
  "home-cards",
  "quick-add",
  ...[
    "start",
    "generate",
    "transcribe",
    "clean_transcript",
    "generate_image",
    "review",
    "pick",
    "output",
  ].map((k) => "setup-" + k),
];
export default function WorkflowStudioPreview() {
  const [state, setState] = useState(
    new URLSearchParams(location.search).get("state") ?? "canvas",
  );
  const ui = useUI();
  const store = useMemo(() => {
    const graph =
      state === "empty" ? blankDoc() : (clone(cases[0].graph) as Doc);
    if (["setup-transcribe", "setup-clean_transcript"].includes(state)) {
      Object.assign(graph, clone(cases[1].graph));
    }
    if (state === "setup-pick" || state === "pick-paused") {
      graph.nodes.push({
        id: "n_pick",
        key: "favorites",
        kind: "pick",
        title: "Pick favorites",
        disabled: false,
        position: { x: 320, y: 860 },
        config: { from: ["{{draft.text}}"], type: "text", maximum: 1 },
      });
      graph.edges.push({
        id: "e_pick",
        source: "n_draft",
        source_port: "out",
        target: "n_pick",
        target_port: "in",
      });
    }
    graph.settings.default_model = {
      connection_id: "fake",
      model_id: "fake-chat",
    };
    if (state === "problems") {
      const n = graph.nodes.find((n) => n.kind === "generate")!;
      n.config.prompt = "{{missing.text}}";
    }
    if (state === "non-nestable")
      graph.nodes.push({
        id: "n_detached",
        key: "detached",
        kind: "generate",
        title: "Synthetic detached block",
        position: { x: 400, y: 160 },
        disabled: false,
        config: {
          model: "workflow_default",
          instructions: "",
          prompt: "Synthetic input",
          format: "text",
          params: {},
          json_fields: [],
        },
      });
    if (state === "outline") {
      const save = graph.nodes.find((n) => n.kind === "output")!;
      const review = graph.nodes.find((n) => n.kind === "review")!;
      graph.edges.push({
        id: newId("e"),
        source: review.id,
        source_port: "rejected",
        target: save.id,
        target_port: "in",
      });
    }
    const definition: Definition = {
      id: "synthetic-design",
      name: "Synthetic image workflow",
      description: "Fake runtime design fixture",
      icon: "workflow",
      graph,
      version: 1,
      template_id: null,
      graph_hash: "fake",
      archived_at: null,
      created_at: "2026-10-12",
      updated_at: "2026-10-12",
    };
    const s = createStudioStore(definition);
    if (state === "selected") s.getState().select(["n_draft"]);
    if (state.startsWith("setup-")) {
      const node = graph.nodes.find((n) => n.kind === state.slice(6));
      if (node) s.getState().select([node.id]);
    }
    if (state === "conflict")
      s.getState().status("conflict", {
        ...definition,
        name: "Synthetic changed elsewhere",
        version: 2,
      });
    return s;
  }, [state]);
  const graph = store.getState().draft.graph;
  const runStates =
    (state.startsWith("run-") && state !== "run-inputs") ||
    ["pick-paused", "block-test"].includes(state);
  const status =
    state === "run-running"
      ? "running"
      : state === "run-paused" || state === "pick-paused"
        ? "paused"
        : state === "run-failed"
          ? "failed"
          : state === "run-interrupted"
            ? "interrupted"
            : "complete";
  const previewRun: Run = {
    id: "synthetic-design-run",
    kind: "graph",
    mode: state === "block-test" ? "test" : "run",
    def_id: "synthetic-design",
    def_name: "Synthetic image workflow",
    graph_hash: "fake",
    snapshot_id: null,
    parent_run_id: null,
    state: status,
    stage:
      status === "paused"
        ? "Waiting for you"
        : status === "running"
          ? "Writing"
          : "Ready for review",
    error:
      status === "failed"
        ? "Synthetic failure. Earlier outputs are saved."
        : null,
    created_at: "2026-10-13T12:00:00Z",
    updated_at: "2026-10-13T12:00:02Z",
    inputs: { brief: "Synthetic blue circle" },
    graph,
    nodes: Object.fromEntries(
      graph.nodes.map((n) => {
        const active =
          n.id ===
          (state === "pick-paused"
            ? "n_pick"
            : status === "paused"
              ? "n_review"
              : "n_draft");
        const nodeState = active
          ? status
          : status === "complete"
            ? "complete"
            : n.kind === "start"
              ? "complete"
              : "pending";
        return [
          n.id,
          {
            state:
              state === "run-skipped" && n.kind !== "start"
                ? "skipped"
                : nodeState,
            attempt: active ? 1 : 0,
            port: nodeState === "complete" ? "out" : null,
            output:
              n.kind === "generate"
                ? {
                    text: "A synthetic blue circle on a warm paper background.",
                  }
                : n.kind === "review"
                  ? { value: "A synthetic blue circle." }
                  : n.kind === "pick"
                    ? {
                        choices: [
                          "Synthetic choice one",
                          "Synthetic choice two",
                        ],
                      }
                    : n.kind === "start"
                      ? { brief: "Synthetic blue circle" }
                      : null,
            error: active && status === "failed" ? "Synthetic failure" : null,
            started_at: active ? "2026-10-13T12:00:00Z" : null,
            finished_at: status === "complete" ? "2026-10-13T12:00:02Z" : null,
            reused_from:
              state === "run-reused" && n.kind !== "output"
                ? "synthetic-earlier"
                : null,
            warnings: [],
          },
        ];
      }),
    ),
    results:
      status === "complete"
        ? [
            {
              node_id: "n_save",
              label: "Save results",
              items: [
                {
                  label: "Synthetic draft",
                  type: "text",
                  value: "A synthetic blue circle on a warm paper background.",
                },
              ],
            },
          ]
        : [],
    source_available: false,
  };
  return (
    <div className="flex h-full min-h-0 flex-col">
      <div
        className="flex max-h-44 shrink-0 flex-wrap items-center gap-2 overflow-y-auto p-3"
        tabIndex={0}
        role="region"
        aria-label="Synthetic Studio states"
      >
        <p className="text-xs text-fg-3">
          Workflow Studio · fake runtime states
        </p>
        {["light", "dark"].map((theme) => (
          <Button
            key={theme}
            variant="outline"
            onClick={() => ui.set({ theme: theme as "light" | "dark" })}
          >
            {theme}
          </Button>
        ))}
        {states.map((s) => (
          <Button
            key={s}
            variant={state === s ? "default" : "outline"}
            onClick={() => setState(s)}
          >
            {s}
          </Button>
        ))}
      </div>
      <StudioContext.Provider value={store}>
        {state === "home-cards" ? (
          <div className="wf-home">
            <h1>Your workflows</h1>
            <div className="wf-card-grid">
              <WorkflowCard
                definition={{
                  ...store.getState().draft,
                  id: "synthetic-card",
                  version: 1,
                  template_id: null,
                  graph_hash: "fake",
                  archived_at: null,
                  created_at: "2026-10-12",
                  updated_at: "2026-10-12",
                }}
                refresh={() => {}}
              />
            </div>
          </div>
        ) : state === "cards" ? (
          <div
            className="flex flex-1 flex-wrap items-start gap-6 overflow-y-auto p-6"
            tabIndex={0}
            aria-label="Synthetic block cards"
          >
            {store.getState().draft.graph.nodes.map((n) => (
              <div key={n.id}>
                <p className="mb-2 text-xs text-fg-3">
                  {registry[n.kind].label}
                </p>
                <BlockCard block={n} />
              </div>
            ))}
            {(clone(cases[1].graph) as Doc).nodes
              .filter(
                (n) => n.kind === "transcribe" || n.kind === "clean_transcript",
              )
              .map((n) => (
                <BlockCard block={n} key={n.id} />
              ))}
          </div>
        ) : (
          <StudioEditor
            key={state}
            store={store}
            preview
            previewRun={runStates ? previewRun : undefined}
            initialQuick={state === "quick-add"}
            initialView={
              state === "outline" || state === "non-nestable"
                ? "outline"
                : undefined
            }
            initialPanel={
              state === "problems"
                ? "problems"
                : state === "settings"
                  ? "settings"
                  : state === "run-inputs" || runStates
                    ? "run"
                    : undefined
            }
          />
        )}
      </StudioContext.Provider>
    </div>
  );
}

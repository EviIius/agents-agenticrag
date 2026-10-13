import { describe, it, expect } from "vitest";
import { edgeState, runLabel, updateLive } from "./run-state";
import { blankDoc } from "./graph";
import type { Run } from "./types";
const step = {
  state: "running" as const,
  attempt: 1,
  port: null,
  output: { text: "Saved prefix" },
  error: null,
  started_at: null,
  finished_at: null,
};
const run: Run = {
  id: "fake-run",
  kind: "graph",
  mode: "run",
  error: null,
  def_id: "fake",
  def_name: "Fake",
  graph_hash: "fake",
  state: "running",
  stage: "Writing",
  created_at: "2026-10-13",
  updated_at: "2026-10-13",
  inputs: {},
  graph: blankDoc(),
  nodes: { n_start: step },
  source_available: false,
};
describe("server-driven run updates", () => {
  it("uses cumulative text so a persisted prefix is never duplicated", () => {
    const result = updateLive(
      [run],
      {
        run_id: run.id,
        node_id: "n_start",
        text: "Saved prefix and tail",
        delta: "prefix and tail",
      },
      "node.text",
    );
    expect(result[0].nodes.n_start.output?.text).toBe("Saved prefix and tail");
  });
  it("never replaces a completed result with late text", () => {
    const complete = {
      ...run,
      nodes: {
        n_start: {
          ...step,
          state: "complete" as const,
          output: { text: "Complete" },
        },
      },
    };
    expect(
      updateLive(
        [complete],
        { run_id: run.id, node_id: "n_start", text: "Partial" },
        "node.text",
      )[0],
    ).toBe(complete);
  });
  it("progress is exactly the event payload, not elapsed time", () => {
    const result = updateLive(
      [run],
      {
        run_id: run.id,
        node_id: "n_start",
        done: 2,
        total: 4,
        label: "Generating",
      },
      "node.progress",
    );
    expect(result[0].nodes.n_start.progress).toEqual({
      done: 2,
      total: 4,
      label: "Generating",
    });
    expect(runLabel(result[0], "n_start")).toBe("Generating · 2 of 4");
  });
  it("unrelated events leave the run untouched", () => {
    expect(
      updateLive(
        [run],
        { run_id: "other", node_id: "n_start", text: "Other" },
        "node.text",
      )[0],
    ).toBe(run);
  });
  it("reused outputs are labeled as reuse", () => {
    expect(
      runLabel(
        { ...run, nodes: { n_start: { ...step, reused_from: "earlier" } } },
        "n_start",
      ),
    ).toBe("Reused from earlier run");
  });
  it("only the taken incoming edge is active", () => {
    const doc = blankDoc(),
      edge = doc.edges[0];
    const r = {
      ...run,
      nodes: {
        [edge.source]: { ...step, state: "complete" as const, port: "out" },
        [edge.target]: step,
      },
    };
    expect(edgeState(r, edge)).toBe("active");
    expect(
      edgeState(
        {
          ...r,
          nodes: {
            ...r.nodes,
            [edge.source]: {
              ...step,
              state: "complete" as const,
              port: "rejected",
            },
          },
        },
        edge,
      ),
    ).toBe("not-taken");
  });
});

it("late cumulative events cannot regress a fresher snapshot or an earlier attempt", () => {
  const refreshed = {
    ...run,
    nodes: {
      n_start: {
        ...step,
        attempt: 2,
        output: { text: "Newer cumulative snapshot" },
      },
    },
  };
  expect(
    updateLive(
      [refreshed],
      { run_id: run.id, node_id: "n_start", attempt: 1, text: "Old attempt" },
      "node.text",
    )[0],
  ).toBe(refreshed);
  expect(
    updateLive(
      [refreshed],
      { run_id: run.id, node_id: "n_start", attempt: 2, text: "Newer" },
      "node.text",
    )[0],
  ).toBe(refreshed);
});

import { Handle, Position, type Node, type NodeProps } from "@xyflow/react";
import { useStudio } from "./store";
import { outputs, ports, registry, summary } from "./registry";
import { BlockMenu } from "./BlockMenu";
import { Check, Pause, RotateCcw, CircleAlert, Minus, X } from "lucide-react";
import { runLabel } from "./run-state";
import type { Run } from "./types";
import type { Block, Issue } from "./types";
import type { CSSProperties } from "react";
export type BlockFlowNode = Node<
  {
    block: Block;
    issues: Issue[];
    index: number;
    defaultName?: string;
    readonly: boolean;
    run?: Run;
  },
  "block"
>;
export function BlockCard({
  block: node,
  selected = false,
  issues = [],
  defaultName,
  children,
  run,
}: {
  block: Block;
  selected?: boolean;
  issues?: Issue[];
  defaultName?: string;
  children?: React.ReactNode;
  run?: Run;
}) {
  const meta = registry[node.kind];
  const problem =
    issues.find((i) => i.node_id === node.id && i.severity === "error") ??
    issues.find((i) => i.node_id === node.id && i.severity === "warning");
  const fields = Object.keys(outputs(node));
  const step = run?.nodes[node.id];
  const state = step?.reused_from ? "reused" : step?.state;
  const Badge =
    state === "complete"
      ? Check
      : state === "paused"
        ? Pause
        : state === "reused"
          ? RotateCcw
          : state === "failed"
            ? CircleAlert
            : state === "skipped"
              ? Minus
              : X;
  return (
    <div
      className="wf-block"
      data-run={state}
      data-selected={selected}
      data-disabled={node.disabled}
    >
      <div className="wf-block-body">
        <div className="wf-block-head">
          <span className="wf-tile" data-cat={meta.tone}>
            <meta.Icon />
          </span>
          <div className="min-w-0 flex-1">
            <div className="wf-block-title">{node.title}</div>
            <div className="wf-kind">{meta.label}</div>
          </div>
          {children}
        </div>
        <p className="wf-summary" data-problem={problem?.severity}>
          {run ? runLabel(run, node.id) : summary(node, defaultName)}
        </p>
        {fields.length > 0 && (
          <div className="wf-chips">
            {fields.slice(0, 2).map((field) => (
              <span className="wf-chip" key={field}>
                {node.key}.{field}
              </span>
            ))}
            {fields.length > 2 && (
              <span className="wf-chip">+{fields.length - 2}</span>
            )}
          </div>
        )}
        {step && !["pending", "running"].includes(step.state) && (
          <span
            className="wf-run-badge"
            data-state={state}
            role="img"
            aria-label={state}
          >
            <Badge className="size-3" />
          </span>
        )}
        {problem && (
          <span
            className="wf-problem-dot"
            role="img"
            data-severity={problem.severity}
            aria-label={problem.message}
          />
        )}
      </div>
    </div>
  );
}
export function BlockNode({ data, selected }: NodeProps<BlockFlowNode>) {
  const select = useStudio((s) => s.select);
  const node = data.block;
  const p = ports(node);
  return (
    <div
      style={{ "--wf-index": Math.min(11, data.index) } as CSSProperties}
      onDoubleClick={(e) => {
        if (data.readonly) return;
        e.stopPropagation();
        select([node.id]);
        requestAnimationFrame(() =>
          document
            .querySelector<HTMLInputElement>("[aria-label='Block name']")
            ?.focus(),
        );
      }}
    >
      {node.kind !== "start" && (
        <Handle
          type="target"
          position={Position.Top}
          id="in"
          className="wf-port"
        />
      )}
      <BlockCard
        block={node}
        selected={selected}
        issues={data.issues}
        defaultName={data.defaultName}
        run={data.run}
      >
        {!data.readonly && <BlockMenu node={node} />}
      </BlockCard>
      {p.map((port, i) => (
        <div key={port}>
          <Handle
            type="source"
            position={Position.Bottom}
            id={port}
            className="wf-port"
            style={{ left: `${((i + 1) / (p.length + 1)) * 100}%` }}
          />
          {p.length > 1 && (
            <span
              className="wf-port-label"
              style={{ left: `${((i + 1) / (p.length + 1)) * 100}%` }}
            >
              {port === "approved" ? "Approved" : "Rejected"}
            </span>
          )}
        </div>
      ))}
    </div>
  );
}

import { useQuery } from "@tanstack/react-query";
import { useRef, useState } from "react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { TextField } from "./fields";
import { fields, references } from "./graph";
import { outputs } from "./registry";
import type { Doc, Run } from "./types";
import type { components } from "@/lib/api-types";
export function BlockRunInputs({
  doc,
  defId,
  nodeId,
  mode,
  beforeRun,
  accepted,
}: {
  doc: Doc;
  defId: string;
  nodeId: string;
  mode: "run" | "test";
  beforeRun: () => Promise<boolean>;
  accepted: (r: Run) => void;
}) {
  const [samples, setSamples] = useState<Record<string, string>>({}),
    [notice, setNotice] = useState(""),
    [busy, setBusy] = useState(false);
  const request = useRef<{ body: string; key: string }>(undefined);
  const reuse = useQuery({
    queryKey: ["workflow-reuse", defId, nodeId, mode, doc],
    queryFn: () =>
      api<components["schemas"]["ReusePlan"]>(
        `/workflows/defs/${defId}/reuse?node_id=${encodeURIComponent(nodeId)}&mode=${mode}`,
      ),
  });
  const node = doc.nodes.find((n) => n.id === nodeId)!;
  const refs = Array.from(
    new Map(
      fields(node)
        .flatMap(([s]) => references(s))
        .map((r) => [`${r.key}.${r.field}`, r]),
    ).values(),
  );
  const canSample = refs.every((r) =>
    [
      "text",
      "string",
      "short_text",
      "long_text",
      "choice",
      "number",
      "boolean",
    ].includes(outputs(doc.nodes.find((n) => n.key === r.key)!)[r.field]),
  );
  const useSamples = mode === "test" && !reuse.data?.eligible;
  const start = async () => {
    setBusy(true);
    setNotice("");
    try {
      if (!(await beforeRun()))
        throw new Error("Save the workflow before running this block.");
      const material = {
        mode,
        node_id: nodeId,
        ...(useSamples
          ? {
              samples: Object.fromEntries(
                refs.map((r) => {
                  const name = `${r.key}.${r.field}`,
                    type = outputs(doc.nodes.find((n) => n.key === r.key)!)[
                      r.field
                    ];
                  return [
                    name,
                    type === "number"
                      ? Number(samples[name])
                      : type === "boolean"
                        ? samples[name] === "true"
                        : (samples[name] ?? ""),
                  ];
                }),
              ),
            }
          : { source_run_id: reuse.data?.source_run_id }),
      };
      const body = JSON.stringify(material);
      if (request.current?.body !== body)
        request.current = { body, key: crypto.randomUUID() };
      const run = await api<Run>(`/workflows/defs/${defId}/runs`, {
        ...material,
        request_key: request.current!.key,
      });
      request.current = undefined;
      accepted(run);
    } catch (e) {
      setNotice(e instanceof Error ? e.message : "Couldn't start this block.");
    } finally {
      setBusy(false);
    }
  };
  return (
    <section className="wf-field-stack" aria-label="Block run inputs">
      <h2 className="font-semibold">
        {mode === "test" ? "Test this block" : "Run from here"} · {node.title}
      </h2>
      {reuse.data?.eligible ? (
        <p className="wf-help">Verified earlier outputs will be reused.</p>
      ) : (
        <p className="wf-help">
          {reuse.data?.reason ?? "Checking earlier outputs…"}
        </p>
      )}
      {useSamples &&
        canSample &&
        refs.map((r) => {
          const name = `${r.key}.${r.field}`;
          return (
            <TextField
              key={name}
              label={`Sample ${name}`}
              value={samples[name] ?? ""}
              onChange={(v) => setSamples((s) => ({ ...s, [name]: v }))}
            />
          );
        })}
      {useSamples && !canSample && (
        <p className="wf-help">
          Run the workflow first to provide real file or image inputs.
        </p>
      )}
      {notice && (
        <p role="alert" className="text-danger text-sm">
          {notice}
        </p>
      )}
      <Button
        onClick={() => void start()}
        disabled={
          busy ||
          reuse.isPending ||
          (!reuse.data?.eligible && (!useSamples || !canSample))
        }
      >
        {busy ? "Starting…" : mode === "test" ? "Test block" : "Run from here"}
      </Button>
    </section>
  );
}

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import type { Run } from "./types";
import { useRunActions } from "./RunActions";
export function BlockOutput({
  nodeId,
  latest,
}: {
  nodeId: string;
  latest?: Run;
}) {
  const context = useRunActions();
  const q = useQuery({
    queryKey: [
      "workflow-block-tests",
      context?.defId,
      nodeId,
      latest?.updated_at,
      latest?.state,
    ],
    queryFn: () =>
      api<Run[]>(
        `/workflows/defs/${context!.defId}/tests?node_id=${encodeURIComponent(nodeId)}`,
      ),
    enabled: !!context,
  });
  const run =
    latest?.mode === "test" && latest.nodes[nodeId]?.attempt
      ? latest
      : (q.data?.[0] ?? latest);
  const output = run?.nodes[nodeId]?.output;
  return (
    <>
      {run?.mode === "test" && (
        <p className="wf-help">Block test · {run.state}</p>
      )}
      {output ? (
        <pre className="wf-output-text">
          {typeof output.text === "string"
            ? output.text
            : JSON.stringify(output, null, 2)}
        </pre>
      ) : (
        <p className="wf-empty-output">
          Run or test this block to see its output.
        </p>
      )}
      {q.isError && (
        <p role="alert">
          Tests couldn't be loaded.{" "}
          <Button variant="ghost" onClick={() => void q.refetch()}>
            Try again
          </Button>
        </p>
      )}
    </>
  );
}

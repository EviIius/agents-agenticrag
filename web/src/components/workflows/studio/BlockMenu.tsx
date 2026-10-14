import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { components } from "@/lib/api-types";
import { useRunActions } from "./RunActions";
import {
  Copy,
  MoreHorizontal,
  Trash2,
  Ban,
  ArrowUp,
  ArrowDown,
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { IconButton } from "@/components/app/IconButton";
import type { Block } from "./types";
import { useStudio } from "./store";
import { clone, moveChain, pasteRemap, remove } from "./graph";
export function BlockMenu({
  node,
  outline = false,
  structureDisabled = false,
}: {
  node: Block;
  outline?: boolean;
  structureDisabled?: boolean;
}) {
  const edit = useStudio((s) => s.edit),
    select = useStudio((s) => s.select),
    doc = useStudio((s) => s.draft.graph);
  const runActions = useRunActions();
  const [open, setOpen] = useState(false);
  const reuse = useQuery({
    queryKey: [
      "workflow-reuse-menu",
      runActions?.defId,
      node.id,
      runActions?.revision,
    ],
    enabled: open && !!runActions && node.kind !== "start",
    queryFn: () =>
      api<components["schemas"]["ReusePlan"]>(
        `/workflows/defs/${runActions!.defId}/reuse?node_id=${encodeURIComponent(node.id)}`,
      ),
  });
  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <IconButton
          className="nodrag nopan wf-more"
          label={`Actions for ${node.title}`}
        >
          <MoreHorizontal />
        </IconButton>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {runActions && node.kind !== "start" && (
          <>
            <DropdownMenuItem
              disabled={!reuse.data?.eligible}
              title={reuse.data?.reason ?? "Checking earlier outputs…"}
              onClick={() => runActions.act("run", node.id)}
            >
              Run from here
            </DropdownMenuItem>
            <DropdownMenuItem
              disabled={node.disabled}
              onClick={() => runActions.act("test", node.id)}
            >
              Test this block
            </DropdownMenuItem>
            <DropdownMenuSeparator />
          </>
        )}
        <DropdownMenuItem
          onClick={() => {
            select([node.id]);
            requestAnimationFrame(() =>
              document
                .querySelector<HTMLInputElement>("[aria-label='Block name']")
                ?.focus(),
            );
          }}
        >
          Rename
        </DropdownMenuItem>
        <DropdownMenuItem
          disabled={node.kind === "start" || structureDisabled}
          onClick={() =>
            edit((d) => ({
              ...d,
              graph: pasteRemap(d.graph, {
                nodes: [clone(node)],
                edges: [],
                notes: [],
              }),
            }))
          }
        >
          <Copy />
          Duplicate
        </DropdownMenuItem>
        <DropdownMenuItem
          disabled={node.kind === "start"}
          onClick={() =>
            edit((d) => ({
              ...d,
              graph: {
                ...d.graph,
                nodes: d.graph.nodes.map((n) =>
                  n.id === node.id ? { ...n, disabled: !n.disabled } : n,
                ),
              },
            }))
          }
        >
          <Ban />
          {node.disabled ? "Enable" : "Disable"}
        </DropdownMenuItem>
        {outline && (
          <>
            <DropdownMenuSeparator />
            {([-1, 1] as const).map((direction) => (
              <DropdownMenuItem
                key={direction}
                disabled={moveChain(doc, node.id, direction) === doc}
                onClick={() =>
                  edit((d) => ({
                    ...d,
                    graph: moveChain(d.graph, node.id, direction),
                  }))
                }
              >
                {direction === -1 ? <ArrowUp /> : <ArrowDown />}
                {direction === -1 ? "Move up" : "Move down"}
              </DropdownMenuItem>
            ))}
          </>
        )}
        <DropdownMenuSeparator />
        <DropdownMenuItem
          className="text-danger"
          disabled={node.kind === "start" || structureDisabled}
          onClick={() => {
            edit((d) => ({ ...d, graph: remove(d.graph, [node.id]) }));
            select([]);
          }}
        >
          <Trash2 />
          Delete
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

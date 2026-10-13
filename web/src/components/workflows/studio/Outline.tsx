import { Plus, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { IconButton } from "@/components/app/IconButton";
import { useStudio } from "./store";
import { outlineTree, topoOrder, type OutlineEntry } from "./graph";
import { registry, summary } from "./registry";
import { BlockMenu } from "./BlockMenu";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import type { AddContext } from "./Canvas";
export function Outline({ add }: { add: (context?: AddContext) => void }) {
  const doc = useStudio((s) => s.draft.graph),
    select = useStudio((s) => s.select),
    selection = useStudio((s) => s.selection);
  const tree = outlineTree(doc);
  const phone = useMediaQuery("(max-width:767px)");
  let order: string[];
  try {
    order = topoOrder(doc);
  } catch {
    order = doc.nodes.map((n) => n.id);
  }
  const render = (entries: OutlineEntry[]): React.ReactNode =>
    entries.map((entry) => {
      const node = doc.nodes.find((n) => n.id === entry.id)!;
      const meta = registry[node.kind];
      const edge = doc.edges.find((e) => e.source === node.id);
      return (
        <div key={node.id}>
          {entry.then && <p className="wf-lane-label">Then</p>}
          <div
            className="wf-outline-row"
            data-disabled={node.disabled}
            data-selected={selection.includes(node.id)}
          >
            <Button
              variant="ghost"
              className="wf-outline-select"
              aria-label={`Configure ${node.title}`}
              onClick={() => select([node.id])}
            >
              <span className="wf-tile" data-cat={meta.tone}>
                <meta.Icon />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block truncate font-medium">{node.title}</span>
                <span className="wf-summary">
                  {summary(node, doc.settings.default_model?.model_id)}
                </span>
              </span>
              <ChevronRight className="size-4 shrink-0" />
            </Button>
            <BlockMenu
              node={node}
              outline={Boolean(tree)}
              structureDisabled={phone && !tree}
            />
          </div>
          {entry.branches
            ? entry.branches.map((lane) => (
                <div className="wf-outline-lane" key={lane.port}>
                  <p className="wf-lane-label">{lane.label}</p>
                  {lane.entries.length ? (
                    render(lane.entries)
                  ) : (
                    <Button
                      variant="ghost"
                      disabled={!tree}
                      onClick={() =>
                        add({
                          source: lane.source,
                          port: lane.port,
                          edgeId: lane.edgeId,
                        })
                      }
                    >
                      + Add a block
                    </Button>
                  )}
                </div>
              ))
            : node.kind !== "output" && (
                <div className="wf-outline-insert">
                  <IconButton
                    label={`Insert after ${node.title}`}
                    disabled={!tree}
                    onClick={() =>
                      add({
                        edgeId: edge?.id,
                        source: node.id,
                        port: edge?.source_port,
                      })
                    }
                  >
                    <Plus />
                  </IconButton>
                </div>
              )}
        </div>
      );
    });
  return (
    <div className="wf-outline" aria-label="Workflow Outline">
      {!tree && (
        <p role="status" className="wf-outline-notice">
          Part of this workflow is easier to change on a larger screen. Settings
          still open here.
        </p>
      )}
      {render(tree ?? order.map((id) => ({ id })))}
    </div>
  );
}

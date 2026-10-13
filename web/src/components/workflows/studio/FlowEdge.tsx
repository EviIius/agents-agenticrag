import {
  BaseEdge,
  EdgeLabelRenderer,
  getSmoothStepPath,
  type EdgeProps,
  type Edge,
} from "@xyflow/react";
import { Plus, X } from "lucide-react";
import { Button } from "@/components/ui/button";
export type Flow = Edge<
  {
    insert: (id: string, anchor: { x: number; y: number }) => void;
    remove: (id: string) => void;
    readonly: boolean;
    hovered: boolean;
  },
  "flow"
>;
export function FlowEdge(props: EdgeProps<Flow>) {
  const [path, x, y] = getSmoothStepPath({ ...props, borderRadius: 12 });
  return (
    <>
      <BaseEdge
        id={props.id}
        path={path}
        className="wf-edge-path"
        interactionWidth={24}
      />
      <EdgeLabelRenderer>
        {!props.data?.readonly && (
          <div
            className="wf-edge-tools nodrag nopan"
            data-visible={props.selected || props.data?.hovered}
            style={{
              transform: `translate(-50%, -50%) translate(${x}px,${y}px)`,
            }}
          >
            <Button
              aria-label={`Insert on connection ${props.id}`}
              variant="outline"
              onClick={(e) =>
                props.data?.insert(props.id, { x: e.clientX, y: e.clientY })
              }
            >
              <Plus />
            </Button>
            <Button
              aria-label={`Delete connection ${props.id}`}
              variant="ghost"
              onClick={() => props.data?.remove(props.id)}
            >
              <X />
            </Button>
          </div>
        )}
      </EdgeLabelRenderer>
    </>
  );
}

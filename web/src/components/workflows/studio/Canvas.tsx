import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  ReactFlow,
  ReactFlowProvider,
  Background,
  BackgroundVariant,
  MiniMap,
  useReactFlow,
  useViewport,
  type OnConnectEnd,
  type NodeChange,
  type EdgeChange,
} from "@xyflow/react";
import "@xyflow/react/dist/base.css";
import {
  Plus,
  Minus,
  Maximize,
  LayoutGrid,
  List,
  StickyNote,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuTrigger,
  ContextMenuItem,
  ContextMenuSeparator,
} from "@/components/ui/context-menu";
import { IconButton } from "@/components/app/IconButton";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import { useStudio } from "./store";
import { canConnect, connect, layout } from "./graph";
import { registry } from "./registry";
import { BlockNode, type BlockFlowNode } from "./BlockNode";
import { NoteNode, type NoteFlowNode } from "./NoteNode";
import { FlowEdge, type Flow } from "./FlowEdge";
import type { Issue, Point } from "./types";
export type AddContext = {
  point?: Point;
  edgeId?: string;
  source?: string;
  port?: string;
  anchor?: Point;
};
export type CanvasActions = {
  center: () => Point;
  fit: () => void;
  problem: (id: string) => void;
  tidy: () => void;
  zoom100: () => void;
  added: () => void;
};
type Props = {
  issues: Issue[];
  add: (context?: AddContext) => void;
  outline: () => void;
  readonly?: boolean;
  minimap?: boolean;
  action: (name: string) => void;
};
const nodeTypes = { block: BlockNode, note: NoteNode };
const edgeTypes = { flow: FlowEdge };
export const Canvas = forwardRef<CanvasActions, Props>(
  function Canvas(props, ref) {
    return (
      <ReactFlowProvider>
        <FlowCanvas {...props} ref={ref} />
      </ReactFlowProvider>
    );
  },
);
const FlowCanvas = forwardRef<CanvasActions, Props>(function FlowCanvas(
  { issues, add, outline, readonly = false, minimap = true, action },
  ref,
) {
  const doc = useStudio((s) => s.draft.graph),
    selection = useStudio((s) => s.selection),
    select = useStudio((s) => s.select),
    edit = useStudio((s) => s.edit),
    begin = useStudio((s) => s.beginDrag),
    drag = useStudio((s) => s.drag),
    end = useStudio((s) => s.endDrag);
  const root = useRef<HTMLDivElement>(null);
  const flow = useReactFlow();
  const viewportIntent = useRef(false);
  const moveView = (change: () => unknown) => {
    viewportIntent.current = true;
    void change();
  };
  const viewport = useViewport();
  const reduced = useReducedMotion(),
    large = useMediaQuery("(min-width:1280px)");
  const [arranging, setArranging] = useState(false),
    [entrance, setEntrance] = useState(true),
    [hint, setHint] = useState(
      () => localStorage.getItem("atelier.workflow.hint") !== "seen",
    );
  const dimensions = useRef<Record<string, { width: number; height: number }>>(
    {},
  );
  const [measurement, measured] = useState(0);
  const [hoveredEdge, setHoveredEdge] = useState<string>();
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  useEffect(() => {
    const t = setTimeout(() => setEntrance(false), 520);
    return () => {
      clearTimeout(t);
      clearTimeout(timer.current);
    };
  }, []);
  const duration = reduced ? 0 : 320;
  const center = () => {
    const r = root.current!.getBoundingClientRect();
    return flow.screenToFlowPosition({
      x: r.left + r.width / 2,
      y: r.top + r.height / 2,
    });
  };
  const tidy = () => {
    setArranging(!reduced);
    clearTimeout(timer.current);
    edit((d) => ({ ...d, graph: layout(d.graph) }));
    timer.current = setTimeout(() => {
      setArranging(false);
      moveView(() => flow.fitView({ duration, padding: 0.15 }));
    }, duration);
  };
  useImperativeHandle(ref, () => ({
    center,
    fit: () => moveView(() => flow.fitView({ duration, padding: 0.15 })),
    problem: (id) => {
      const n = flow.getNode(id);
      if (n)
        moveView(() =>
          flow.setCenter(n.position.x + 144, n.position.y + 64, {
            zoom: 1,
            duration,
          }),
        );
    },
    tidy,
    zoom100: () => moveView(() => flow.zoomTo(1, { duration })),
    added: () => setHint(false),
  }));
  const nodes = useMemo<(BlockFlowNode | NoteFlowNode)[]>(
    () => [
      ...doc.nodes.map((block, index) => ({
        id: block.id,
        type: "block" as const,
        position: block.position,
        selected: selection.includes(block.id),
        measured: dimensions.current[block.id],
        ariaLabel: `${registry[block.kind].label} block ‘${block.title}’, ${index + 1} of ${doc.nodes.length}`,
        domAttributes: { "aria-roledescription": "block" },
        data: {
          block,
          issues,
          index,
          defaultName: doc.settings.default_model?.model_id,
          readonly,
        },
      })),
      ...doc.notes.map((note) => ({
        id: note.id,
        type: "note" as const,
        position: note.position,
        selected: selection.includes(note.id),
        measured: dimensions.current[note.id],
        style: { width: note.size.w, height: note.size.h },
        data: { note, readonly },
        ariaLabel: "Canvas note",
      })),
    ],
    [doc, selection, issues, readonly, measurement],
  );
  const edges = useMemo<Flow[]>(
    () =>
      doc.edges.map((edge) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        sourceHandle: edge.source_port,
        targetHandle: edge.target_port,
        type: "flow",
        ariaLabel: `Connection from ${doc.nodes.find((n) => n.id === edge.source)?.title ?? "block"} to ${doc.nodes.find((n) => n.id === edge.target)?.title ?? "block"}`,
        domAttributes: { "aria-roledescription": "connection" },
        selected: selection.includes(edge.id),
        data: {
          insert: (edgeId, anchor) => {
            const target = doc.nodes.find((n) => n.id === edge.target)!;
            add({
              edgeId,
              point: { x: target.position.x, y: target.position.y - 112 },
              anchor,
            });
          },
          remove: (id) =>
            edit((d) => ({
              ...d,
              graph: {
                ...d.graph,
                edges: d.graph.edges.filter((e) => e.id !== id),
              },
            })),
          readonly,
          hovered: hoveredEdge === edge.id,
        },
      })),
    [doc, selection, add, edit, readonly, hoveredEdge],
  );
  const connectEnd: OnConnectEnd = (event, state) => {
    if (
      readonly ||
      state.isValid ||
      !state.fromNode ||
      state.fromHandle?.type !== "source"
    )
      return;
    const mouse = "changedTouches" in event ? event.changedTouches[0] : event;
    const point = { x: mouse.clientX, y: mouse.clientY };
    const target = state.toNode;
    if (
      target &&
      canConnect(
        doc,
        state.fromNode.id,
        target.id,
        state.fromHandle.id ?? "out",
      )
    )
      edit((d) => ({
        ...d,
        graph: connect(
          d.graph,
          state.fromNode!.id,
          target.id,
          state.fromHandle!.id ?? "out",
        ),
      }));
    else if (!target)
      add({
        point: flow.screenToFlowPosition(point),
        source: state.fromNode.id,
        port: state.fromHandle.id ?? "out",
        anchor: point,
      });
  };
  const selectedChanges = (changes: (NodeChange | EdgeChange)[]) => {
    const next = new Set(selection);
    for (const c of changes)
      if (c.type === "select") {
        if (c.selected) next.add(c.id);
        else next.delete(c.id);
      }
    if (JSON.stringify([...next]) !== JSON.stringify(selection))
      select([...next]);
  };
  const changed = (changes: NodeChange[]) => {
    let updated = false;
    for (const c of changes)
      if (
        c.type === "dimensions" &&
        c.dimensions &&
        JSON.stringify(dimensions.current[c.id]) !==
          JSON.stringify(c.dimensions)
      ) {
        dimensions.current[c.id] = c.dimensions;
        updated = true;
      }
    if (updated) measured((v) => v + 1);
    if (readonly) return;
    selectedChanges(changes);
    const positions = Object.fromEntries(
      changes
        .filter((c) => c.type === "position" && c.position)
        .map((c) => (c.type === "position" ? [c.id, c.position!] : [])),
    );
    if (Object.keys(positions).length) drag(positions);
  };
  const drop = (event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();
    if (readonly) return;
    const kind = event.dataTransfer.getData("application/x-atelier-block");
    if (!(kind in registry)) return;
    const point = flow.screenToFlowPosition({
      x: event.clientX,
      y: event.clientY,
    });
    // Hit-test the actual rendered path in screen coordinates, including bends.
    let edgeId: string | undefined;
    let best = 12;
    root.current
      ?.querySelectorAll<SVGPathElement>(
        ".react-flow__edge .react-flow__edge-path",
      )
      .forEach((path) => {
        const length = path.getTotalLength(),
          matrix = path.getScreenCTM();
        if (!matrix) return;
        for (let at = 0; at <= length; at += 4) {
          const p = path.getPointAtLength(at).matrixTransform(matrix);
          const distance = Math.hypot(p.x - event.clientX, p.y - event.clientY);
          if (distance < best) {
            best = distance;
            edgeId =
              path.closest(".react-flow__edge")?.getAttribute("data-id") ??
              undefined;
          }
        }
      });
    root.current?.dispatchEvent(
      new CustomEvent("studio:add", {
        bubbles: true,
        detail: { kind, context: { point, edgeId } },
      }),
    );
    localStorage.setItem("atelier.workflow.hint", "seen");
    setHint(false);
  };
  return (
    <ContextMenu>
      <ContextMenuTrigger asChild disabled={readonly}>
        <div
          ref={root}
          className="wf-canvas"
          data-arranging={arranging}
          data-entrance={entrance}
          aria-label={
            readonly ? "Read-only workflow canvas" : "Workflow canvas"
          }
          onContextMenu={(e) => {
            const id = (e.target as HTMLElement)
              .closest(".react-flow__node[data-id]")
              ?.getAttribute("data-id");
            if (id) select([id]);
            else select([]);
          }}
          onDragOver={(e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = "copy";
          }}
          onDrop={drop}
        >
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            snapToGrid
            snapGrid={[16, 16]}
            minZoom={0.25}
            maxZoom={1.75}
            panOnScroll
            zoomOnPinch
            zoomOnScroll={false}
            panOnDrag
            selectionOnDrag={false}
            selectionKeyCode="Shift"
            multiSelectionKeyCode="Shift"
            deleteKeyCode={null}
            disableKeyboardA11y
            nodesDraggable={!readonly}
            nodesConnectable={!readonly}
            edgesFocusable={!readonly}
            onlyRenderVisibleElements={nodes.length > 60}
            defaultViewport={doc.viewport ?? undefined}
            fitView={!doc.viewport}
            fitViewOptions={{ padding: 0.15 }}
            onNodesChange={changed}
            onEdgesChange={selectedChanges}
            onEdgeMouseEnter={(_, edge) => setHoveredEdge(edge.id)}
            onEdgeMouseLeave={() => setHoveredEdge(undefined)}
            onNodeDragStart={() => {
              setArranging(false);
              begin();
            }}
            onNodeDragStop={end}
            onSelectionDragStart={begin}
            onSelectionDragStop={end}
            onPaneClick={() => select([])}
            onConnect={(c) =>
              edit((d) => ({
                ...d,
                graph: connect(
                  d.graph,
                  c.source,
                  c.target,
                  c.sourceHandle ?? "out",
                ),
              }))
            }
            onConnectEnd={connectEnd}
            isValidConnection={(c) =>
              canConnect(doc, c.source, c.target, c.sourceHandle ?? "out")
            }
            onMoveEnd={(event, v) => {
              // Initial fit is presentation, not a user edit. Explicit controls
              // and real pan/zoom gestures still persist the chosen viewport.
              if (!readonly && (event || viewportIntent.current))
                edit(
                  (d) => ({ ...d, graph: { ...d.graph, viewport: v } }),
                  "viewport",
                );
              viewportIntent.current = false;
            }}
          >
            <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
            {large && minimap && (
              <MiniMap
                className="wf-minimap"
                pannable
                zoomable
                nodeColor={(n) => {
                  const b = doc.nodes.find((b) => b.id === n.id);
                  return b
                    ? `var(--cat-${registry[b.kind].tone})`
                    : "var(--note-amber)";
                }}
              />
            )}
          </ReactFlow>
          {hint && !readonly && (
            <p className="wf-canvas-hint">
              Drag blocks from the left, or hover a connection and press +
            </p>
          )}
          <div className="wf-canvas-controls">
            <IconButton
              label="Zoom out"
              onClick={() => moveView(() => flow.zoomOut({ duration }))}
            >
              <Minus />
            </IconButton>
            <Button
              variant="ghost"
              aria-label="Zoom 100%"
              onClick={() => moveView(() => flow.zoomTo(1, { duration }))}
            >
              {Math.round(viewport.zoom * 100)}%
            </Button>
            <IconButton
              label="Zoom in"
              onClick={() => moveView(() => flow.zoomIn({ duration }))}
            >
              <Plus />
            </IconButton>
            <IconButton
              label="Fit view"
              onClick={() =>
                moveView(() => flow.fitView({ duration, padding: 0.15 }))
              }
            >
              <Maximize />
            </IconButton>
            {!readonly && (
              <IconButton label="Tidy up" onClick={tidy}>
                <LayoutGrid />
              </IconButton>
            )}
            <IconButton label="Outline view" onClick={outline}>
              <List />
            </IconButton>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <IconButton label="Canvas actions">
                  <StickyNote />
                </IconButton>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem
                  disabled={readonly}
                  onClick={() => add({ point: center() })}
                >
                  Add block
                </DropdownMenuItem>
                <DropdownMenuItem onClick={tidy} disabled={readonly}>
                  Tidy up
                </DropdownMenuItem>
                <DropdownMenuItem
                  onClick={() => moveView(() => flow.fitView({ duration }))}
                >
                  Fit view
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
          {!readonly && (
            <IconButton
              className="wf-add-floating"
              label="Add a block"
              onClick={() => add({ point: center() })}
            >
              <Plus />
            </IconButton>
          )}
        </div>
      </ContextMenuTrigger>
      <ContextMenuContent>
        {selection.length ? (
          <>
            <ContextMenuItem onSelect={() => action("rename-block")}>
              Rename
            </ContextMenuItem>
            <ContextMenuItem onSelect={() => action("duplicate-block")}>
              Duplicate
            </ContextMenuItem>
            <ContextMenuItem onSelect={() => action("copy")}>
              Copy
            </ContextMenuItem>
            <ContextMenuItem onSelect={() => action("disable-block")}>
              Enable / Disable
            </ContextMenuItem>
            <ContextMenuSeparator />
            <ContextMenuItem
              className="text-danger"
              onSelect={() => action("delete-block")}
            >
              Delete
            </ContextMenuItem>
          </>
        ) : (
          <>
            <ContextMenuItem onSelect={() => add({ point: center() })}>
              Add block
            </ContextMenuItem>
            <ContextMenuItem onSelect={() => action("paste")}>
              Paste
            </ContextMenuItem>
            <ContextMenuItem onSelect={() => action("add-note")}>
              Add note
            </ContextMenuItem>
            <ContextMenuItem onSelect={tidy}>Tidy up</ContextMenuItem>
            <ContextMenuItem
              onSelect={() => moveView(() => flow.fitView({ duration }))}
            >
              Fit view
            </ContextMenuItem>
          </>
        )}
      </ContextMenuContent>
    </ContextMenu>
  );
});

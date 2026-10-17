import { useEffect, useRef, useState } from "react";
import {
  useBlocker,
  useNavigate,
  useParams,
  useSearchParams,
} from "react-router";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { X, CircleAlert, Ban } from "lucide-react";
import { api } from "@/lib/api";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import { useUI } from "@/stores/ui";
import { Button } from "@/components/ui/button";
import { IconButton } from "@/components/app/IconButton";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  Drawer,
  DrawerContent,
  DrawerTitle,
  DrawerDescription,
} from "@/components/ui/drawer";
import {
  Sheet,
  SheetContent,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { FileSaveDialog } from "@/components/app/FileSaveDialog";
import {
  StudioContext,
  createStudioStore,
  useStudio,
  type StudioStore,
} from "./store";
import { useAutosave } from "./useAutosave";
import { useResources } from "./api";
import {
  addBlock,
  clone,
  connect,
  newId,
  pasteRemap,
  outlineTree,
  validate,
} from "./graph";
import { Canvas, type CanvasActions, type AddContext } from "./Canvas";
import { BlocksPanel } from "./BlocksPanel";
import { QuickAdd } from "./QuickAdd";
import { availability, type CatalogKind } from "./registry";
import { StudioTopBar } from "./StudioTopBar";
import { Inspector } from "./Inspector";
import { Outline } from "./Outline";
import { RunActions } from "./RunActions";
import { BlockRunInputs } from "./BlockRunInputs";
import { VersionsPanel } from "./VersionsPanel";
import { RunInputs } from "./RunInputs";
import { RunCard } from "./RunCard";
import { useGraphRuns } from "./useGraphRuns";
import type { Definition, Doc, Issue, Kind } from "./types";
import type { components } from "@/lib/api-types";
import "./studio.css";
import { promptPreview } from "./preview";
export function Studio() {
  const { workflowId } = useParams();
  const q = useQuery({
    queryKey: ["workflow-definition", workflowId],
    queryFn: () => api<Definition>(`/workflows/defs/${workflowId}`),
    enabled: !!workflowId,
  });
  return q.data ? (
    <LoadedStudio key={q.data.id} definition={q.data} />
  ) : (
    <div className="p-8">
      <p role="status">
        {q.isError ? "This workflow couldn't be opened." : "Loading workflow…"}
      </p>
      {q.isError && (
        <Button variant="outline" onClick={() => void q.refetch()}>
          Try again
        </Button>
      )}
    </div>
  );
}
function LoadedStudio({ definition }: { definition: Definition }) {
  const [store] = useState(() => createStudioStore(definition));
  return (
    <StudioContext.Provider value={store}>
      <StudioEditor store={store} />
    </StudioContext.Provider>
  );
}
export function StudioEditor({
  store,
  preview = false,
  initialView,
  initialPanel,
  initialQuick = false,
  previewRun,
  initialBlockRun,
}: {
  store: StudioStore;
  preview?: boolean;
  initialView?: "canvas" | "outline";
  initialPanel?: "inspector" | "settings" | "problems" | "run" | "versions";
  initialQuick?: boolean;
  previewRun?: import("./types").Run;
  initialBlockRun?: { mode: "run" | "test"; nodeId: string };
}) {
  const draft = useStudio((s) => s.draft),
    selection = useStudio((s) => s.selection),
    edit = useStudio((s) => s.edit),
    select = useStudio((s) => s.select),
    saveState = useStudio((s) => s.saveState),
    conflict = useStudio((s) => s.conflict);
  const phone = useMediaQuery("(max-width:767px)"),
    tablet = useMediaQuery("(min-width:768px) and (max-width:1023px)");
  const { catalog, error: resourceError } = useResources();
  const navigate = useNavigate(),
    query = useQueryClient();
  const [search] = useSearchParams();
  const [view, setView] = useState<"canvas" | "outline" | undefined>(
      initialView,
    ),
    [panel, setPanel] = useState<
      "inspector" | "settings" | "problems" | "run" | "versions" | null
    >(
      initialPanel ??
        (search.has("run") ||
        sessionStorage.getItem(
          "atelier.studio-panel:" + store.getState().id,
        ) === "run"
          ? "run"
          : null),
    );
  const [quick, setQuick] = useState<AddContext>(),
    [quickOpen, setQuickOpen] = useState(initialQuick),
    [minimap, setMinimap] = useState(true),
    [json, setJson] = useState(false),
    [save, setSave] = useState(false),
    [notice, setNotice] = useState("");
  const [remote, setRemote] = useState<Issue[]>([]);
  const importFile = useRef<HTMLInputElement>(null),
    root = useRef<HTMLDivElement>(null),
    canvas = useRef<CanvasActions>(null);
  const copied = useRef<Pick<Doc, "nodes" | "edges" | "notes"> | undefined>(
    undefined,
  );
  const [selectedRunId, setSelectedRunId] = useState<string | undefined>(
    () =>
      sessionStorage.getItem("atelier.studio-run:" + store.getState().id) ??
      undefined,
  );
  const [showInputs, setShowInputs] = useState(false);
  const [blockRun, setBlockRun] = useState<
    | {
        mode: "run" | "test";
        nodeId: string;
      }
    | undefined
  >(initialBlockRun);
  const autosave = useAutosave(store, !preview);
  const { runs, accepted, connection } = useGraphRuns(selectedRunId);
  const latest =
    previewRun ??
    runs.find((r) => r.id === selectedRunId) ??
    runs.find((r) => r.def_id === store.getState().id && r.mode !== "test");
  const acceptRun = (r: import("./types").Run) => {
    accepted(r);
    setSelectedRunId(r.id);
    sessionStorage.setItem("atelier.studio-run:" + store.getState().id, r.id);
    setShowInputs(false);
    setBlockRun(undefined);
  };
  const outline = view === "outline" || (!view && phone);
  const structural = validate(draft.graph);
  const issues = [
    ...structural,
    ...remote.filter(
      (i) => !structural.some((s) => JSON.stringify(s) === JSON.stringify(i)),
    ),
  ];
  const errors = issues.filter((i) => i.severity === "error");
  const blocker = useBlocker(
    ({ currentLocation, nextLocation }) =>
      !preview &&
      currentLocation.pathname !== nextLocation.pathname &&
      JSON.stringify(store.getState().draft) !== store.getState().saved,
  );
  useEffect(() => {
    const before = useUI.getState().collapsed;
    useUI.getState().set({ collapsedBeforeStudio: before, collapsed: true });
    return () =>
      useUI
        .getState()
        .set({ collapsed: before, collapsedBeforeStudio: undefined });
  }, []);
  useEffect(() => {
    if (
      panel !== "run" &&
      selection.some((id) => draft.graph.nodes.some((n) => n.id === id))
    )
      setPanel("inspector");
    else if (panel === "inspector") setPanel(null);
  }, [selection]);
  useEffect(() => {
    if (preview) return;
    const controller = new AbortController();
    setRemote([]);
    const timer = setTimeout(() => {
      void fetch(`/api/workflows/defs/${store.getState().id}/validate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: controller.signal,
        body: JSON.stringify({ graph: draft.graph }),
      })
        .then(async (r) => {
          if (!r.ok) throw new Error("Settings need attention");
          return r.json() as Promise<components["schemas"]["ValidationResult"]>;
        })
        .then(
          (v) => {
            if (!controller.signal.aborted) setRemote(v.issues);
          },
          () => {
            if (!controller.signal.aborted)
              setRemote([
                {
                  code: "settings",
                  message:
                    "Some settings need attention. Check required values and reference names.",
                  node_id: null,
                  severity: "error",
                },
              ]);
          },
        );
    }, 350);
    return () => {
      controller.abort();
      clearTimeout(timer);
    };
  }, [draft.graph, preview, store]);
  const openAdd = (context: AddContext = {}) => {
    setQuick(context);
    setQuickOpen(true);
  };
  const add = (kind: CatalogKind, context = quick ?? {}) => {
    if (!availability(kind, catalog).available) return;
    const doc = store.getState().draft.graph;
    const selected = doc.nodes.find((n) => n.id === selection[0]);
    const previous = doc.nodes.find((n) => n.id === context.source) ?? selected;
    const edge = doc.edges.find((e) => e.id === context.edgeId);
    const target = edge && doc.nodes.find((n) => n.id === edge.target);
    const point =
      context.point ??
      (target
        ? { x: target.position.x, y: target.position.y - 112 }
        : previous
          ? { x: previous.position.x, y: previous.position.y + 208 }
          : (canvas.current?.center() ?? { x: 0, y: 0 }));
    if (kind === "note") {
      const id = newId("note");
      edit((d) => ({
        ...d,
        graph: {
          ...d.graph,
          notes: [
            ...d.graph.notes,
            {
              id,
              position: point,
              size: { w: 220, h: 160 },
              tone: "amber",
              text: "",
            },
          ],
        },
      }));
      select([id]);
    } else {
      let graph = addBlock(doc, kind as Kind, point, previous?.id, edge?.id);
      if (graph === doc) {
        setNotice("Use at most 40 blocks and one Start.");
        return;
      }
      const node = graph.nodes.at(-1)!;
      if (context.source && context.port) {
        graph = {
          ...graph,
          edges: graph.edges.filter(
            (e) => !(e.source === context.source && e.target === node.id),
          ),
        };
        graph = connect(graph, context.source, node.id, context.port);
      }
      edit((d) => ({ ...d, graph }));
      select([node.id]);
      localStorage.setItem("atelier.workflow.hint", "seen");
      canvas.current?.added();
    }
  };
  const addRef = useRef(add);
  addRef.current = add;
  useEffect(() => {
    const listener = (e: Event) => {
      const event = e as CustomEvent<{
        kind: CatalogKind;
        context: AddContext;
      }>;
      addRef.current(event.detail.kind, event.detail.context);
    };
    const element = root.current!;
    element.addEventListener("studio:add", listener);
    return () => element.removeEventListener("studio:add", listener);
  }, []);
  const run = () => {
    setShowInputs(
      !latest ||
        !["queued", "running", "paused", "cancelling"].includes(latest.state),
    );
    setBlockRun(undefined);
    if (errors.length) setPanel("problems");
    else setPanel("run");
  };
  const action = async (name: string) => {
    const s = store.getState();
    if (["copy", "duplicate-block"].includes(name)) {
      const fragment = {
        nodes: s.draft.graph.nodes.filter((n) => s.selection.includes(n.id)),
        edges: s.draft.graph.edges.filter(
          (e) =>
            s.selection.includes(e.source) && s.selection.includes(e.target),
        ),
        notes: s.draft.graph.notes.filter((n) => s.selection.includes(n.id)),
      };
      copied.current = clone(fragment);
      if (name === "duplicate-block")
        edit((d) => ({ ...d, graph: pasteRemap(d.graph, fragment) }));
      else
        void navigator.clipboard
          .writeText(JSON.stringify(fragment))
          .catch(() => {});
    } else if (name === "paste" && copied.current)
      edit((d) => ({
        ...d,
        graph: pasteRemap(d.graph, copied.current!, canvas.current?.center()),
      }));
    else if (name === "delete-block") s.remove();
    else if (name === "disable-block")
      edit((d) => ({
        ...d,
        graph: {
          ...d.graph,
          nodes: d.graph.nodes.map((n) =>
            s.selection.includes(n.id) && n.kind !== "start"
              ? { ...n, disabled: !n.disabled }
              : n,
          ),
        },
      }));
    else if (name === "rename-block") {
      setPanel("inspector");
      requestAnimationFrame(() =>
        root.current
          ?.querySelector<HTMLInputElement>("[aria-label='Block name']")
          ?.focus(),
      );
    } else if (name === "add-note")
      add("note", { point: canvas.current?.center() });
    else if (name === "run-workflow") run();
    else if (name === "cancel-run" && latest)
      void api(`/workflows/runs/${latest.id}/v2/cancel`, {});
    else if (["settings", "problems", "versions"].includes(name))
      setPanel(name as "settings" | "problems" | "versions");
    else if (name === "view") {
      setView(outline ? "canvas" : "outline");
      select([]);
    } else if (name === "minimap") setMinimap((v) => !v);
    else if (name === "json") setJson(true);
    else if (name === "export") {
      if ((await autosave.flush()) || preview) setSave(true);
      else
        setNotice(
          "Save the workflow before exporting, or resolve the conflict.",
        );
    } else if (name === "import") importFile.current?.click();
    else if (name === "duplicate" && !preview) {
      if (!(await autosave.flush())) {
        setNotice("Save the workflow before duplicating.");
        return;
      }
      try {
        const def = await api<Definition>(
          `/workflows/defs/${store.getState().id}/duplicate`,
          {},
        );
        navigate(`/workflows/${def.id}`);
      } catch {
        setNotice("Couldn't duplicate this workflow.");
      }
    } else if (name === "delete" && !preview) {
      try {
        await api(
          `/workflows/defs/${store.getState().id}`,
          undefined,
          "DELETE",
        );
        store.getState().status("saved");
        store.setState({ saved: JSON.stringify(store.getState().draft) });
        void query.invalidateQueries({ queryKey: ["workflow-definitions"] });
        navigate("/workflows");
      } catch {
        setNotice("Couldn't delete this workflow.");
      }
    }
  };
  const actionRef = useRef(action);
  actionRef.current = action;
  useEffect(() => {
    const listener = (event: Event) =>
      void actionRef.current((event as CustomEvent<string>).detail);
    window.addEventListener("studio:command", listener);
    return () => window.removeEventListener("studio:command", listener);
  }, []);
  const onKey = (e: React.KeyboardEvent) => {
    const form = (e.target as HTMLElement).closest(
      "input,textarea,select,[contenteditable=true],[role=combobox],[role=dialog],[role=menu],[role=listbox]",
    );
    if (form) return;
    if (panel === "run" && !["escape", "f"].includes(e.key.toLowerCase()))
      return;
    const mod = e.metaKey || e.ctrlKey;
    const key = e.key.toLowerCase();
    const s = store.getState();
    if (
      phone &&
      (!outline || !outlineTree(s.draft.graph)) &&
      (["n", "delete", "backspace"].includes(key) ||
        (key === "/" && !mod) ||
        (mod && ["d", "v"].includes(key)))
    )
      return;
    const focusedBlock = (e.target as HTMLElement).closest(
      ".react-flow__node[data-id]",
    );
    if (
      !mod &&
      (key === "enter" || key === " ") &&
      focusedBlock &&
      !(e.target as HTMLElement).closest("button")
    ) {
      e.preventDefault();
      select([focusedBlock.getAttribute("data-id")!]);
      return;
    }
    if (mod && key === "z") {
      e.preventDefault();
      e.stopPropagation();
      e.shiftKey ? s.redo() : s.undo();
    } else if (mod && key === "enter") {
      e.preventDefault();
      run();
    } else if (key === "n" || (key === "/" && !mod)) {
      e.preventDefault();
      openAdd();
    } else if (
      (key === "delete" || key === "backspace") &&
      s.selection.length
    ) {
      e.preventDefault();
      s.remove();
    } else if (mod && key === "a") {
      e.preventDefault();
      s.select(s.draft.graph.nodes.map((n) => n.id));
    } else if (mod && (key === "c" || key === "d")) {
      const fragment = {
        nodes: s.draft.graph.nodes.filter((n) => s.selection.includes(n.id)),
        edges: s.draft.graph.edges.filter(
          (edge) =>
            s.selection.includes(edge.source) &&
            s.selection.includes(edge.target),
        ),
        notes: s.draft.graph.notes.filter((n) => s.selection.includes(n.id)),
      };
      copied.current = clone(fragment);
      e.preventDefault();
      if (key === "d")
        edit((d) => ({ ...d, graph: pasteRemap(d.graph, fragment) }));
      else
        void navigator.clipboard
          .writeText(JSON.stringify(fragment))
          .catch(() => {});
    } else if (mod && key === "v" && copied.current) {
      e.preventDefault();
      edit((d) => ({ ...d, graph: pasteRemap(d.graph, copied.current!) }));
    } else if (mod && key === "/") {
      e.preventDefault();
      e.stopPropagation();
      edit((d) => ({
        ...d,
        graph: {
          ...d.graph,
          nodes: d.graph.nodes.map((n) =>
            s.selection.includes(n.id) && n.kind !== "start"
              ? { ...n, disabled: !n.disabled }
              : n,
          ),
        },
      }));
    } else if (key === "f" || (e.shiftKey && key === "1")) {
      e.preventDefault();
      canvas.current?.fit();
    } else if (mod && key === "0") {
      e.preventDefault();
      canvas.current?.zoom100();
    } else if (
      e.altKey &&
      ["arrowup", "arrowdown", "arrowleft", "arrowright"].includes(key)
    ) {
      e.preventDefault();
      edit((d) => ({
        ...d,
        graph: {
          ...d.graph,
          nodes: d.graph.nodes.map((n) =>
            s.selection.includes(n.id)
              ? {
                  ...n,
                  position: {
                    x:
                      n.position.x +
                      (key === "arrowright"
                        ? 16
                        : key === "arrowleft"
                          ? -16
                          : 0),
                    y:
                      n.position.y +
                      (key === "arrowdown" ? 16 : key === "arrowup" ? -16 : 0),
                  },
                }
              : n,
          ),
        },
      }));
    } else if (key === "escape") {
      s.select([]);
      setPanel(null);
    } else if (key === "f2") {
      e.preventDefault();
      setPanel("inspector");
      requestAnimationFrame(() =>
        root.current
          ?.querySelector<HTMLInputElement>("[aria-label='Block name']")
          ?.focus(),
      );
    } else if (
      ["arrowup", "arrowdown"].includes(key) &&
      s.selection.length === 1
    ) {
      const id =
        key === "arrowup"
          ? s.draft.graph.edges.find((e) => e.target === s.selection[0])?.source
          : s.draft.graph.edges.find((e) => e.source === s.selection[0])
              ?.target;
      if (id) {
        e.preventDefault();
        s.select([id]);
        requestAnimationFrame(() =>
          root.current
            ?.querySelector<HTMLElement>(`.react-flow__node[data-id='${id}']`)
            ?.focus(),
        );
      }
    }
  };
  useEffect(() => {
    if (preview) return;
    const key = "atelier.studio-panel:" + store.getState().id;
    if (panel === "run") sessionStorage.setItem(key, "run");
    else sessionStorage.removeItem(key);
  }, [panel, preview, store]);
  const close = () => {
    setPanel(null);
    select([]);
  };
  const node = draft.graph.nodes.find((n) => n.id === selection[0]);
  let previewMessages: { role: string; content: string }[] | undefined;
  let previewNotice = "";
  if (json && node?.kind === "generate") {
    try {
      previewMessages = promptPreview(draft.graph, node, latest);
    } catch (e) {
      previewNotice =
        e instanceof Error
          ? e.message
          : "An input isn't available for this preview.";
    }
  }
  const panelContent =
    panel === "versions" ? (
      <VersionsPanel
        close={close}
        previewSnapshots={
          preview
            ? [
                {
                  id: "synthetic-version",
                  def_id: store.getState().id,
                  graph_hash: "synthetic",
                  graph: draft.graph,
                  label: "Synthetic named version",
                  created_at: "2026-10-13T12:00:00Z",
                  run_count: 2,
                },
              ]
            : undefined
        }
      />
    ) : panel === "inspector" || panel === "settings" ? (
      <Inspector
        structureDisabled={phone && !outlineTree(draft.graph)}
        settings={panel === "settings"}
        close={close}
        latest={latest}
        preview={() => setJson(true)}
      />
    ) : panel === "problems" ? (
      <div className="wf-inspector">
        <header className="wf-panel-head">
          <h2>Problems</h2>
          <IconButton label="Close Problems" onClick={close}>
            <X />
          </IconButton>
        </header>
        <div className="wf-panel-body">
          {issues.length ? (
            issues.map((issue, i) => (
              <Button
                key={i}
                variant="ghost"
                className="wf-problem-row"
                onClick={() => {
                  if (issue.node_id) {
                    select([issue.node_id]);
                    canvas.current?.problem(issue.node_id);
                    setPanel("inspector");
                    requestAnimationFrame(() =>
                      root.current
                        ?.querySelector<HTMLElement>(
                          ".wf-panel-body textarea,.wf-panel-body input",
                        )
                        ?.focus(),
                    );
                  } else {
                    setPanel("settings");
                  }
                }}
              >
                <span>
                  {issue.severity === "info" ? <Ban /> : <CircleAlert />}
                </span>
                <span>
                  {issue.node_id && (
                    <span className="block text-xs text-fg-3">
                      {
                        draft.graph.nodes.find((n) => n.id === issue.node_id)
                          ?.title
                      }
                    </span>
                  )}
                  {issue.message}
                </span>
              </Button>
            ))
          ) : (
            <p className="wf-empty-output">No problems. Ready to run.</p>
          )}
        </div>
      </div>
    ) : panel === "run" ? (
      <div className="wf-inspector">
        <header className="wf-panel-head">
          <h2>Run</h2>
          <IconButton label="Close Run" onClick={close}>
            <X />
          </IconButton>
        </header>
        <div className="wf-panel-body">
          {blockRun ? (
            <BlockRunInputs
              key={blockRun.nodeId + blockRun.mode}
              doc={draft.graph}
              defId={store.getState().id}
              nodeId={blockRun.nodeId}
              mode={blockRun.mode}
              beforeRun={autosave.flush}
              accepted={acceptRun}
              previewPlan={
                preview
                  ? {
                      eligible: blockRun.mode === "run",
                      reason: "Run the workflow once first.",
                      source_run_id:
                        blockRun.mode === "run" ? "synthetic-source-run" : null,
                      node_ids: [],
                    }
                  : undefined
              }
            />
          ) : !latest || showInputs ? (
            <RunInputs
              doc={draft.graph}
              defId={store.getState().id}
              beforeRun={autosave.flush}
              accepted={acceptRun}
              previous={latest}
              preview={preview}
            />
          ) : null}
          {connection !== "Connected" && (
            <p role="status" className="wf-help">
              {connection}
            </p>
          )}
          {latest && (
            <RunCard
              key={latest.id}
              run={latest}
              preview={preview}
              selected={selection[0]}
              onSelect={(id) => {
                select([id]);
                canvas.current?.problem(id);
              }}
            />
          )}
        </div>
      </div>
    ) : null;
  return (
    <RunActions.Provider
      value={{
        defId: store.getState().id,
        revision: store.getState().revision,
        act: (mode, nodeId) => {
          setBlockRun({ mode, nodeId });
          setPanel("run");
        },
      }}
    >
      <div className="wf-studio" ref={root} onKeyDown={onKey} tabIndex={-1}>
        <StudioTopBar
          problems={errors.length}
          run={run}
          action={(name) => void action(name)}
          outline={outline}
          minimap={minimap}
          retry={autosave.retry}
          running={
            !!latest &&
            ["queued", "running", "cancelling"].includes(latest.state)
          }
        />
        {saveState === "conflict" && conflict && (
          <div className="wf-conflict" role="alert">
            <span>This workflow changed on another device.</span>
            <Button
              variant="outline"
              onClick={() => store.getState().loaded(conflict)}
            >
              Load latest
            </Button>
            <Button onClick={() => void autosave.keepMine()}>Keep mine</Button>
          </div>
        )}
        {notice && (
          <p role="alert" className="wf-editor-notice">
            {notice}
            <Button variant="ghost" onClick={() => setNotice("")}>
              Dismiss
            </Button>
          </p>
        )}
        {resourceError && (
          <p role="alert" className="wf-editor-notice">
            Block availability couldn't be loaded. Check your connection.
          </p>
        )}
        <div className="wf-studio-body">
          {!outline && !phone && (
            <BlocksPanel catalog={catalog} add={(kind) => add(kind, {})} />
          )}
          {outline ? (
            <Outline add={openAdd} run={panel === "run" ? latest : undefined} />
          ) : (
            <Canvas
              ref={canvas}
              action={(name) => void action(name)}
              issues={issues}
              add={openAdd}
              outline={() => setView("outline")}
              readonly={phone}
              minimap={minimap}
              run={panel === "run" ? latest : undefined}
            />
          )}
          {!phone && !tablet && panelContent && (
            <aside
              className="wf-right"
              aria-label={
                panel === "inspector" ? "Inspector" : (panel ?? undefined)
              }
            >
              {panelContent}
            </aside>
          )}
        </div>
        {phone && (
          <Drawer
            open={!!panelContent}
            onOpenChange={(v) => !v && close()}
            snapPoints={[0.6, 0.95]}
            activeSnapPoint={0.95}
          >
            <DrawerContent className="wf-phone-panel">
              <DrawerTitle className="sr-only">
                {panel === "inspector" ? (node?.title ?? "Inspector") : panel}
              </DrawerTitle>
              <DrawerDescription className="sr-only">
                Edit this workflow's settings.
              </DrawerDescription>
              {panelContent}
            </DrawerContent>
          </Drawer>
        )}
        {tablet && (
          <Sheet open={!!panelContent} onOpenChange={(v) => !v && close()}>
            <SheetContent className="wf-tablet-panel" side="right">
              <SheetTitle className="sr-only">
                {panel === "inspector" ? "Inspector" : panel}
              </SheetTitle>
              <SheetDescription className="sr-only">
                Edit this workflow's settings.
              </SheetDescription>
              {panelContent}
            </SheetContent>
          </Sheet>
        )}
        <QuickAdd
          open={quickOpen}
          close={() => setQuickOpen(false)}
          add={(kind) => add(kind)}
          catalog={catalog}
          anchor={quick?.anchor}
        />
        <input
          ref={importFile}
          aria-label="Import workflow JSON"
          className="sr-only"
          type="file"
          accept=".json"
          onChange={async (e) => {
            const file = e.target.files?.[0];
            if (!file) return;
            e.target.value = "";
            if (file.size > 512 * 1024) {
              setNotice("Choose JSON smaller than 512 KB.");
              return;
            }
            try {
              const imported = JSON.parse(await file.text()) as
                Doc | { graph: Doc };
              const graph = "graph" in imported ? imported.graph : imported;
              const response = await api<
                components["schemas"]["ValidationResult"]
              >(`/workflows/defs/${store.getState().id}/validate`, { graph });
              if (response.issues.some((i) => i.code === "settings"))
                throw new Error();
              if (!response.graph) throw new Error();
              edit((d) => ({ ...d, graph: response.graph as Doc }));
            } catch {
              setNotice(
                "This JSON isn't a supported workflow. Check its blocks and settings.",
              );
            }
          }}
        />
        <Dialog open={json} onOpenChange={setJson}>
          <DialogContent className="max-h-[85dvh] overflow-y-auto">
            <DialogTitle>
              {node?.kind === "generate" ? "Preview prompt" : "Workflow JSON"}
            </DialogTitle>
            <DialogDescription>
              {node?.kind === "generate"
                ? "These are your exact message templates. Variables use the previous blocks' values when the workflow runs; no hidden text is added."
                : "The current workflow definition."}
            </DialogDescription>
            {previewNotice && (
              <p role="status" className="wf-help">
                {previewNotice} The unfilled templates are shown below.
              </p>
            )}
            <pre className="wf-output-text">
              {JSON.stringify(
                node?.kind === "generate"
                  ? (previewMessages ?? [
                      { role: "system", content: node.config.instructions },
                      { role: "user", content: node.config.prompt },
                    ])
                  : draft.graph,
                null,
                2,
              )}
            </pre>
          </DialogContent>
        </Dialog>
        {save && (
          <FileSaveDialog
            initial="json"
            title="Save workflow"
            closeLabel="Close workflow save"
            preview={preview ? "ready" : undefined}
            onClose={() => setSave(false)}
            options={[
              {
                format: "json",
                label: "Workflow (.json)",
                url: `/api/workflows/defs/${store.getState().id}`,
                filename: `Aether-workflow-${store.getState().id.slice(0, 8)}.json`,
              },
            ]}
          />
        )}
        <Dialog
          open={blocker.state === "blocked"}
          onOpenChange={(v) => {
            if (!v && blocker.state === "blocked") blocker.reset();
          }}
        >
          <DialogContent>
            <DialogTitle>Leave with unsaved changes?</DialogTitle>
            <DialogDescription>
              Your current changes haven't been saved. Stay here to retry
              saving.
            </DialogDescription>
            <div className="flex gap-2">
              <Button
                onClick={() => blocker.state === "blocked" && blocker.reset()}
              >
                Stay here
              </Button>
              <Button
                variant="outline"
                onClick={() => blocker.state === "blocked" && blocker.proceed()}
              >
                Leave without saving
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </RunActions.Provider>
  );
}

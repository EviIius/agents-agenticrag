import { useMemo, useRef, useState } from "react";
import { Link } from "react-router";
import { Button } from "@/components/ui/button";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import {
  Drawer,
  DrawerContent,
  DrawerTitle,
  DrawerDescription,
} from "@/components/ui/drawer";
import { StudioContext, createStudioStore } from "./store";
import { Canvas, type CanvasActions } from "./Canvas";
import { Outline } from "./Outline";
import { RunCard } from "./RunCard";
import type { Definition, Run } from "./types";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import "./studio.css";
export function RunView({
  run,
  legacyPanel,
}: {
  run: Run;
  legacyPanel?: React.ReactNode;
}) {
  const store = useMemo(
    () =>
      createStudioStore({
        id: run.def_id ?? run.id,
        name: run.def_name,
        description: "",
        icon: "workflow",
        graph: run.graph,
        graph_hash: run.graph_hash ?? "",
        version: 1,
        template_id: null,
        archived_at: null,
        created_at: run.created_at,
        updated_at: run.updated_at,
      }),
    [run.id],
  );
  const phone = useMediaQuery("(max-width:767px)"),
    [outline, setOutline] = useState(false),
    [open, setOpen] = useState(true),
    [selected, setSelected] = useState<string>();
  const canvas = useRef<CanvasActions>(null);
  const q = useQuery({
    queryKey: ["workflow-definition", run.def_id],
    queryFn: () => api<Definition>(`/workflows/defs/${run.def_id}`),
    enabled: !!run.def_id,
  });
  const panel = legacyPanel ?? (
    <RunCard
      key={run.id}
      run={run}
      selected={selected}
      onSelect={(id) => {
        setSelected(id);
        store.getState().select([id]);
        canvas.current?.problem(id);
      }}
    />
  );
  const changed =
    q.data && JSON.stringify(q.data.graph) !== JSON.stringify(run.graph);
  return (
    <StudioContext.Provider value={store}>
      <div className="wf-studio" aria-label="Saved workflow run">
        <header className="wf-topbar">
          <Button variant="ghost" asChild>
            <Link to="/workflows/runs">All runs</Link>
          </Button>
          <h1 className="min-w-0 truncate font-semibold">{run.def_name}</h1>
          <span className="wf-help">
            {run.mode === "test" ? "Block test" : run.state}
          </span>
          <div className="flex-1" />
          {run.def_id && (
            <Button variant="outline" asChild>
              <Link to={`/workflows/${run.def_id}`}>Edit workflow</Link>
            </Button>
          )}
          {phone && <Button onClick={() => setOpen(true)}>Run details</Button>}
        </header>
        <div className="wf-run-view-banner">
          Viewing a run from {new Date(run.created_at).toLocaleString()}.{" "}
          {changed
            ? "The current workflow has changed."
            : "This saved version is read-only."}
        </div>
        <div className="wf-studio-body">
          {phone || outline ? (
            <Outline run={run} add={() => {}} />
          ) : (
            <Canvas
              ref={canvas}
              run={run}
              readonly
              issues={[]}
              add={() => {}}
              action={() => {}}
              outline={() => setOutline(true)}
            />
          )}
          {!phone && (
            <aside className="wf-right wf-inspector">
              <div className="wf-panel-body">{panel}</div>
            </aside>
          )}
        </div>
        {phone && (
          <Drawer open={open} onOpenChange={setOpen}>
            <DrawerContent className="max-h-[95dvh]">
              <DrawerTitle className="sr-only">Run details</DrawerTitle>
              <DrawerDescription className="sr-only">
                Saved states and results for this run.
              </DrawerDescription>
              <div className="wf-panel-body">{panel}</div>
            </DrawerContent>
          </Drawer>
        )}
      </div>
    </StudioContext.Provider>
  );
}

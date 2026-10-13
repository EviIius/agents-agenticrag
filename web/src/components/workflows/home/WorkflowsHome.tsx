import { useRef, useState } from "react";
import { Link, useNavigate } from "react-router";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Workflow,
  Plus,
  MoreHorizontal,
  Play,
  ChevronRight,
  Circle,
  Copy,
  Trash2,
} from "lucide-react";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { IconButton } from "@/components/app/IconButton";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { FileSaveDialog } from "@/components/app/FileSaveDialog";
import { useWorkspace } from "@/components/app/WorkspaceNavigation";
import { useGraphRuns } from "../studio/useGraphRuns";
import { registry } from "../studio/registry";
import {
  getDefinitions,
  getTemplates,
  saveDefinition,
  useResources,
} from "../studio/api";
import { asDraft } from "../studio/store";
import { TextField } from "../studio/fields";
import type { Definition, Run, Doc, Template } from "../studio/types";
import { toast } from "sonner";
import { workflowIcons } from "../studio/icons";
import { blankDoc } from "../studio/graph";
export function WorkflowsHome() {
  const definitions = useQuery({
    queryKey: ["workflow-definitions"],
    queryFn: getDefinitions,
  });
  const templates = useQuery({
    queryKey: ["workflow-templates"],
    queryFn: getTemplates,
  });
  const { models } = useResources(),
    navigation = useWorkspace(),
    navigate = useNavigate(),
    query = useQueryClient();
  const { runs, connection, error } = useGraphRuns();
  const [busy, setBusy] = useState(false),
    [notice, setNotice] = useState("");
  const create = async (template_id?: string, graph?: Doc) => {
    if (busy) return;
    setBusy(true);
    setNotice("");
    const model = models.find(
      (m) => `${m.connection_id}/${m.model_id}` === navigation.modelKey,
    );
    try {
      const def = await api<Definition>("/workflows/defs", {
        ...(template_id
          ? {
              template_id,
              name: templates.data?.find((t) => t.id === template_id)?.name,
            }
          : {}),
        ...(graph ? { graph } : !template_id ? { graph: blankDoc() } : {}),
        ...(model && !graph
          ? {
              default_model: {
                connection_id: model.connection_id,
                model_id: model.model_id,
              },
            }
          : {}),
      });
      void query.invalidateQueries({ queryKey: ["workflow-definitions"] });
      navigate(`/workflows/${def.id}`, { state: navigation });
      if (template_id) toast("Created from template. Changes are yours.");
    } catch (e) {
      setNotice(
        e instanceof Error ? e.message : "Couldn't create the workflow.",
      );
    } finally {
      setBusy(false);
    }
  };
  return (
    <WorkflowHomeContent
      definitions={definitions}
      templates={templates}
      runs={runs}
      connection={connection}
      error={error}
      notice={notice}
      setNotice={setNotice}
      busy={busy}
      create={create}
      refresh={() =>
        void query.invalidateQueries({ queryKey: ["workflow-definitions"] })
      }
    />
  );
}
export function WorkflowHomeContent({
  definitions,
  templates,
  runs,
  connection,
  error,
  notice,
  setNotice,
  busy,
  create,
  refresh,
}: {
  definitions: {
    data?: Definition[];
    isLoading: boolean;
    isError: boolean;
    refetch: () => unknown;
  };
  templates: { data?: Template[] };
  runs: Run[];
  connection: string;
  error: string;
  notice: string;
  setNotice: (message: string) => void;
  busy: boolean;
  create: (templateId?: string, graph?: Doc) => Promise<void>;
  refresh: () => void;
}) {
  const importFile = useRef<HTMLInputElement>(null);
  return (
    <section className="wf-home" aria-label="Workflows">
      <header className="wf-home-header">
        <div>
          <h1>Workflows</h1>
          <p>
            Chain models, search, images and recordings into repeatable steps.
            <br />
            Runs keep going on your Mac when you close the app.
          </p>
        </div>
        <div className="flex shrink-0">
          <Button onClick={() => void create()} disabled={busy}>
            <Plus className="size-4" />
            New workflow
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <IconButton label="New workflow options">
                <MoreHorizontal />
              </IconButton>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              {templates.data?.map((t) => (
                <DropdownMenuItem key={t.id} onClick={() => void create(t.id)}>
                  {t.name}
                </DropdownMenuItem>
              ))}
              <DropdownMenuItem onClick={() => importFile.current?.click()}>
                Import JSON
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>
      <input
        ref={importFile}
        type="file"
        accept=".json,application/json"
        className="sr-only"
        aria-label="Import workflow JSON"
        onChange={async (e) => {
          const file = e.target.files?.[0];
          if (!file) return;
          e.target.value = "";
          if (file.size > 512 * 1024) {
            setNotice("Choose a workflow JSON file smaller than 512 KB.");
            return;
          }
          try {
            const value = JSON.parse(await file.text()) as Doc | { graph: Doc };
            await create("", "graph" in value ? value.graph : value);
          } catch {
            setNotice(
              "This JSON file isn't a supported workflow. Check the block types and settings.",
            );
          }
        }}
      />
      {(notice || definitions.isError || error) && (
        <p role="alert" className="text-sm text-danger">
          {notice || error || "Your workflows couldn't be loaded."}{" "}
          <Button variant="ghost" onClick={() => void definitions.refetch()}>
            Try again
          </Button>
        </p>
      )}
      {connection !== "Connected" && (
        <p role="status" className="wf-help">
          {connection}
        </p>
      )}
      {definitions.isLoading ? (
        <p role="status">Loading workflows…</p>
      ) : definitions.data?.length ? (
        <section className="wf-home-section" aria-label="Your workflows">
          <h2 className="wf-section-title">YOUR WORKFLOWS</h2>
          <div className="wf-card-grid">
            {definitions.data.map((def) => (
              <WorkflowCard
                key={def.id}
                definition={def}
                lastRun={runs.find((r) => r.def_id === def.id)}
                refresh={refresh}
              />
            ))}
          </div>
        </section>
      ) : (
        <div className="wf-home-empty">
          <h2>Build your first workflow</h2>
          <p>Pick a template or start blank. You can change every step.</p>
        </div>
      )}
      <section className="wf-home-section" aria-label="Workflow templates">
        <h2 className="wf-section-title">START FROM A TEMPLATE</h2>
        <div className="wf-template-chips">
          {templates.data?.map((t) => (
            <Button
              key={t.id}
              variant="outline"
              aria-label={`Use ${t.name} template`}
              disabled={busy}
              onClick={() => void create(t.id)}
            >
              <Workflow className="size-4" />
              {t.name}
            </Button>
          ))}
          <Button
            variant="outline"
            onClick={() => void create()}
            disabled={busy}
          >
            Start blank
          </Button>
        </div>
      </section>
      <section className="wf-home-section" aria-label="Recent workflow runs">
        <div className="flex justify-between gap-2">
          <h2 className="wf-section-title">RECENT RUNS</h2>
          <Button variant="ghost" asChild>
            <Link to="/workflows/runs">View all runs</Link>
          </Button>
        </div>
        <RunsList runs={runs.slice(0, 10)} />
      </section>
    </section>
  );
}
export function WorkflowCard({
  definition: def,
  lastRun,
  refresh,
}: {
  definition: Definition;
  lastRun?: Run;
  refresh: () => void;
}) {
  const Icon = workflowIcons[def.icon];
  const [rename, setRename] = useState(false),
    [name, setName] = useState(def.name),
    [save, setSave] = useState(false),
    [notice, setNotice] = useState("");
  const navigate = useNavigate();
  const operation = async (kind: "duplicate" | "delete" | "rename") => {
    try {
      if (kind === "duplicate") {
        const copy = await api<Definition>(
          `/workflows/defs/${def.id}/duplicate`,
          {},
        );
        navigate(`/workflows/${copy.id}`);
      } else if (kind === "delete")
        await api(`/workflows/defs/${def.id}`, undefined, "DELETE");
      else {
        await saveDefinition(def.id, { ...asDraft(def), name }, def.version);
        setRename(false);
      }
      refresh();
    } catch (e) {
      setNotice(
        e instanceof Error ? e.message : "The change couldn't be saved.",
      );
    }
  };
  const status = lastRun
    ? ["running", "queued"].includes(lastRun.state)
      ? "Running now"
      : lastRun.state === "paused"
        ? "Waiting for you"
        : `${lastRun.state === "failed" ? "Failed" : "Ran"} ${new Date(lastRun.created_at).toLocaleDateString()}`
    : "Never run";
  return (
    <article className="wf-definition-card">
      <div className="flex gap-3">
        <span className="wf-tile" data-cat="input">
          <Icon />
        </span>
        <Link className="min-w-0 flex-1" to={`/workflows/${def.id}`}>
          <h3 className="truncate">{def.name}</h3>
          <p className="line-clamp-2 text-xs text-fg-2">
            {def.description || "Open to edit your blocks and settings."}
          </p>
        </Link>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <IconButton label={`Actions for ${def.name}`}>
              <MoreHorizontal />
            </IconButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent>
            <DropdownMenuItem
              onClick={() => {
                setName(def.name);
                setRename(true);
              }}
            >
              Rename
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => void operation("duplicate")}>
              <Copy />
              Duplicate
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSave(true)}>
              Export JSON
            </DropdownMenuItem>
            <DropdownMenuItem
              className="text-danger"
              onClick={() => void operation("delete")}
            >
              <Trash2 />
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      <Link
        className="wf-block-strip"
        to={`/workflows/${def.id}`}
        aria-label={`Edit ${def.name}`}
      >
        {def.graph.nodes.slice(0, 6).map((n, i) => {
          const meta = registry[n.kind];
          return (
            <span key={n.id} className="flex items-center gap-2">
              {i > 0 && <span className="h-px w-2 bg-line" />}
              <span className="wf-tile" data-cat={meta.tone}>
                <meta.Icon />
              </span>
            </span>
          );
        })}
        {def.graph.nodes.length > 6 && (
          <span className="wf-help">+{def.graph.nodes.length - 6}</span>
        )}
      </Link>
      <footer>
        <span className="wf-help">
          <Circle className="mr-1 inline size-2" />
          {status}
        </span>
        <Button variant="ghost" asChild>
          <Link to={`/workflows/${def.id}?run=1`}>
            <Play className="size-3" />
            Run
          </Link>
        </Button>
      </footer>
      {notice && (
        <p role="alert" className="wf-help text-danger">
          {notice}
        </p>
      )}
      <Dialog open={rename} onOpenChange={setRename}>
        <DialogContent>
          <DialogTitle>Rename workflow</DialogTitle>
          <DialogDescription>
            Choose a name for your workflow.
          </DialogDescription>
          <TextField
            label="Workflow name"
            value={name}
            maxLength={80}
            onChange={setName}
          />
          <Button
            disabled={!name.trim()}
            onClick={() => void operation("rename")}
          >
            Rename
          </Button>
        </DialogContent>
      </Dialog>
      {save && (
        <FileSaveDialog
          initial="json"
          title="Save workflow"
          closeLabel="Close workflow save"
          onClose={() => setSave(false)}
          options={[
            {
              format: "json",
              label: "Workflow (.json)",
              url: `/api/workflows/defs/${def.id}`,
              filename: `Atelier-workflow-${def.id.slice(0, 8)}.json`,
            },
          ]}
        />
      )}
    </article>
  );
}
export function RunsList({ runs }: { runs: Run[] }) {
  return runs.length ? (
    <div className="wf-runs-list">
      {runs.map((run) => (
        <Link
          key={run.id}
          to={`/workflows/runs/${run.id}`}
          className="wf-run-row"
          aria-label={`${run.def_name} — ${run.state} · ${run.stage}`}
        >
          <Circle className="size-3 shrink-0" />
          <span className="min-w-0 flex-1">
            <span className="block truncate text-sm font-medium">
              {run.def_name}
            </span>
            <span className="wf-help">
              {run.state === "paused" ? "Waiting for you" : run.state} ·{" "}
              {run.stage}
            </span>
          </span>
          <time className="hidden text-xs text-fg-3 sm:block">
            {new Date(run.created_at).toLocaleString()}
          </time>
          <ChevronRight className="size-4 shrink-0" />
        </Link>
      ))}
    </div>
  ) : (
    <p className="wf-help rounded-xl border border-line p-6">
      No runs yet. Choose a template to get started.
    </p>
  );
}

import "../studio/studio.css";

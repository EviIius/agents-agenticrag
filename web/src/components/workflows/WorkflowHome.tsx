import { Link } from "react-router";
import {
  AudioLines,
  ImagePlus,
  Workflow as WorkflowIcon,
  Play,
  Sparkles,
  Check,
  ChevronRight,
  Circle,
  CircleAlert,
  Pause,
  Square,
  Save,
} from "lucide-react";
import { useWorkspace } from "@/components/app/WorkspaceNavigation";
import { Button } from "@/components/ui/button";
import type { Workflow } from "./WorkflowsPage";

const templates = [
  {
    key: "brief_images",
    title: "Brief to images",
    description:
      "Turn a brief into an image prompt, review it, then create one to three images.",
    Icon: ImagePlus,
    steps: [Play, Sparkles, Pause, ImagePlus, Save],
  },
  {
    key: "meeting_pack",
    title: "Recording to meeting pack",
    description:
      "Save the original transcript and draft a summary, decisions and action items for your review.",
    Icon: AudioLines,
    steps: [Play, AudioLines, Sparkles, Save],
  },
];
const status: Record<
  string,
  { label: string; Icon: typeof Circle; style: string }
> = {
  complete: { label: "Complete", Icon: Check, style: "text-success" },
  paused: { label: "Waiting for you", Icon: Pause, style: "text-warning" },
  failed: { label: "Failed", Icon: CircleAlert, style: "text-danger" },
  interrupted: {
    label: "Interrupted",
    Icon: CircleAlert,
    style: "text-warning",
  },
  cancelled: { label: "Cancelled", Icon: Square, style: "text-fg-3" },
  cancelling: { label: "Cancelling", Icon: Square, style: "text-fg-3" },
  running: { label: "Running", Icon: Circle, style: "text-brand" },
  queued: { label: "Queued", Icon: Circle, style: "text-fg-3" },
};

export function WorkflowRunRows({
  runs,
  loading = false,
}: {
  runs: Workflow[];
  loading?: boolean;
}) {
  if (loading)
    return (
      <div
        role="status"
        aria-label="Loading workflow runs"
        className="space-y-3"
      >
        <div className="skeleton h-14" />
        <div className="skeleton h-14" />
      </div>
    );
  if (!runs.length)
    return (
      <div className="rounded-xl border border-line p-6">
        <p className="text-sm text-fg-2">
          No runs yet. Choose a template to get started.
        </p>
      </div>
    );
  return (
    <div className="overflow-hidden rounded-xl border border-line bg-surface">
      {runs.map((run) => {
        const state = status[run.state] ?? {
          label: run.state,
          Icon: Circle,
          style: "text-fg-3",
        };
        return (
          <Link
            key={run.id}
            to={`/workflows/runs/${run.id}`}
            aria-label={`${run.input.template === "brief_images" ? "Brief to images" : "Recording to meeting pack"} — ${state.label} · ${run.stage}`}
            className="flex min-h-16 items-center gap-3 border-b border-line px-4 py-3 last:border-b-0 hover:bg-surface-2"
          >
            <state.Icon className={`size-4 shrink-0 ${state.style}`} />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">
                {run.input.template === "brief_images"
                  ? "Brief to images"
                  : "Recording to meeting pack"}
              </p>
              <p className="truncate text-xs text-fg-2">
                {state.label} · {run.stage}
              </p>
            </div>
            <time
              dateTime={run.created_at}
              className="hidden shrink-0 text-xs text-fg-3 sm:block"
            >
              {new Date(run.created_at).toLocaleString(undefined, {
                month: "short",
                day: "numeric",
                hour: "numeric",
                minute: "2-digit",
              })}
            </time>
            <ChevronRight className="size-4 shrink-0 text-fg-3" />
          </Link>
        );
      })}
    </div>
  );
}

export function WorkflowHome({
  runs,
  loading = false,
}: {
  runs: Workflow[];
  loading?: boolean;
}) {
  const navigation = useWorkspace();
  return (
    <div className="space-y-8 lg:space-y-10">
      <header className="space-y-3">
        <h1 className="text-2xl font-semibold">Workflows</h1>
        <p className="max-w-3xl text-sm leading-relaxed text-fg-2">
          Turn images and recordings into repeatable steps. Accepted runs keep
          going on your Mac when you close the app.
        </p>
      </header>
      <section aria-label="Workflow templates" className="space-y-4">
        <h2 className="text-xs font-medium tracking-wide text-fg-3">
          START FROM A TEMPLATE
        </h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {templates.map(({ key, title, description, Icon, steps }) => (
            <Link
              key={key}
              to={`/workflows/new?template=${key}`}
              aria-label={`Use ${title} template`}
              state={navigation}
              className="group flex flex-col gap-4 rounded-xl border border-line bg-surface p-5 hover:border-line-strong hover:bg-surface-2"
            >
              <div className="flex items-center gap-3">
                <span className="grid size-9 shrink-0 place-items-center rounded-lg bg-brand-soft text-brand">
                  <Icon className="size-4" />
                </span>
                <h3 className="text-base font-semibold">{title}</h3>
              </div>
              <p className="flex-1 text-sm leading-relaxed text-fg-2">
                {description}
              </p>
              <div
                className="flex items-center gap-2 text-fg-3"
                aria-hidden="true"
              >
                {steps.map((Step, index) => (
                  <span key={index} className="flex items-center gap-2">
                    <Step className="size-4" />
                    {index < steps.length - 1 && (
                      <span className="h-px w-3 bg-line" />
                    )}
                  </span>
                ))}
                <span className="ml-auto flex items-center gap-1 text-sm font-medium text-brand">
                  Use template <ChevronRight className="size-4" />
                </span>
              </div>
            </Link>
          ))}
        </div>
      </section>
      <section aria-label="Recent workflow runs" className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-xs font-medium tracking-wide text-fg-3">
            RECENT RUNS
          </h2>
          <Button variant="ghost" asChild>
            <Link to="/workflows/runs">View all runs</Link>
          </Button>
        </div>
        <WorkflowRunRows runs={runs.slice(0, 10)} loading={loading} />
      </section>
      <p className="text-xs text-fg-3">
        <WorkflowIcon className="mr-2 inline size-4" />
        Text outputs are drafts for your review. Original sources and saved
        results stay available in each run.
      </p>
    </div>
  );
}

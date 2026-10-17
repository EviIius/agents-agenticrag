import { useState } from "react";
import { Link } from "react-router";
import { api } from "@/lib/api";
import type { components } from "@/lib/api-types";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { FileSaveDialog } from "@/components/app/FileSaveDialog";
export type Workflow = components["schemas"]["WorkflowRun"];
type Source = components["schemas"]["WorkflowSource"];
const active = new Set(["queued", "running", "cancelling"]);
export function WorkflowList({
  runs,
  onAction,
  preview = false,
}: {
  runs: Workflow[];
  onAction?: (
    id: string,
    operation: "cancel" | "resume",
    body?: components["schemas"]["WorkflowResume"],
  ) => Promise<void>;
  preview?: boolean;
}) {
  return (
    <section className="space-y-4">
      <h2 className="font-semibold">Saved runs</h2>
      {!runs.length && (
        <p className="text-sm text-fg-2">
          No workflows yet. Choose a template and model to begin.
        </p>
      )}
      {runs.map((run) => (
        <WorkflowCard
          key={run.id}
          run={run}
          onAction={onAction}
          preview={preview}
        />
      ))}
    </section>
  );
}

export function WorkflowCard({
  run,
  onAction,
  preview,
}: {
  run: Workflow;
  onAction?: (
    id: string,
    operation: "cancel" | "resume",
    body?: components["schemas"]["WorkflowResume"],
  ) => Promise<void>;
  preview: boolean;
}) {
  const [save, setSave] = useState(false);
  const [source, setSource] = useState<Source>();
  const [sourceOpen, setSourceOpen] = useState(false);
  const [notice, setNotice] = useState("");
  const [edited, setEdited] = useState<string>();
  const [acting, setActing] = useState(false);
  async function act(
    operation: "cancel" | "resume",
    body?: components["schemas"]["WorkflowResume"],
  ) {
    setActing(true);
    try {
      await onAction?.(run.id, operation, body);
    } finally {
      setActing(false);
    }
  }
  async function viewSource() {
    if (preview) {
      setSource({
        text: "Synthetic source: Mina will send the draft on Friday.",
        raw_text: "Synthetic source",
        segments: [
          {
            start: 0.2,
            end: 2.8,
            text: "Synthetic source: Mina will send the draft on Friday.",
            raw_text: "Synthetic source: Mina will send the draft on Friday.",
          },
        ],
        attachment_id: "synthetic",
        filename: "Synthetic.wav",
      });
      setSourceOpen(true);
      return;
    }
    try {
      setSource(await api<Source>(`/workflows/runs/${run.id}/source`));
      setSourceOpen(true);
    } catch {
      setNotice("The saved source could not be opened.");
    }
  }
  const draft = run.steps[0]?.output?.text;
  const title =
    run.input.template === "brief_images"
      ? "Brief to images"
      : "Recording to meeting pack";
  return (
    <article
      className="rounded-lg border border-line bg-surface-1 p-4 sm:p-5"
      aria-label={`${title} run`}
    >
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-medium">{title}</h3>
        <span className="text-xs text-fg-3">
          {new Date(run.created_at).toLocaleString()}
        </span>
      </div>
      <p role="status" className="mb-3 text-sm text-fg-2">
        {run.stage} · {run.state}
      </p>
      <p className="mb-3 break-words text-xs text-fg-3">
        Text model: {run.input.model.model_id}
        {run.input.cleanup_model
          ? ` · Clean-up: ${run.input.cleanup_model.model_id}`
          : ""}
      </p>
      {run.error && <p className="mb-3 text-sm text-error">{run.error}</p>}
      {notice && (
        <p role="status" className="mb-3 text-sm text-fg-2">
          {notice}
        </p>
      )}
      <ol className="space-y-3">
        {run.steps.map((step) => (
          <li key={step.position} className="rounded-md border border-line p-3">
            <div className="flex flex-wrap justify-between gap-2 text-sm">
              <span>
                {step.position + 1}. {step.label}
              </span>
              <span className="text-fg-3">
                {step.state}
                {step.attempt ? ` · attempt ${step.attempt}` : ""}
              </span>
            </div>
            {typeof step.output?.text === "string" && (
              <pre className="mt-3 max-h-72 overflow-y-auto whitespace-pre-wrap break-words font-sans text-sm">
                {step.output.text as string}
              </pre>
            )}
            {typeof step.output?.image_job_id === "string" && (
              <div className="mt-3">
                {step.state === "complete" &&
                  (preview ? (
                    <div
                      role="img"
                      aria-label="Fake image output preview"
                      className="flex aspect-square max-h-80 items-center justify-center rounded-md bg-surface-2 text-fg-3"
                    >
                      Fake image output
                    </div>
                  ) : (
                    <img
                      className="max-h-80 rounded-md object-contain"
                      alt="Workflow generated image"
                      src={`/api/images/jobs/${step.output.image_job_id as string}/output/png`}
                    />
                  ))}
                <Button asChild variant="outline" className="mt-2">
                  <Link to="/images">View and save in Images</Link>
                </Button>
              </div>
            )}
          </li>
        ))}
      </ol>
      {run.state === "paused" && (
        <div className="mt-4 space-y-3">
          <label className="block text-sm">
            Review image prompt
            <Textarea
              aria-label="Review image prompt"
              className="mt-2 min-h-28"
              value={edited ?? (typeof draft === "string" ? draft : "")}
              onChange={(e) => setEdited(e.target.value)}
              maxLength={4000}
            />
          </label>
          <Button
            disabled={acting || !(edited ?? draft)}
            onClick={() => {
              void act("resume", {
                prompt: edited ?? (draft as string),
                skip_cleanup: false,
              });
            }}
          >
            Approve prompt and generate
          </Button>
        </div>
      )}
      <div className="mt-4 flex flex-wrap gap-2">
        {(active.has(run.state) || run.state === "paused") && (
          <Button
            variant="outline"
            disabled={acting || run.state === "cancelling"}
            onClick={() => {
              void act("cancel");
            }}
          >
            Cancel workflow
          </Button>
        )}
        {["failed", "interrupted", "cancelled"].includes(run.state) && (
          <Button
            disabled={acting}
            onClick={() => {
              void act("resume", { skip_cleanup: false });
            }}
          >
            Retry unfinished steps
          </Button>
        )}
        {run.state === "failed" &&
          run.steps.some(
            (s) => s.kind === "cleanup" && s.state === "failed",
          ) && (
            <Button
              variant="outline"
              disabled={acting}
              onClick={() => {
                void act("resume", { skip_cleanup: true });
              }}
            >
              Continue with original transcript
            </Button>
          )}
        {run.source_available && (
          <Button
            variant="outline"
            onClick={() => {
              void viewSource();
            }}
          >
            View original transcript
          </Button>
        )}
        <Button variant="outline" onClick={() => setSave(true)}>
          Save outputs
        </Button>
      </div>
      {run.input.template === "meeting_pack" && (
        <p className="mt-3 text-xs text-fg-3">
          Draft for review. Cancelling this workflow leaves an already-started
          recording transcription available.
        </p>
      )}
      {save && (
        <FileSaveDialog
          initial="md"
          title="Save workflow outputs"
          closeLabel="Close workflow save"
          preview={preview ? "ready" : undefined}
          onClose={() => setSave(false)}
          options={[
            {
              format: "md",
              label: "Markdown (.md)",
              url: `/api/workflows/runs/${run.id}/export?format=md`,
              filename: `Aether-workflow-${run.id.slice(0, 8)}.md`,
            },
            {
              format: "json",
              label: "Details and source (.json)",
              url: `/api/workflows/runs/${run.id}/export?format=json`,
              filename: `Aether-workflow-${run.id.slice(0, 8)}.json`,
            },
          ]}
        />
      )}
      <Dialog open={sourceOpen} onOpenChange={setSourceOpen}>
        <DialogContent className="max-h-[85dvh] overflow-y-auto">
          <DialogTitle>Original transcript</DialogTitle>
          <DialogDescription>
            The saved source remains available after audio removal.
          </DialogDescription>
          <pre className="whitespace-pre-wrap break-words font-sans text-sm">
            {source?.text}
          </pre>
          {!!source?.segments.length && (
            <details className="rounded-md border border-line p-3">
              <summary className="cursor-pointer text-sm">
                Original source timestamps
              </summary>
              <ol className="mt-3 space-y-3 text-sm">
                {source.segments.map((segment, index) => (
                  <li key={index} className="break-words">
                    <p className="text-xs text-fg-3">
                      {String(segment.start)}s–{String(segment.end)}s
                      {segment.speaker ? ` · ${String(segment.speaker)}` : ""}
                    </p>
                    <p className="whitespace-pre-wrap">
                      {String(segment.text)}
                    </p>
                  </li>
                ))}
              </ol>
            </details>
          )}
        </DialogContent>
      </Dialog>
    </article>
  );
}

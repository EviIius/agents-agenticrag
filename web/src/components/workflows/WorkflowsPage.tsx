import { useEffect, useRef, useState } from "react";
import { Link } from "react-router";
import { ArrowLeft } from "lucide-react";
import { api } from "@/lib/api";
import { uploadWithProgress } from "@/lib/attachments";
import type { components } from "@/lib/api-types";
import { usePreferenceSync } from "@/hooks/usePreferenceSync";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { FileSaveDialog } from "@/components/app/FileSaveDialog";
import { IconButton } from "@/components/app/IconButton";

export type Workflow = components["schemas"]["WorkflowRun"];
type Create = components["schemas"]["WorkflowCreate"];
type Recording = components["schemas"]["WorkflowRecording"];
type Source = components["schemas"]["WorkflowSource"];
type Model = components["schemas"]["ModelInfo"];
type Snapshot = components["schemas"]["WorkflowSnapshot"];
type Change = components["schemas"]["WorkflowChange"];
export type Choice = Pick<
  Model,
  "connection_id" | "model_id" | "display_name" | "context_length"
> & { imageCompatible?: boolean };
const active = new Set(["queued", "running", "cancelling"]);
const key = (model: Choice) => `${model.connection_id}/${model.model_id}`;

export function WorkflowsPage() {
  const [runs, setRuns] = useState<Workflow[]>([]);
  const [models, setModels] = useState<Choice[]>([]);
  const [recordings, setRecordings] = useState<Recording[]>([]);
  const [preferences, setPreferences] = useState<Record<string, unknown>>();
  const [notice, setNotice] = useState("");
  const [connection, setConnection] = useState("Connecting…");
  usePreferenceSync(preferences);
  useEffect(() => {
    let mounted = true;
    void Promise.all([
      api<Model[]>("/models"),
      api<Recording[]>("/workflows/recordings"),
      api<Record<string, unknown>>("/settings"),
      api<Record<string, string>[]>("/workflows/image-models").catch(() => []),
    ])
      .then(([m, r, p, compatible]) => {
        if (mounted) {
          setModels(
            m
              .filter((value) => value.chat_capable)
              .map((value) => ({
                ...value,
                imageCompatible: compatible.some(
                  (item) =>
                    item.connection_id === value.connection_id &&
                    item.model_id === value.model_id,
                ),
              })),
          );
          setRecordings(r);
          setPreferences(p);
        }
      })
      .catch(() => {
        if (mounted)
          setNotice(
            "Models or recordings could not be loaded. Reload to try again.",
          );
      });
    const source = new EventSource("/api/workflows/events");
    let frame = 0;
    const pending: (
      { kind: "snapshot"; data: Snapshot } | { kind: "change"; data: Change }
    )[] = [];
    const enqueue = (kind: "snapshot" | "change", event: MessageEvent) => {
      try {
        pending.push(
          kind === "snapshot"
            ? { kind, data: JSON.parse(event.data) as Snapshot }
            : { kind, data: JSON.parse(event.data) as Change },
        );
        if (!frame)
          frame = requestAnimationFrame(() => {
            frame = 0;
            const batch = pending.splice(0);
            if (!mounted) return;
            setRuns((current) => {
              let next = current;
              for (const item of batch)
                next =
                  item.kind === "snapshot"
                    ? item.data.runs
                    : [
                        item.data.run,
                        ...next.filter((run) => run.id !== item.data.run.id),
                      ].sort((a, b) =>
                        b.created_at.localeCompare(a.created_at),
                      );
              return next;
            });
          });
      } catch {
        setNotice("An update could not be read. Reload to reconnect.");
      }
    };
    source.addEventListener("workflow.snapshot", (event) =>
      enqueue("snapshot", event as MessageEvent),
    );
    source.addEventListener("workflow.updated", (event) =>
      enqueue("change", event as MessageEvent),
    );
    source.onopen = () => setConnection("Connected");
    source.onerror = () =>
      setConnection("Reconnecting — accepted work continues on your Mac");
    return () => {
      mounted = false;
      source.close();
      cancelAnimationFrame(frame);
    };
  }, []);
  async function action(
    id: string,
    operation: "cancel" | "resume",
    body?: components["schemas"]["WorkflowResume"],
  ) {
    try {
      await api(
        `/workflows/runs/${id}/${operation}`,
        operation === "resume" ? (body ?? {}) : undefined,
        "POST",
      );
    } catch (error) {
      setNotice(
        error instanceof Error ? error.message : "The action did not finish.",
      );
    }
  }
  return (
    <main className="h-dvh overflow-y-auto bg-bg px-4 pb-[max(24px,env(safe-area-inset-bottom))] pt-[max(16px,env(safe-area-inset-top))]">
      <div className="mx-auto max-w-4xl">
        <header className="mb-6 flex min-h-11 items-center gap-3">
          <IconButton label="Back to chat" asChild>
            <Link to="/">
              <ArrowLeft />
            </Link>
          </IconButton>
          <h1 className="flex-1 text-xl font-semibold">Workflows</h1>
          <span role="status" className="text-xs text-fg-3">
            {connection}
          </span>
        </header>
        {notice && (
          <p role="status" className="mb-4 text-fg-2">
            {notice}
          </p>
        )}
        <WorkflowForm
          models={models}
          recordings={recordings}
          onAccepted={(run) =>
            setRuns((current) => [
              run,
              ...current.filter((r) => r.id !== run.id),
            ])
          }
          onNotice={setNotice}
        />
        <WorkflowList runs={runs} onAction={action} />
      </div>
    </main>
  );
}

function ModelSelect({
  value,
  onChange,
  models,
  label,
}: {
  value: string;
  onChange: (value: string) => void;
  models: Choice[];
  label: string;
}) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium">{label}</label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger aria-label={label} className="w-full">
          <SelectValue placeholder="Choose a text model" />
        </SelectTrigger>
        <SelectContent>
          {models.map((model) => (
            <SelectItem key={key(model)} value={key(model)}>
              {model.display_name}
              {model.imageCompatible ? " · tested with images" : ""}
              {model.context_length
                ? ` · ${Math.round(model.context_length / 1024)}K context`
                : ""}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

export function WorkflowForm({
  models,
  recordings,
  onAccepted,
  onNotice,
  preview = false,
  previewProgress,
  previewRecording = false,
}: {
  models: Choice[];
  recordings: Recording[];
  onAccepted?: (run: Workflow) => void;
  onNotice?: (text: string) => void;
  preview?: boolean;
  previewProgress?: number;
  previewRecording?: boolean;
}) {
  const [template, setTemplate] = useState<"brief_images" | "meeting_pack">(
    preview && previewRecording ? "meeting_pack" : "brief_images",
  );
  const [brief, setBrief] = useState("");
  const [model, setModel] = useState("");
  const [attachment, setAttachment] = useState("");
  const [cleanup, setCleanup] = useState(false);
  const [cleanupModel, setCleanupModel] = useState("");
  const [review, setReview] = useState(true);
  const [seeds, setSeeds] = useState("42");
  const [maximum, setMaximum] = useState("");
  const [temperature, setTemperature] = useState("");
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState<number | undefined>(
    preview ? previewProgress : undefined,
  );
  const [uploaded, setUploaded] = useState<Recording>();
  const requestKey = useRef<string>(crypto.randomUUID());
  const upload = useRef<AbortController | null>(null);
  useEffect(() => () => upload.current?.abort(), []);
  const selected = models.find((item) => key(item) === model);
  const cleaner = models.find((item) => key(item) === cleanupModel);
  async function addFile(file?: File) {
    if (!file || preview) return;
    const controller = new AbortController();
    upload.current = controller;
    setProgress(0);
    try {
      const value = await uploadWithProgress(
        file,
        setProgress,
        controller.signal,
      );
      setUploaded({
        id: value.id,
        filename: value.filename,
        status: value.transcript?.status ?? "queued",
      });
      setAttachment(value.id);
    } catch (error) {
      onNotice?.(
        error instanceof Error ? error.message : "Upload did not finish.",
      );
    } finally {
      setProgress(undefined);
      upload.current = null;
    }
  }
  async function submit() {
    if (!selected || preview) return;
    const values = seeds.split(",").map((v) => Number(v.trim()));
    if (
      template === "brief_images" &&
      (seeds.split(",").some((v) => !v.trim()) ||
        !values.length ||
        values.length > 3 ||
        values.some((v) => !Number.isInteger(v) || v < 0 || v > 4294967295))
    ) {
      onNotice?.("Enter one to three whole-number seeds separated by commas.");
      return;
    }
    const params: components["schemas"]["Parameters"] = {};
    if (maximum) params.max_tokens = Number(maximum);
    if (temperature) params.temperature = Number(temperature);
    const body: Create = {
      request_key: requestKey.current,
      template,
      model: {
        connection_id: selected.connection_id,
        model_id: selected.model_id,
        params,
      },
      brief: template === "brief_images" ? brief : "",
      attachment_id: template === "meeting_pack" ? attachment : null,
      cleanup_model:
        template === "meeting_pack" && cleanup && cleaner
          ? {
              connection_id: cleaner.connection_id,
              model_id: cleaner.model_id,
              params: {},
            }
          : null,
      seeds: template === "brief_images" ? values : [42],
      review_prompt: review,
    };
    setBusy(true);
    try {
      const run = await api<Workflow>("/workflows/runs", body);
      onAccepted?.(run);
      requestKey.current = crypto.randomUUID();
    } catch (error) {
      onNotice?.(
        error instanceof Error ? error.message : "Workflow was not accepted.",
      );
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="mb-8 rounded-lg border border-line bg-surface-1 p-4 sm:p-5">
      <h2 className="mb-3 font-semibold">New workflow</h2>
      <div className="mb-4 flex flex-wrap gap-2">
        <Button
          variant={template === "brief_images" ? "default" : "outline"}
          aria-pressed={template === "brief_images"}
          onClick={() => setTemplate("brief_images")}
        >
          Brief to images
        </Button>
        <Button
          variant={template === "meeting_pack" ? "default" : "outline"}
          aria-pressed={template === "meeting_pack"}
          onClick={() => setTemplate("meeting_pack")}
        >
          Recording to meeting pack
        </Button>
      </div>
      <div className="space-y-4">
        {template === "brief_images" ? (
          <>
            <label className="block text-sm">
              Image brief
              <Textarea
                aria-label="Image brief"
                className="mt-2 min-h-28"
                value={brief}
                onChange={(e) => setBrief(e.target.value)}
                placeholder="Describe the image you want…"
                maxLength={20000}
              />
            </label>
            <p className="text-sm text-fg-2">
              Your text model drafts one prompt. FLUX.2 klein 4B generates the
              images.
            </p>
            <p className="text-xs text-fg-3">
              Choose a model marked “tested with images” for an uninterrupted
              run. Other loaded combinations can stop the image step; your draft
              stays saved.
            </p>
          </>
        ) : (
          <>
            <label className="block text-sm">
              Upload a recording
              <Input
                aria-label="Upload workflow recording"
                type="file"
                accept=".wav,.m4a,.mp3,.aac,.flac,.ogg,.aiff,.aif"
                className="mt-2"
                disabled={progress !== undefined || preview}
                onChange={(e) => {
                  void addFile(e.target.files?.[0]);
                  e.target.value = "";
                }}
              />
            </label>
            {progress !== undefined && (
              <div className="flex items-center gap-3">
                <p role="status">Uploading {progress}%</p>
                <Button
                  variant="outline"
                  onClick={() => upload.current?.abort()}
                >
                  Cancel upload
                </Button>
              </div>
            )}
            <label className="block text-sm">
              Or use a saved recording
              <Select value={attachment} onValueChange={setAttachment}>
                <SelectTrigger
                  className="mt-2 w-full"
                  aria-label="Saved recording"
                >
                  <SelectValue placeholder="Choose a recording" />
                </SelectTrigger>
                <SelectContent>
                  {[
                    ...(uploaded ? [uploaded] : []),
                    ...recordings.filter((r) => r.id !== uploaded?.id),
                  ].map((r) => (
                    <SelectItem key={r.id} value={r.id}>
                      {r.filename} · {r.status}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </label>
            <p className="text-sm text-fg-2">
              The original transcript is saved. Successful audio follows your
              existing retention setting.
            </p>
          </>
        )}
        <ModelSelect
          value={model}
          onChange={setModel}
          models={models}
          label={
            template === "brief_images"
              ? "Prompt draft model"
              : "Meeting-pack model"
          }
        />
        <details className="rounded-md border border-line p-3">
          <summary className="cursor-pointer text-sm">
            Optional model overrides
          </summary>
          <p className="my-2 text-xs text-fg-3">
            Empty fields use your saved model defaults, then runtime defaults.
          </p>
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="text-sm">
              Output token limit
              <Input
                aria-label="Workflow output token limit"
                type="number"
                min={1}
                max={32768}
                value={maximum}
                onChange={(e) => setMaximum(e.target.value)}
                placeholder="Saved or runtime default"
              />
            </label>
            <label className="text-sm">
              Temperature
              <Input
                aria-label="Workflow temperature"
                type="number"
                min={0}
                max={2}
                step="0.1"
                value={temperature}
                onChange={(e) => setTemperature(e.target.value)}
                placeholder="Saved or runtime default"
              />
            </label>
          </div>
        </details>
        {template === "brief_images" ? (
          <>
            <label className="block text-sm">
              Image seeds · one to three variants
              <Input
                aria-label="Image variant seeds"
                className="mt-2"
                value={seeds}
                onChange={(e) => setSeeds(e.target.value)}
              />
            </label>
            <label className="flex min-h-11 items-center gap-3 text-sm">
              <input
                type="checkbox"
                checked={review}
                onChange={(e) => setReview(e.target.checked)}
              />
              Pause to review the prompt before generating
            </label>
          </>
        ) : (
          <>
            <label className="flex min-h-11 items-center gap-3 text-sm">
              <input
                type="checkbox"
                checked={cleanup}
                onChange={(e) => setCleanup(e.target.checked)}
              />
              Run guarded transcript clean-up first
            </label>
            {cleanup && (
              <ModelSelect
                value={cleanupModel}
                onChange={setCleanupModel}
                models={models}
                label="Clean-up model"
              />
            )}
            <p className="text-sm text-fg-2">
              The meeting pack is a draft. Check quotations, decisions, owners
              and dates against the saved source.
            </p>
          </>
        )}
        <Button
          onClick={() => {
            void submit();
          }}
          disabled={
            busy ||
            progress !== undefined ||
            !selected ||
            (template === "brief_images"
              ? !brief.trim()
              : !attachment || (cleanup && !cleaner))
          }
        >
          {busy ? "Accepting…" : "Start workflow"}
        </Button>
        <p className="text-xs text-fg-3">
          Accepted steps continue on your Mac when you close the app. The latest
          50 runs are shown below.
        </p>
      </div>
    </section>
  );
}

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

function WorkflowCard({
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
              filename: `Atelier-workflow-${run.id.slice(0, 8)}.md`,
            },
            {
              format: "json",
              label: "Details and source (.json)",
              url: `/api/workflows/runs/${run.id}/export?format=json`,
              filename: `Atelier-workflow-${run.id.slice(0, 8)}.json`,
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

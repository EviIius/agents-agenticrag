import { useEffect, useRef, useState } from "react";
import { Link, useLocation, useParams } from "react-router";
import { useWorkspace } from "@/components/app/WorkspaceNavigation";
import { useWorkflowRuns } from "./useWorkflowRuns";
import { WorkflowStatus, WorkflowRunUnavailable } from "./WorkflowStatus";
import { WorkflowHome, WorkflowRunRows } from "./WorkflowHome";
import { WorkflowCanvas, type StepPanel } from "./WorkflowCanvas";
import { imageSeeds, validImageSeed } from "@/lib/image-seeds";
import { api } from "@/lib/api";
import { uploadWithProgress } from "@/lib/attachments";
import type { components } from "@/lib/api-types";
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

export type Workflow = components["schemas"]["WorkflowRun"];
type Create = components["schemas"]["WorkflowCreate"];
type Recording = components["schemas"]["WorkflowRecording"];
type Source = components["schemas"]["WorkflowSource"];
type Model = components["schemas"]["ModelInfo"];
export type Choice = Pick<
  Model,
  "connection_id" | "model_id" | "display_name" | "context_length"
> & { imageCompatible?: boolean };
const active = new Set(["queued", "running", "cancelling"]);
const key = (model: Choice) => `${model.connection_id}/${model.model_id}`;

export function WorkflowsPage() {
  const location = useLocation();
  const navigation = useWorkspace();
  const builder = location.pathname === "/workflows/new";
  const allRuns = location.pathname === "/workflows/runs";
  const { runId } = useParams();
  const {
    runs,
    setRuns,
    loading,
    notice,
    setNotice,
    connection,
    retry,
    attempt,
  } = useWorkflowRuns();
  const [models, setModels] = useState<Choice[]>([]);
  const [recordings, setRecordings] = useState<Recording[]>([]);
  const [requested, setRequested] = useState<Workflow>();
  useEffect(() => {
    if (!builder) return;
    let mounted = true;
    void Promise.all([
      api<Model[]>("/models"),
      api<Recording[]>("/workflows/recordings"),
      api<Record<string, string>[]>("/workflows/image-models").catch(() => []),
    ])
      .then(([m, r, compatible]) => {
        if (!mounted) return;
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
      })
      .catch(() => {
        if (mounted)
          setNotice(
            "Models or recordings could not be loaded. Reload to try again.",
          );
      });
    return () => {
      mounted = false;
    };
  }, [builder, setNotice, attempt]);
  useEffect(() => {
    if (!runId) return;
    let mounted = true;
    setRequested(undefined);
    void api<Workflow>(`/workflows/runs/${runId}`).then(
      (run) => {
        if (mounted) setRequested(run);
      },
      () => {
        if (mounted) setNotice("This run could not be opened.");
      },
    );
    return () => {
      mounted = false;
    };
  }, [runId, setNotice, attempt]);
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
  const template =
    new URLSearchParams(location.search).get("template") === "meeting_pack"
      ? "meeting_pack"
      : "brief_images";
  const run = runs.find((item) => item.id === runId) ?? requested;
  return (
    <section
      className="min-h-0 flex-1 overflow-y-auto bg-bg px-4 py-6 pb-[max(24px,env(safe-area-inset-bottom))] lg:px-8"
      aria-label="Workflows"
    >
      <div className="mx-auto max-w-[1120px]">
        <WorkflowStatus connection={connection} notice={notice} retry={retry} />
        {builder ? (
          <>
            <h1 className="mb-6 text-xl font-semibold">Use a template</h1>
            <WorkflowForm
              key={template}
              initialTemplate={template}
              initialModel={navigation.modelKey}
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
          </>
        ) : runId ? (
          <>
            <h1 className="mb-6 text-xl font-semibold">Workflow run</h1>
            {run ? (
              <WorkflowCard
                key={run.id}
                run={run}
                onAction={action}
                preview={false}
              />
            ) : (
              <WorkflowRunUnavailable failed={!!notice} />
            )}
          </>
        ) : allRuns ? (
          <>
            <h1 className="mb-2 text-2xl font-semibold">Workflow runs</h1>
            <p className="mb-6 text-sm text-fg-2">
              The latest 50 runs. Open a run to review its saved results.
            </p>
            <WorkflowRunRows runs={runs} loading={loading} />
          </>
        ) : (
          <WorkflowHome runs={runs} loading={loading} />
        )}
      </div>
    </section>
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
  initialModel,
  initialTemplate,
  onAccepted,
  onNotice,
  preview = false,
  previewProgress,
  previewRecording = false,
}: {
  models: Choice[];
  initialModel?: string;
  initialTemplate?: "brief_images" | "meeting_pack";
  recordings: Recording[];
  onAccepted?: (run: Workflow) => void;
  onNotice?: (text: string) => void;
  preview?: boolean;
  previewProgress?: number;
  previewRecording?: boolean;
}) {
  const [template, setTemplate] = useState<"brief_images" | "meeting_pack">(
    initialTemplate ??
      (preview && previewRecording ? "meeting_pack" : "brief_images"),
  );
  const [brief, setBrief] = useState("");
  const [model, setModel] = useState(initialModel ?? "");
  const [panel, setPanel] = useState<StepPanel>("input");
  const [attachment, setAttachment] = useState("");
  const [cleanup, setCleanup] = useState(false);
  const [cleanupModel, setCleanupModel] = useState("");
  const [review, setReview] = useState(true);
  const [seeds, setSeeds] = useState("");
  const [count, setCount] = useState(1);
  const acceptedRequest = useRef<
    { signature: string; body: Create } | undefined
  >(undefined);
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
    const values = seeds ? seeds.split(",").map((v) => Number(v.trim())) : [];
    if (
      template === "brief_images" &&
      seeds &&
      (seeds.split(",").some((v) => !validImageSeed(v.trim())) ||
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
    const signature = JSON.stringify([
      { ...body, request_key: undefined },
      count,
    ]);
    if (
      !acceptedRequest.current ||
      acceptedRequest.current.signature !== signature
    ) {
      if (acceptedRequest.current) {
        requestKey.current = crypto.randomUUID();
        body.request_key = requestKey.current;
      }
      if (template === "brief_images" && !seeds) body.seeds = imageSeeds(count);
      acceptedRequest.current = { signature, body };
    }
    setBusy(true);
    try {
      const run = await api<Workflow>(
        "/workflows/runs",
        acceptedRequest.current.body,
      );
      onAccepted?.(run);
      requestKey.current = crypto.randomUUID();
      acceptedRequest.current = undefined;
    } catch (error) {
      onNotice?.(
        error instanceof Error ? error.message : "Workflow was not accepted.",
      );
    } finally {
      setBusy(false);
    }
  }
  return (
    <WorkflowCanvas
      template={template}
      onTemplate={(value) => {
        setTemplate(value);
        setPanel("input");
      }}
      panel={panel}
      onPanel={setPanel}
      model={selected?.display_name}
      cleanup={cleanup}
      review={review}
      count={seeds ? seeds.split(",").length : count}
      busy={busy}
      disabled={
        busy ||
        progress !== undefined ||
        !selected ||
        (template === "brief_images"
          ? !brief.trim()
          : !attachment || (cleanup && !cleaner))
      }
      onStart={() => void submit()}
    >
      <div className="space-y-4">
        <div hidden={panel !== "input"}>
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
                run. Other loaded combinations can stop the image step; your
                draft stays saved.
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
        </div>
        <div hidden={panel !== "model"}>
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
        </div>
        {template === "brief_images" ? (
          <>
            <div hidden={panel !== "images"}>
              <p className="mb-3 text-sm text-fg-2">
                Choose how many images to compare.
              </p>
              <div className="mb-3 flex gap-2" aria-label="Number of images">
                {[1, 2, 3].map((value) => (
                  <Button
                    key={value}
                    aria-pressed={count === value}
                    variant={count === value ? "default" : "outline"}
                    onClick={() => {
                      setCount(value);
                      setSeeds("");
                    }}
                  >
                    {value}
                  </Button>
                ))}
              </div>
              <details>
                <summary className="flex min-h-11 cursor-pointer items-center text-sm">
                  Advanced seeds
                </summary>
                <p className="my-2 text-xs text-fg-3">
                  Seeds are automatic. Enter one to three saved seeds only to
                  repeat exact results.
                </p>
                <label className="block text-sm">
                  Image seeds (optional)
                  <Input
                    aria-label="Image variant seeds"
                    className="mt-2"
                    placeholder="Automatic"
                    value={seeds}
                    onChange={(e) => setSeeds(e.target.value)}
                  />
                </label>
              </details>
            </div>
            <div hidden={panel !== "review"}>
              <label className="flex min-h-11 items-center gap-3 text-sm">
                <input
                  type="checkbox"
                  checked={review}
                  onChange={(e) => setReview(e.target.checked)}
                />
                Pause to review the prompt before generating
              </label>
              <p className="mt-3 text-sm text-fg-2">
                You can edit the model’s prompt before the images start.
              </p>
            </div>
          </>
        ) : (
          <div hidden={panel !== "cleanup"}>
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
          </div>
        )}
        <div hidden={panel !== "output"}>
          <p className="mb-3 text-sm text-fg-2">
            {template === "brief_images"
              ? "Your images appear in Saved runs. Compare them and save your favorite."
              : "Your meeting pack is a draft. Review decisions, owners, dates and quoted speech against the original transcript before saving."}
          </p>
          <p className="text-xs text-fg-3">
            Accepted steps continue on your Mac when you close the app. The
            latest 50 runs are shown below.
          </p>
        </div>
      </div>
    </WorkflowCanvas>
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

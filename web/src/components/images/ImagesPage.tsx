import { useEffect, useRef, useState } from "react";
import { Link } from "react-router";
import { ArrowLeft, ImageIcon } from "lucide-react";
import { api } from "@/lib/api";
import { usePreferenceSync } from "@/hooks/usePreferenceSync";
import type { components } from "@/lib/api-types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { FileSaveDialog } from "@/components/app/FileSaveDialog";
import { IconButton } from "@/components/app/IconButton";
import { imageSeeds, validImageSeed } from "@/lib/image-seeds";

type Job = components["schemas"]["ImageJob"];
type Snapshot = components["schemas"]["ImageSnapshot"];
type Status = components["schemas"]["ImageStatus"];
type Change = components["schemas"]["ImageChange"];
const active = new Set(["queued", "preparing", "running", "cancelling"]);
export function bytes(value: number) {
  return value >= 1e9
    ? `${(value / 1e9).toFixed(2)} GB`
    : value >= 1e6
      ? `${(value / 1e6).toFixed(2)} MB`
      : `${(value / 1e3).toFixed(1)} KB`;
}

export function ImagesPage() {
  return <ImagesWorkspace inShell />;
}

export function ImagesWorkspace({
  embedded = false,
  prompt,
  onPromptChange,
  onClose,
  preview = false,
  inShell = false,
}: {
  embedded?: boolean;
  prompt?: string;
  onPromptChange?: (prompt: string) => void;
  onClose?: () => void;
  preview?: boolean;
  inShell?: boolean;
}) {
  const [preferences, setPreferences] = useState<Record<string, unknown>>();
  usePreferenceSync(preferences);
  const [snapshot, setSnapshot] = useState<Snapshot>();
  const [status, setStatus] = useState<Status>();
  const [connection, setConnection] = useState("Connecting…");
  const [error, setError] = useState("");
  useEffect(() => {
    if (preview) return;
    let mounted = true;
    void api<Record<string, unknown>>("/settings")
      .then((value) => {
        if (mounted) setPreferences(value);
      })
      .catch(() => {
        if (mounted) setError("Saved appearance could not be loaded.");
      });
    void api<Status>("/images/status")
      .then((value) => {
        if (mounted) setStatus(value);
      })
      .catch(() => {
        if (mounted) setError("Cannot reach the image service.");
      });
    const source = new EventSource("/api/images/events");
    let frame = 0;
    const pending: (
      { kind: "snapshot"; data: Snapshot } | { kind: "change"; data: Change }
    )[] = [];
    function flush() {
      frame = 0;
      if (!mounted) return;
      const batch = pending.splice(0);
      setSnapshot((current) => {
        let next = current;
        for (const item of batch) {
          if (item.kind === "snapshot") next = item.data;
          else if (next)
            next = {
              storage: item.data.storage,
              jobs: [
                item.data.job,
                ...next.jobs.filter((job) => job.id !== item.data.job.id),
              ].sort((a, b) => b.created_at.localeCompare(a.created_at)),
            };
        }
        return next;
      });
    }
    function enqueue(kind: "snapshot" | "change", event: MessageEvent) {
      try {
        pending.push(
          kind === "snapshot"
            ? { kind, data: JSON.parse(event.data) as Snapshot }
            : { kind, data: JSON.parse(event.data) as Change },
        );
        if (!frame) frame = requestAnimationFrame(flush);
      } catch {
        setError("The image update could not be read. Reload this view.");
      }
    }
    source.addEventListener("image.snapshot", (event) =>
      enqueue("snapshot", event as MessageEvent),
    );
    source.addEventListener("image.updated", (event) =>
      enqueue("change", event as MessageEvent),
    );
    source.onopen = () => setConnection("Connected");
    source.onerror = () =>
      setConnection("Reconnecting — accepted jobs continue on your Mac");
    return () => {
      mounted = false;
      source.close();
      cancelAnimationFrame(frame);
    };
  }, [preview]);
  async function older() {
    try {
      const before = snapshot?.jobs.at(-1)?.created_at;
      const jobs = await api<Job[]>(
        `/images/jobs?before=${encodeURIComponent(before ?? "")}`,
      );
      setSnapshot((current) =>
        current
          ? {
              ...current,
              jobs: [
                ...current.jobs,
                ...jobs.filter(
                  (job) => !current.jobs.some((old) => old.id === job.id),
                ),
              ],
            }
          : current,
      );
      if (!jobs.length) setError("No earlier jobs.");
    } catch {
      setError("Couldn't load earlier jobs.");
    }
  }
  return (
    <section
      className={
        embedded
          ? "bg-bg"
          : inShell
            ? "min-h-0 flex-1 overflow-y-auto bg-bg px-4 py-6 pb-[max(24px,env(safe-area-inset-bottom))] lg:px-8"
            : "h-dvh overflow-y-auto bg-bg px-4 pb-[max(24px,env(safe-area-inset-bottom))] pt-[max(16px,env(safe-area-inset-top))]"
      }
      aria-label={embedded ? "Create images here" : "Images"}
    >
      <div className="mx-auto max-w-5xl">
        <header
          className={`mb-3 flex min-h-11 items-center gap-3 ${embedded ? "sticky top-0 z-10 bg-bg" : ""}`}
        >
          {embedded ? (
            <Button variant="ghost" className="h-11" onClick={onClose}>
              <ArrowLeft className="size-4" /> Message
            </Button>
          ) : !inShell ? (
            <IconButton label="Back to chat" asChild>
              <Link to="/">
                <ArrowLeft />
              </Link>
            </IconButton>
          ) : null}
          <h1 className="flex-1 text-xl font-semibold">Images</h1>
          {embedded && (
            <Link
              to="/images"
              className="flex min-h-11 items-center px-2 text-sm text-brand"
            >
              Gallery
            </Link>
          )}
          <span className="text-xs text-fg-3" role="status">
            {preview ? "Design preview" : connection}
          </span>
        </header>
        {error && (
          <p role="status" className="mb-4 text-fg-2">
            {error}
          </p>
        )}
        <ImagesView
          jobs={snapshot?.jobs ?? []}
          storage={snapshot?.storage}
          status={status}
          preview={preview}
          prompt={prompt}
          onPromptChange={onPromptChange}
          embedded={embedded}
        />
        {snapshot && snapshot.jobs.length >= 100 && (
          <Button
            className="mt-6 h-11"
            variant="outline"
            onClick={() => void older()}
          >
            Earlier jobs
          </Button>
        )}
      </div>
    </section>
  );
}

export function ImagesView({
  jobs,
  storage,
  status,
  preview = false,
  prompt: controlledPrompt,
  onPromptChange,
  embedded = false,
}: {
  jobs: Job[];
  storage?: Snapshot["storage"];
  status?: Status;
  preview?: boolean;
  prompt?: string;
  onPromptChange?: (prompt: string) => void;
  embedded?: boolean;
}) {
  const [ownPrompt, setOwnPrompt] = useState("");
  const prompt = controlledPrompt ?? ownPrompt;
  const setPrompt = onPromptChange ?? setOwnPrompt;
  const [seed, setSeed] = useState("");
  const [parent, setParent] = useState<string>();
  const [filter, setFilter] = useState("all");
  const [saving, setSaving] = useState<Job>();
  const [detail, setDetail] = useState<Job>();
  const [removing, setRemoving] = useState<Job | "all">();
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const request = useRef<
    { signature: string; key: string; seed: number } | undefined
  >(undefined);
  async function submit(value: string, number?: number, parentId?: string) {
    const signature = JSON.stringify([value, number, parentId]);
    if (!request.current || request.current.signature !== signature)
      request.current = {
        signature,
        key: crypto.randomUUID(),
        seed: number ?? imageSeeds(1)[0],
      };
    setBusy(true);
    setNotice("");
    try {
      const job = await api<Job>("/images/jobs", {
        prompt: value,
        seed: request.current.seed,
        parent_id: parentId ?? null,
        request_key: request.current.key,
      });
      request.current = undefined;
      setNotice(
        `Image accepted. ${job.stage}. You can close this view while it works.`,
      );
    } catch (error) {
      setNotice(
        error instanceof Error
          ? error.message
          : "Couldn't submit the image. Retry uses the same request key.",
      );
    } finally {
      setBusy(false);
    }
  }
  async function action(job: Job, kind: "cancel" | "retry") {
    if (preview) return;
    if (kind === "retry") {
      await submit(job.prompt, job.seed, job.id);
      return;
    }
    try {
      await api(`/images/jobs/${job.id}/cancel`, {});
    } catch (error) {
      setNotice(
        error instanceof Error ? error.message : "Couldn't cancel this image.",
      );
    }
  }
  async function remove() {
    if (!removing || preview) return;
    setBusy(true);
    try {
      if (removing === "all") await api("/images/clear", { confirm: true });
      else await api(`/images/jobs/${removing.id}/output`, undefined, "DELETE");
      setRemoving(undefined);
      setNotice(
        "Saved image files removed. Job history and backups are retained.",
      );
    } catch (error) {
      setNotice(
        error instanceof Error ? error.message : "Couldn't remove image files.",
      );
    } finally {
      setBusy(false);
    }
  }
  const visible = jobs.filter(
    (job) =>
      filter === "all" ||
      (filter === "active" ? active.has(job.state) : job.image_bytes > 0),
  );
  const validSeed = !seed || validImageSeed(seed);
  return (
    <>
      <section
        className={
          embedded
            ? "composer"
            : "rounded-xl border border-line bg-surface p-4 sm:p-5"
        }
        aria-labelledby="image-create"
      >
        <h2 id="image-create" className="mb-1 font-medium">
          Create an image
        </h2>
        <p className="mb-4 text-sm text-fg-2">
          Describe what you want. Your Mac creates it with FLUX.2 klein 4B.
        </p>
        {status && !status.available && (
          <p className="mb-3 text-sm text-fg-2" role="status">
            {status.reason}
          </p>
        )}
        <label className="mb-2 block text-sm" htmlFor="image-prompt">
          Prompt
        </label>
        <Textarea
          id="image-prompt"
          value={prompt}
          maxLength={4000}
          className="min-h-28 bg-surface-2 text-base"
          placeholder="Describe the image you want…"
          onChange={(event) => setPrompt(event.target.value)}
        />
        <div className="mt-4 flex flex-wrap items-end gap-3">
          <details className="text-sm">
            <summary className="flex min-h-11 cursor-pointer items-center">
              Advanced
            </summary>
            <label className="block text-sm">
              Seed (optional)
              <Input
                aria-label="Seed"
                inputMode="numeric"
                value={seed}
                onChange={(event) => setSeed(event.target.value)}
                className="mt-1 h-11 w-36 bg-surface-2"
                placeholder="Automatic"
              />
            </label>
            <p className="mt-2 max-w-60 text-xs text-fg-3">
              Leave empty for a new result. Use a saved seed to repeat an image
              with the same prompt.
            </p>
          </details>
          <Button
            className="h-11"
            disabled={
              busy ||
              !prompt.trim() ||
              !validSeed ||
              (!preview && !status?.available)
            }
            onClick={() =>
              !preview &&
              void submit(prompt, seed ? Number(seed) : undefined, parent)
            }
          >
            Generate one image
          </Button>
          {parent && (
            <Button
              className="h-11"
              variant="ghost"
              onClick={() => setParent(undefined)}
            >
              Clear version link
            </Button>
          )}
        </div>
        {parent && (
          <p className="mt-2 text-sm text-fg-2">
            New version from the selected prompt. This generates a complete
            image and keeps the original.
          </p>
        )}
        <p className="mt-3 text-xs text-fg-3">
          One native task at a time. Chat may wait for an image to finish;
          models are never unloaded automatically.
        </p>
      </section>
      {notice && (
        <p className="my-4 text-sm text-fg-2" role="status">
          {notice}
        </p>
      )}
      {storage && !embedded && (
        <section
          className="my-5 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-line p-4"
          aria-label="Image storage"
        >
          <div>
            <p className="font-medium">
              {storage.outputs} saved images ·{" "}
              {bytes(storage.image_bytes + storage.metadata_bytes)}
            </p>
            <p className="mt-1 text-sm text-fg-2">
              {storage.versions} additional versions · Images{" "}
              {bytes(storage.image_bytes)} · Details{" "}
              {bytes(storage.metadata_bytes)}
            </p>
            <p className="mt-1 text-xs text-fg-3">
              Image backups {bytes(storage.backup_bytes)} · Request history{" "}
              {bytes(storage.manifest_bytes)} · Shared app database{" "}
              {bytes(storage.database_bytes)} · Free {bytes(storage.free_bytes)}
            </p>
            <p className="mt-1 text-xs text-fg-3">
              Each version is a full PNG. Shared model weights are separate.
              Removing outputs keeps history and the last seven backups.
            </p>
          </div>
          <Button
            variant="outline"
            className="h-11"
            disabled={!storage.outputs}
            onClick={() => setRemoving("all")}
          >
            Remove all saved image files
          </Button>
        </section>
      )}
      <div className="my-5 flex flex-wrap gap-2" aria-label="Image job filters">
        {[
          ["all", "All jobs"],
          ["active", "In progress"],
          ["saved", "Saved images"],
        ].map(([value, label]) => (
          <Button
            key={value}
            className="h-11"
            variant={filter === value ? "default" : "outline"}
            aria-pressed={filter === value}
            onClick={() => setFilter(value)}
          >
            {label}
          </Button>
        ))}
      </div>
      {!visible.length && (
        <p className="py-10 text-center text-fg-2">
          {jobs.length
            ? "No images in this view."
            : "Your images will appear here. Accepted jobs keep running when you close the phone."}
        </p>
      )}
      <section
        className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
        aria-label="Image jobs"
      >
        {visible.map((job) => (
          <article
            key={job.id}
            data-job-id={job.id}
            className="min-w-0 overflow-hidden rounded-xl border border-line bg-surface"
          >
            {job.image_bytes ? (
              preview ? (
                <div
                  className="flex aspect-square items-center justify-center bg-surface-2"
                  role="img"
                  aria-label="Synthetic image placeholder"
                >
                  <ImageIcon className="size-12 text-fg-3" />
                </div>
              ) : (
                <img
                  src={`/api/images/jobs/${job.id}/output/png`}
                  alt={job.prompt}
                  loading="lazy"
                  className="aspect-square w-full object-contain"
                />
              )
            ) : (
              <div className="flex aspect-[3/2] items-center justify-center bg-surface-2 px-4 text-center text-fg-2">
                <span>
                  {job.stage}
                  {job.state === "running" && job.stage === "Generating image"
                    ? ` · ${job.completed_steps} of ${job.steps} steps`
                    : ""}
                </span>
              </div>
            )}
            <div className="p-4">
              <p className="line-clamp-3 break-words text-sm">{job.prompt}</p>
              <p className="mt-2 text-xs text-fg-3">
                {job.state}
                {job.parent_id ? " · Additional version" : ""}
                {job.image_bytes
                  ? ` · ${bytes(job.image_bytes + job.metadata_bytes)}`
                  : ""}
              </p>
              {job.error && (
                <p className="mt-3 text-sm text-danger">{job.error}</p>
              )}
              {job.state === "complete" && !job.image_bytes && (
                <p className="mt-2 text-sm text-fg-2">
                  Saved image files removed.
                </p>
              )}
              <div className="mt-3 flex flex-wrap gap-2">
                {active.has(job.state) && (
                  <Button
                    className="h-11"
                    variant="outline"
                    disabled={job.state === "cancelling"}
                    onClick={() => void action(job, "cancel")}
                  >
                    Cancel
                  </Button>
                )}
                {["failed", "interrupted", "cancelled"].includes(job.state) && (
                  <Button
                    className="h-11"
                    variant="outline"
                    disabled={busy}
                    onClick={() => void action(job, "retry")}
                  >
                    Retry
                  </Button>
                )}
                {!!job.image_bytes && (
                  <Button className="h-11" onClick={() => setSaving(job)}>
                    Save
                  </Button>
                )}
                <Button
                  className="h-11"
                  variant="outline"
                  onClick={() => setDetail(job)}
                >
                  Details
                </Button>
              </div>
            </div>
          </article>
        ))}
      </section>
      {saving && (
        <FileSaveDialog
          title="Save image"
          closeLabel="Close image save"
          initial="png"
          options={[
            {
              format: "png",
              label: "Image (.png)",
              url: `/api/images/jobs/${saving.id}/output/png`,
              filename: `Atelier-${saving.id.slice(0, 8)}.png`,
            },
            {
              format: "json",
              label: "Details (.json)",
              url: `/api/images/jobs/${saving.id}/output/json`,
              filename: `Atelier-${saving.id.slice(0, 8)}.json`,
            },
          ]}
          onClose={() => setSaving(undefined)}
          preview={preview ? "ready" : undefined}
        />
      )}
      <Dialog
        open={!!detail}
        onOpenChange={(open) => !open && setDetail(undefined)}
      >
        <DialogContent className="max-h-[85dvh] overflow-y-auto">
          <DialogTitle>Image details</DialogTitle>
          <DialogDescription>
            Exact inputs and output storage for this job.
          </DialogDescription>
          {detail && (
            <>
              <p className="break-words whitespace-pre-wrap text-sm">
                {detail.prompt}
              </p>
              <p className="text-sm text-fg-2">
                Seed {detail.seed} · 1024 × 1024 · 4 steps · 8-bit · Guidance 1
              </p>
              <p className="text-sm text-fg-2">
                PNG {bytes(detail.image_bytes)} · Details{" "}
                {bytes(detail.metadata_bytes)}
              </p>
              <p className="break-all text-xs text-fg-3">
                {detail.sha256 ?? "No saved output"}
              </p>
              <p className="text-xs text-fg-3">
                Created {new Date(detail.created_at).toLocaleString()}
              </p>
              <div className="flex flex-wrap gap-2">
                <Button
                  className="h-11"
                  onClick={() => {
                    setPrompt(detail.prompt);
                    setSeed("");
                    setParent(detail.id);
                    setDetail(undefined);
                    document.getElementById("image-prompt")?.focus();
                  }}
                >
                  Use prompt for new version
                </Button>
                {!!detail.image_bytes && (
                  <Button
                    className="h-11"
                    variant="outline"
                    onClick={() => {
                      setRemoving(detail);
                      setDetail(undefined);
                    }}
                  >
                    Remove image files
                  </Button>
                )}
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
      <Dialog
        open={!!removing}
        onOpenChange={(open) => !busy && !open && setRemoving(undefined)}
      >
        <DialogContent>
          <DialogTitle>
            {removing === "all"
              ? "Remove all saved image files?"
              : "Remove these image files?"}
          </DialogTitle>
          <DialogDescription>
            {removing === "all"
              ? `${storage?.outputs ?? 0} PNGs and their details (${bytes((storage?.image_bytes ?? 0) + (storage?.metadata_bytes ?? 0))}) will be removed.`
              : "The PNG and downloadable details will be removed."}{" "}
            Job history, model weights, chats and existing backups are kept.
            Active jobs continue.
          </DialogDescription>
          <div className="flex flex-wrap justify-end gap-2">
            <Button
              className="h-11"
              variant="outline"
              disabled={busy}
              onClick={() => setRemoving(undefined)}
            >
              Cancel
            </Button>
            <Button
              className="h-11"
              disabled={busy}
              onClick={() => void remove()}
            >
              Remove files
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}

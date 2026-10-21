import { useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router";
import { ArrowLeft, ImageIcon } from "lucide-react";
import { api } from "@/lib/api";
import { usePreferenceSync } from "@/hooks/usePreferenceSync";
import type { components } from "@/lib/api-types";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { FileSaveDialog } from "@/components/app/FileSaveDialog";
import { IconButton } from "@/components/app/IconButton";
import { imageSeeds } from "@/lib/image-seeds";
import { clearPhotoInputs } from "@/hooks/usePhotoEdit";

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
  const navigate = useNavigate();
  const [filter, setFilter] = useState("all");
  const [saving, setSaving] = useState<Job>();
  const [detail, setDetail] = useState<Job>();
  const [removing, setRemoving] = useState<Job | "all" | "inputs">();
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
      if (job.mode === "edit") {
        if (job.origin && !job.origin.deleted)
          navigate(`/c/${job.origin.chat_id}#m-${job.origin.message_id}`);
        else
          setNotice(
            "Attach the photo in a chat to edit again. No plain generation was started.",
          );
        return;
      }
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
      if (removing === "inputs") {
        await api("/images/references/clear", { confirm: true });
        clearPhotoInputs();
      } else if (removing === "all")
        await api("/images/clear", { confirm: true });
      else await api(`/images/jobs/${removing.id}/output`, undefined, "DELETE");
      setRemoving(undefined);
      setNotice(
        removing === "inputs"
          ? "Inactive photo inputs cleared. Outputs and existing backups are kept."
          : "Saved image files removed. Job history and backups are retained.",
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
  return (
    <>
      <div className="mb-5 flex items-center justify-between gap-3">
        <p className="text-sm text-fg-2">
          Images from your chats and workflows.
        </p>
        <Button className="h-11" onClick={() => navigate("/?image=1")}>
          New image
        </Button>
      </div>
      {status && !status.available && (
        <p role="status" className="mb-4 text-sm text-fg-2">
          {status.reason}
        </p>
      )}
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
            <p className="mt-1 text-sm text-fg-2">
              Photo inputs {bytes(storage.reference_bytes)} · Reference details{" "}
              {bytes(storage.reference_metadata_bytes)} · Export copies{" "}
              {bytes(storage.export_bytes)} · Storage records{" "}
              {bytes(storage.measurement_bytes)}
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
          <Button
            variant="outline"
            className="h-11"
            disabled={
              !storage.references ||
              jobs.some((job) => job.mode === "edit" && active.has(job.state))
            }
            onClick={() => setRemoving("inputs")}
          >
            Clear inactive photo inputs
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
              {job.origin &&
                (job.origin.deleted ? (
                  <p className="mt-2 text-xs text-fg-3">From a deleted chat</p>
                ) : (
                  <Link
                    className="mt-2 flex min-h-11 items-center text-sm text-brand"
                    to={`/c/${job.origin.chat_id}#m-${job.origin.message_id}`}
                  >
                    From {job.origin.title ?? "chat"}
                  </Link>
                ))}
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
                    disabled={
                      busy ||
                      (job.mode === "edit" &&
                        (!job.reference?.available ||
                          !job.origin ||
                          job.origin.deleted))
                    }
                    onClick={() => void action(job, "retry")}
                  >
                    {job.mode === "edit" ? "Open chat to retry" : "Retry"}
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
              filename: `Aether-${saving.id.slice(0, 8)}.png`,
            },
            {
              format: "json",
              label: "Details (.json)",
              url: `/api/images/jobs/${saving.id}/output/json`,
              filename: `Aether-${saving.id.slice(0, 8)}.json`,
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
            {removing === "inputs"
              ? "Clear inactive photo inputs?"
              : removing === "all"
                ? "Remove all saved image files?"
                : "Remove these image files?"}
          </DialogTitle>
          <DialogDescription>
            {removing === "inputs"
              ? "Original and normalized photo inputs will be removed. Completed outputs stay; comparison and retry need reattachment. Existing backups retain their copies until normal backup cleanup."
              : removing === "all"
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

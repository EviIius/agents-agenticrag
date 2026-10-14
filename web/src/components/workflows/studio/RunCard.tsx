import { useState } from "react";
import { Link } from "react-router";
import { api } from "@/lib/api";
import type { Run } from "./types";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { FileSaveDialog } from "@/components/app/FileSaveDialog";
import { Check, Pause, Circle, CircleAlert, RotateCcw } from "lucide-react";
import Markdown from "@/components/chat/Markdown";
import { topoOrder } from "./graph";
import { runLabel } from "./run-state";
import { registry } from "./registry";
type Original = {
  node_id: string;
  source: { text: string; segments: Record<string, unknown>[] };
};
export function RunCard({
  run,
  preview = false,
  selected,
  onSelect,
}: {
  run: Run;
  preview?: boolean;
  selected?: string;
  onSelect?: (nodeId: string) => void;
}) {
  const [save, setSave] = useState(false),
    [source, setSource] = useState<Original[]>(),
    [sourceOpen, setSourceOpen] = useState(false),
    [notice, setNotice] = useState(""),
    [savingImage, setSavingImage] = useState<string>(),
    [favorites, setFavorites] = useState<{
      nodeId: string;
      indices: number[];
    }>();
  const [editValue, setEdited] = useState<{ nodeId: string; value: string }>(),
    [acting, setActing] = useState(false);
  let order: string[];
  try {
    order = topoOrder(run.graph);
  } catch {
    order = run.graph.nodes.map((n) => n.id);
  }
  const paused = run.graph.nodes.find(
    (n) => run.nodes[n.id]?.state === "paused",
  );
  const pauseState = paused && run.nodes[paused.id];
  const edited =
    editValue?.nodeId === paused?.id ? editValue?.value : undefined;
  const originalValue =
    typeof pauseState?.output?.value === "string"
      ? pauseState.output.value
      : typeof pauseState?.output?.prompt === "string"
        ? pauseState.output.prompt
        : "";
  const act = async (path: string, body: unknown = {}) => {
    if (preview) return;
    setActing(true);
    setNotice("");
    try {
      await api(`/workflows/runs/${run.id}/${path}`, body);
    } catch (e) {
      setNotice(e instanceof Error ? e.message : "The action didn't finish.");
    } finally {
      setActing(false);
    }
  };
  return (
    <article className="wf-run-card" aria-label={`${run.def_name} run`}>
      <div className="flex flex-wrap justify-between gap-2">
        <h3 className="font-medium">{run.def_name}</h3>
        <time className="wf-help">
          {new Date(run.created_at).toLocaleString()}
        </time>
      </div>
      <p role="status" className="my-3 text-sm text-fg-2">
        {run.stage} · {run.state}
      </p>
      {run.error && <p className="text-sm text-danger">{run.error}</p>}
      {notice && (
        <p role="alert" className="text-sm text-danger">
          {notice}
        </p>
      )}
      <ol className="wf-run-steps">
        {order.map((id) => {
          const n = run.graph.nodes.find((n) => n.id === id)!;
          const state = run.nodes[n.id];
          const visible =
            selected === n.id ||
            ["running", "failed", "interrupted", "cancelled"].includes(
              state?.state ?? "",
            );
          return (
            <li
              key={n.id}
              data-selected={selected === n.id}
              data-state={state?.state}
            >
              <button
                className="wf-run-step-head text-sm"
                onClick={() => onSelect?.(n.id)}
                aria-label={`View result for ${n.title}`}
                aria-expanded={visible}
              >
                {state?.reused_from ? (
                  <RotateCcw className="size-4" />
                ) : state?.state === "complete" ? (
                  <Check className="size-4 text-success" />
                ) : state?.state === "paused" ? (
                  <Pause className="size-4 text-warning" />
                ) : state?.state === "failed" ? (
                  <CircleAlert className="size-4 text-danger" />
                ) : (
                  <Circle
                    className={`size-4 ${state?.state === "running" ? "activity-spin text-brand" : ""}`}
                  />
                )}
                <span>{n.title}</span>
                <span className="wf-help">{runLabel(run, n.id)}</span>
              </button>
              {state?.progress && (
                <progress
                  className="w-full"
                  aria-label={`Progress for ${n.title}`}
                  value={Number(state.progress.done) || 0}
                  max={Number(state.progress.total) || 1}
                />
              )}
              {state?.warnings?.map((w, i) => (
                <p key={i} className="wf-help">
                  {w}
                </p>
              ))}
              {visible && typeof state?.output?.text === "string" && (
                <div className="wf-stream-preview">
                  <Markdown
                    text={state.output.text}
                    streaming={state.state === "running"}
                    copyFeedbackRole="none"
                  />
                </div>
              )}
              {visible && Array.isArray(state?.output?.images) && (
                <div className="grid grid-cols-2 gap-3">
                  {(state.output.images as { id: string }[]).map((image, i) => (
                    <button
                      key={image.id}
                      aria-label={`Save workflow image ${i + 1}`}
                      onClick={() => setSavingImage(image.id)}
                    >
                      <img
                        className="rounded-lg"
                        alt={`Workflow generated image ${i + 1}`}
                        src={`/api/images/jobs/${image.id}/output/png`}
                      />
                    </button>
                  ))}
                  <Button variant="outline" asChild>
                    <Link to="/images">View and save in Images</Link>
                  </Button>
                </div>
              )}
            </li>
          );
        })}
      </ol>
      {run.state === "paused" && paused && paused.kind !== "pick" && (
        <div className="my-4 space-y-3">
          <label className="wf-field">
            Review {paused.kind === "review" ? paused.title : "image prompt"}
            <Textarea
              aria-label="Review result"
              value={edited ?? originalValue}
              readOnly={paused.kind === "review" && !paused.config.editable}
              onChange={(e) =>
                setEdited({ nodeId: paused.id, value: e.target.value })
              }
              maxLength={paused.kind === "generate_image" ? 4000 : 20000}
            />
          </label>
          {paused.kind === "review" && paused.config.message && (
            <p className="wf-help">{paused.config.message}</p>
          )}
          <div className="flex gap-2">
            <Button
              disabled={acting}
              onClick={() =>
                void act(
                  paused.kind === "review" ? "decision" : "v2/resume",
                  paused.kind === "review"
                    ? {
                        node_id: paused.id,
                        decision: "approve",
                        value: edited ?? originalValue,
                      }
                    : { prompt: edited ?? originalValue },
                )
              }
            >
              Approve
            </Button>
            {paused.kind === "review" && (
              <Button
                variant="outline"
                disabled={acting}
                onClick={() =>
                  void act("decision", {
                    node_id: paused.id,
                    decision: "reject",
                  })
                }
              >
                Reject
              </Button>
            )}
          </div>
        </div>
      )}
      {run.state === "paused" && paused?.kind === "pick" && (
        <section className="my-4 space-y-3" aria-label="Pick favorites">
          <h3>Pick up to {paused.config.maximum}</h3>
          <div className="grid grid-cols-2 gap-2">
            {(
              (pauseState?.output?.choices ?? []) as (string | { id: string })[]
            ).map((choice, index) => {
              const indices =
                favorites?.nodeId === paused.id ? favorites.indices : [];
              return (
                <button
                  key={index}
                  className="wf-pick"
                  aria-label={`Pick result ${index + 1}`}
                  aria-pressed={indices.includes(index)}
                  disabled={
                    !indices.includes(index) &&
                    indices.length >= paused.config.maximum
                  }
                  onClick={() =>
                    setFavorites({
                      nodeId: paused.id,
                      indices: indices.includes(index)
                        ? indices.filter((i) => i !== index)
                        : [...indices, index],
                    })
                  }
                >
                  {typeof choice === "string" ? (
                    <p className="p-2 text-sm">{choice}</p>
                  ) : (
                    <img
                      alt={`Choice ${index + 1}`}
                      src={`/api/images/jobs/${choice.id}/output/png`}
                    />
                  )}
                </button>
              );
            })}
          </div>
          <Button
            disabled={
              acting ||
              favorites?.nodeId !== paused.id ||
              !favorites?.indices.length
            }
            onClick={() =>
              void act("decision", {
                node_id: paused.id,
                decision: "approve",
                chosen: favorites!.indices,
              })
            }
          >
            Keep favorites
          </Button>
        </section>
      )}
      {run.state === "complete" && (run.results ?? []).length > 0 && (
        <section className="wf-run-results" aria-label="Workflow results">
          <h3 className="mb-3 font-semibold">Results</h3>
          {(run.results ?? []).map((section) => (
            <section key={section.node_id} className="space-y-3">
              <h4>{section.label}</h4>
              {section.items.map((item, index) => (
                <div key={index}>
                  <p className="wf-help">{item.label}</p>
                  {item.type === "image_list" && Array.isArray(item.value) ? (
                    <div className="grid grid-cols-2 gap-2">
                      {(item.value as { id: string }[]).map((image, i) => (
                        <button
                          key={image.id}
                          aria-label={`Save result image ${i + 1}`}
                          onClick={() => setSavingImage(image.id)}
                        >
                          <img
                            alt={`Workflow generated image ${i + 1}`}
                            src={`/api/images/jobs/${image.id}/output/png`}
                          />
                        </button>
                      ))}
                    </div>
                  ) : typeof item.value === "string" ? (
                    <Markdown text={item.value} copyFeedbackRole="none" />
                  ) : (
                    <pre className="wf-output-text">
                      {JSON.stringify(item.value, null, 2)}
                    </pre>
                  )}
                </div>
              ))}
            </section>
          ))}
        </section>
      )}
      <div className="my-4 flex flex-wrap gap-2">
        {["running", "queued", "paused", "cancelling"].includes(run.state) && (
          <Button
            variant="outline"
            disabled={acting || run.state === "cancelling"}
            onClick={() => void act("v2/cancel")}
          >
            Cancel workflow
          </Button>
        )}
        {["failed", "interrupted", "cancelled"].includes(run.state) && (
          <Button disabled={acting} onClick={() => void act("v2/resume")}>
            {run.state === "failed" ? "Retry block" : "Retry unfinished steps"}
          </Button>
        )}
        {run.state === "failed" &&
          run.graph.nodes
            .filter(
              (n) =>
                n.kind === "clean_transcript" &&
                run.nodes[n.id]?.state === "failed",
            )
            .map((n) => (
              <Button
                key={n.id}
                variant="outline"
                onClick={() => void act("v2/resume", { skip_node_id: n.id })}
              >
                Continue with original transcript
              </Button>
            ))}
        {run.source_available && (
          <Button
            variant="outline"
            onClick={() => {
              setNotice("");
              void api<Original[]>(`/workflows/runs/${run.id}/v2/sources`).then(
                (v) => {
                  setSource(v);
                  setSourceOpen(true);
                },
                () => setNotice("The saved source couldn't be opened."),
              );
            }}
          >
            View original transcript
          </Button>
        )}
        <Button variant="outline" onClick={() => setSave(true)}>
          Save outputs
        </Button>
      </div>
      <p className="wf-help">
        Draft for review. Check it against the original.
      </p>
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
              url: `/api/workflows/runs/${run.id}/v2/export?format=md`,
              filename: `Atelier-workflow-${run.id.slice(0, 8)}.md`,
            },
            {
              format: "json",
              label: "Details and source (.json)",
              url: `/api/workflows/runs/${run.id}/v2/export?format=json`,
              filename: `Atelier-workflow-${run.id.slice(0, 8)}.json`,
            },
          ]}
        />
      )}
      {savingImage && (
        <FileSaveDialog
          title="Save image"
          closeLabel="Close image save"
          initial="png"
          onClose={() => setSavingImage(undefined)}
          preview={preview ? "ready" : undefined}
          options={[
            {
              format: "png",
              label: "Image (.png)",
              url: `/api/images/jobs/${savingImage}/output/png`,
              filename: `Atelier-${savingImage.slice(0, 8)}.png`,
            },
            {
              format: "json",
              label: "Details (.json)",
              url: `/api/images/jobs/${savingImage}/output/json`,
              filename: `Atelier-${savingImage.slice(0, 8)}.json`,
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
          {source?.map((s) => (
            <section key={s.node_id}>
              <h3 className="text-sm font-medium">
                {run.graph.nodes.find((n) => n.id === s.node_id)?.title ??
                  registry.transcribe.label}
              </h3>
              <pre className="wf-output-text">{s.source.text}</pre>
              <details>
                <summary>Original source timestamps</summary>
                <ol>
                  {s.source.segments.map((segment, i) => (
                    <li key={i}>
                      <span className="wf-help">
                        {String(segment.start)}s–{String(segment.end)}s
                        {segment.speaker ? ` · ${String(segment.speaker)}` : ""}
                      </span>
                      <p className="text-sm">{String(segment.text)}</p>
                    </li>
                  ))}
                </ol>
              </details>
            </section>
          ))}
        </DialogContent>
      </Dialog>
    </article>
  );
}

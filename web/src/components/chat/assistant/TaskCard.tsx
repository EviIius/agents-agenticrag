import { useEffect, useState } from "react";
import { Check, Circle, Monitor, Square } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import type { components } from "@/lib/api-types";
import { terminalTask } from "@/lib/assistant-stream";

export type DesktopTask = components["schemas"]["DesktopTask"];
export type TaskDecision = components["schemas"]["TaskDecision"];

export function TaskCard({
  task,
  onDecision,
  onStop,
}: {
  task: DesktopTask;
  onDecision?: (body: TaskDecision) => Promise<void>;
  onStop?: () => Promise<void>;
}) {
  const [editing, setEditing] = useState(false);
  const [text, setText] = useState(task.approval?.action.text ?? "");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    setText(task.approval?.action.text ?? "");
    setEditing(false);
    setError("");
  }, [task.approval?.id, task.revision, task.approval?.action.text]);
  const decide = async () => {
    if (!task.approval || busy || !text.trim()) return;
    setBusy(true);
    setError("");
    try {
      await onDecision?.({
        approval_id: task.approval.id,
        revision: task.revision,
        decision: "approve",
        text,
      });
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "Could not submit this action.",
      );
    } finally {
      setBusy(false);
    }
  };
  const stop = async () => {
    setBusy(true);
    try {
      await onStop?.();
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "Could not stop this task.",
      );
    } finally {
      setBusy(false);
    }
  };
  const thread = task.observation?.conversation;
  const approval = task.state === "awaiting_approval" && task.approval;
  return (
    <article
      className="my-5 min-w-0 rounded-xl border border-line bg-surface p-4"
      aria-label="Computer task"
    >
      <header className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="flex items-center gap-2 text-sm font-medium">
          <Monitor className="size-4" aria-hidden />
          Fake desktop
        </h2>
        <span className="text-xs text-fg-2">
          {task.observation?.app_name ?? "Computer task"}
        </span>
      </header>
      <p className="mt-3 break-words text-sm">{task.text}</p>
      <p role="status" className="mt-3 text-sm text-fg-2">
        {task.stage}
      </p>
      {task.steps.length > 0 && (
        <ol className="my-4 space-y-2" aria-label="Task progress">
          {task.steps.map((step, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-fg-2">
              {step.state === "complete" ? (
                <Check
                  className="mt-0.5 size-4 shrink-0 text-success"
                  aria-label="Complete"
                />
              ) : (
                <Circle
                  className="mt-0.5 size-4 shrink-0"
                  aria-label={
                    step.state === "awaiting_approval"
                      ? "Needs approval"
                      : "In progress"
                  }
                />
              )}
              <span>{step.label}</span>
            </li>
          ))}
        </ol>
      )}
      {thread && (
        <section
          className="mt-4 rounded-lg border border-line bg-surface-2 p-3"
          aria-label="Selected conversation"
        >
          <h3 className="text-sm font-medium">
            {thread.participants.length === 1
              ? "Reply to"
              : "Choose a conversation"}
          </h3>
          {thread.participants.map((person) => (
            <p key={person.id} className="mt-1 break-all text-sm">
              {person.name} · {person.address}
            </p>
          ))}
          <p className="mt-3 text-xs text-fg-2">Latest incoming message</p>
          <blockquote className="mt-1 whitespace-pre-wrap break-words text-sm">
            {thread.incoming}
          </blockquote>
        </section>
      )}
      {approval && (
        <section
          className="mt-4"
          aria-label={thread ? "Proposed reply" : "Proposed note"}
        >
          <label
            htmlFor={"reply-" + task.id}
            className="mb-2 block text-sm font-medium"
          >
            {thread ? "Proposed reply" : "Proposed note"}
          </label>
          {editing ? (
            <Textarea
              id={"reply-" + task.id}
              value={text}
              onChange={(e) => setText(e.target.value)}
              maxLength={4000}
              disabled={busy}
            />
          ) : (
            <p className="whitespace-pre-wrap break-words rounded-lg border border-line p-3 text-sm">
              {text}
            </p>
          )}
          <div className="mt-3 flex flex-wrap gap-2">
            <Button
              className="min-h-11"
              onClick={() => void decide()}
              disabled={busy || !text.trim() || !onDecision}
            >
              {thread ? "Send (fake)" : "Apply (fake)"}
            </Button>
            <Button
              variant="outline"
              className="min-h-11"
              onClick={() => setEditing((old) => !old)}
              disabled={busy}
            >
              {editing ? "Done editing" : "Edit"}
            </Button>
            <Button
              variant="ghost"
              className="min-h-11"
              onClick={() => void stop()}
              disabled={busy || !onStop}
            >
              Cancel
            </Button>
          </div>
        </section>
      )}
      {!approval && task.approved_action && (
        <section className="mt-4" aria-label="Approved action">
          <h3 className="text-sm font-medium">Approved text</h3>
          <p className="mt-2 whitespace-pre-wrap break-words text-sm">
            {task.approved_action.text}
          </p>
        </section>
      )}
      {!approval && !terminalTask(task) && (
        <Button
          variant="outline"
          className="mt-4 min-h-11"
          disabled={busy || !onStop}
          onClick={() => void stop()}
        >
          <Square className="size-4" aria-hidden />
          Stop task
        </Button>
      )}
      {error && (
        <p role="alert" className="mt-3 text-sm text-danger">
          {error}
        </p>
      )}
      <p className="mt-4 text-xs text-fg-2">
        Scripted demonstration. No Mac app is controlled and no message is sent.
      </p>
    </article>
  );
}

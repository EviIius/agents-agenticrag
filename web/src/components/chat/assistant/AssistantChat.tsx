import { useEffect, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Composer } from "@/components/chat/Composer";
import { api, type Chat, type Model } from "@/lib/api";
import type { components } from "@/lib/api-types";
import { TaskCard, type DesktopTask, type TaskDecision } from "./TaskCard";

import { attachDesktopTasks, terminalTask } from "@/lib/assistant-stream";

type TaskList = components["schemas"]["TaskList"];
export default function AssistantChat({
  chatId,
  parentId,
  onCreated,
  onExit,
  model,
}: {
  chatId?: string;
  parentId?: string | null;
  onCreated: (id: string) => void;
  onExit: () => void;
  model?: Model;
}) {
  const query = useQueryClient();
  const [fixture, setFixture] = useState<"messages" | "notes">("messages");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const key = ["assistant-tasks", chatId];
  const tasks = useQuery({
    queryKey: key,
    queryFn: () => api<TaskList>(`/chats/${chatId}/assistant-tasks`),
    enabled: !!chatId,
  });
  const put = (task: DesktopTask) =>
    query.setQueryData<TaskList>(["assistant-tasks", task.chat_id], (old) => {
      const rows = old?.tasks ?? [];
      const prior = rows.find((t) => t.id === task.id);
      if (prior && prior.revision > task.revision) return old;
      return {
        tasks: prior
          ? rows.map((t) => (t.id === task.id ? task : t))
          : [...rows, task],
      };
    });
  const activeIds = (tasks.data?.tasks ?? [])
    .filter((t) => !terminalTask(t))
    .map((t) => t.id)
    .join(",");
  const putRef = useRef(put);
  putRef.current = put;
  const [reconnecting, setReconnecting] = useState(false);
  useEffect(() => {
    if (!activeIds) return;
    return attachDesktopTasks(
      activeIds.split(","),
      (task) => putRef.current(task),
      setReconnecting,
    );
  }, [activeIds]);
  const decide = async (id: string, body: TaskDecision) => {
    put(await api<DesktopTask>(`/assistant/tasks/${id}/decision`, body));
  };
  const stop = async (id: string) => {
    put(await api<DesktopTask>(`/assistant/tasks/${id}/cancel`, {}));
  };
  const attempt = useRef<{
    id: string;
    text: string;
    fixture: typeof fixture;
    key: string;
  } | null>(null);
  const send = async (text: string) => {
    if (busy) return false;
    setBusy(true);
    setError("");
    try {
      if (
        attempt.current &&
        (attempt.current.text !== text || attempt.current.fixture !== fixture)
      ) {
        attempt.current = null;
      }
      const id =
        attempt.current?.id ??
        chatId ??
        (
          await api<Chat>("/chats", {
            connection_id: model?.connection_id,
            model_id: model?.model_id,
          })
        ).id;
      attempt.current ??= { id, text, fixture, key: crypto.randomUUID() };
      const task = await api<DesktopTask>(`/chats/${id}/assistant-tasks`, {
        request_key: attempt.current.key,
        text,
        fixture,
        parent_id: parentId ?? null,
      } satisfies components["schemas"]["TaskCreate"]);
      put(task);
      attempt.current = null;
      if (!chatId) onCreated(id);
      return true;
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "Could not start this task.",
      );
      return false;
    } finally {
      setBusy(false);
    }
  };
  return (
    <>
      <div className="thread-scroll" aria-label="Computer tasks">
        <div className="mx-auto w-full max-w-3xl px-4 py-5">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h1 className="text-lg font-medium">Computer use</h1>
            <Button variant="ghost" className="min-h-11" onClick={onExit}>
              Back to chat
            </Button>
          </div>
          <p className="mt-2 text-sm text-fg-2">
            Fake desktop preview · select a scripted task and type a request. No
            model is called.
          </p>
          <fieldset className="mt-4">
            <legend className="mb-2 text-sm">Demo task</legend>
            <div className="flex flex-wrap gap-2">
              {(["messages", "notes"] as const).map((value) => (
                <Button
                  key={value}
                  className="min-h-11"
                  variant={fixture === value ? "default" : "outline"}
                  aria-pressed={fixture === value}
                  onClick={() => setFixture(value)}
                >
                  {value === "messages" ? "Messages demo" : "Notes demo"}
                </Button>
              ))}
            </div>
          </fieldset>
          {tasks.isError && (
            <p role="alert" className="mt-4 text-sm text-danger">
              Could not load computer tasks.{" "}
              <Button
                variant="link"
                className="min-h-11"
                onClick={() => void tasks.refetch()}
              >
                Retry
              </Button>
            </p>
          )}
          {reconnecting && (
            <p role="status" className="mt-3 text-sm text-fg-2">
              Reconnecting to task updates…
            </p>
          )}
          <div role="log" aria-live="off" aria-label="Task history">
            {(tasks.data?.tasks ?? []).map((task) => (
              <TaskCard
                key={task.id}
                task={task}
                onDecision={(body) => decide(task.id, body)}
                onStop={() => stop(task.id)}
              />
            ))}
          </div>
        </div>
      </div>
      <div className="composer-row">
        <Composer
          attachmentsAllowed={false}
          draftKey={`assistant:${chatId ?? "new"}`}
          model={{
            connection_id: "fake-desktop",
            model_id: "fake-desktop",
            display_name: "Fake desktop",
            params_defaults: {},
            chat_capable: true,
            hidden: false,
            embedding: false,
          }}
          onSend={send}
          disabled={busy}
          error={error}
        />
      </div>
    </>
  );
}

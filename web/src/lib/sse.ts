import { useTranscripts } from "@/stores/transcripts";
import type { Message, Detail, TranscriptionEvent } from "./api";
import { useRuns } from "@/stores/runs";
import { cited } from "./citations";
import type { QueryClient } from "@tanstack/react-query";
const attached = new Map<string, EventSource>();
const finished = new Set<string>();
function rememberFinished(id: string) {
  finished.add(id);
  if (finished.size > 256) finished.delete(finished.values().next().value!);
}
export function attachRun(
  id: string,
  chatId: string,
  snapshot: Message,
  query: QueryClient,
) {
  if (attached.has(id) || finished.has(id) || snapshot.status !== "streaming")
    return;
  useRuns.getState().put(id, {
    chatId,
    message: { ...snapshot, content: "", reasoning: null },
    stage: "waiting",
    steps: [],
  });
  const source = new EventSource("/api/runs/" + id + "/events");
  attached.set(id, source);
  let text = "",
    reasoning = "",
    frame = 0;
  let closed = false;
  const flush = () => {
    frame = 0;
    const run = useRuns.getState().runs[id];
    if (!run) return;
    const message = {
      ...run.message,
      content: run.message.content + text,
      reasoning: (run.message.reasoning ?? "") + reasoning,
    };
    const stage = text ? "streaming" : reasoning ? "reasoning" : run.stage;
    text = "";
    reasoning = "";
    useRuns.getState().patch(id, { message, stage });
  };
  const schedule = () => {
    if (!frame) frame = requestAnimationFrame(flush);
  };
  for (const type of [
    "text.delta",
    "reasoning.delta",
    "run.started",
    "run.queued",
    "message.done",
    "message.error",
    "chat.title",
    "run.closed",
    "search.planning",
    "search.queries",
    "search.skipped",
    "search.results",
    "search.reading",
    "search.read",
    "search.done",
    "search.failed",
  ]) {
    source.addEventListener(type, (event) => {
      if (closed) return;
      const data = JSON.parse((event as MessageEvent<string>).data);
      if (type === "text.delta") {
        text += data.text;
        schedule();
        return;
      }
      if (type === "reasoning.delta") {
        reasoning += data.text;
        schedule();
        return;
      }
      if (type === "run.started")
        useRuns.getState().patch(id, {
          stage: data.model_loaded === false ? "loading-model" : "waiting",
        });
      if (type === "run.queued")
        useRuns
          .getState()
          .patch(id, { stage: "queued", position: data.position });
      if (type === "search.done")
        useRuns
          .getState()
          .patch(id, { sources: data.sources, stage: "waiting" });
      if (type.startsWith("search.")) {
        const existing = useRuns.getState().runs[id];
        if (existing) {
          const web = existing.message.web ?? {
            status: "used" as const,
            queries: [],
            providers: [],
            timings: {},
            source_count: 0,
            plan_fallback: false,
            ranking: "keyword",
          };
          if (type === "search.queries") web.queries = data.queries;
          if (type === "search.results")
            web.providers = data.provider ? data.provider.split(", ") : [];
          if (type === "search.skipped") {
            web.status = "skipped";
            if (data.reason === "recording")
              web.notice = { code: "search_blocked_recording", message: "" };
          }
          if (type === "search.failed") {
            web.status = "failed";
            web.notice = { code: data.code, message: data.message };
          }
          if (type === "search.done") {
            web.timings = data.timings;
            web.source_count = data.sources.length;
          }
          useRuns
            .getState()
            .patch(id, { message: { ...existing.message, web: { ...web } } });
        }
        const run = useRuns.getState().runs[id];
        if (run)
          useRuns.getState().patch(id, {
            stage:
              type === "search.done" ||
              type === "search.skipped" ||
              type === "search.failed"
                ? "waiting"
                : "search",
            steps: [
              ...run.steps,
              {
                label: type.replace("search.", ""),
                detail:
                  data.url ?? data.queries?.join(" · ") ?? data.message ?? "",
                status:
                  type === "search.failed" || data.status === "failed"
                    ? "failed"
                    : "ok",
              },
            ],
          });
      }
      if (type === "message.done" || type === "message.error") {
        if (frame) cancelAnimationFrame(frame);
        frame = 0;
        text = "";
        reasoning = "";
        const message = data.message_snapshot ?? data.message;
        const ids = cited(message.content);
        const sources = useRuns.getState().runs[id]?.sources;
        useRuns.getState().patch(id, {
          message,
          ...(sources
            ? {
                sources: sources.map((source) => ({
                  ...source,
                  cited: ids.has(source.n),
                })),
              }
            : {}),
          stage: "done",
        });
        void query.invalidateQueries({ queryKey: ["chat", chatId] });
        void query.invalidateQueries({ queryKey: ["chats"] });
        void query.invalidateQueries({ queryKey: ["models"] });
      }
      if (type === "chat.title")
        void query.invalidateQueries({ queryKey: ["chats"] });
      if (type === "run.closed") {
        closed = true;
        rememberFinished(id);
        source.close();
        attached.delete(id);
        if (frame) cancelAnimationFrame(frame);
        // Keep final rendering until the authoritative chat fetch resolves.
        void query
          .invalidateQueries({ queryKey: ["chat", chatId] })
          .then(() => {
            const final = useRuns.getState().runs[id];
            if (final && final.message.status !== "streaming") {
              // The first chat request may have captured a streaming row before
              // completion. Its late response must not replace the SSE snapshot.
              query.setQueryData<Detail>(["chat", chatId], (detail) => {
                if (!detail) return detail;
                const stored = detail.messages.find(
                  (m) => m.id === final.message.id,
                );
                if (stored && stored.status !== "streaming") return detail;
                return {
                  ...detail,
                  messages: stored
                    ? detail.messages.map((m) =>
                        m.id === final.message.id ? final.message : m,
                      )
                    : [...detail.messages, final.message],
                  sources: final.sources
                    ? { ...detail.sources, [final.message.id]: final.sources }
                    : detail.sources,
                };
              });
            }
            useRuns.getState().remove(id);
          });
        void query.invalidateQueries({ queryKey: ["active"] });
        void query.invalidateQueries({ queryKey: ["chats"] });
      }
    });
  }
  let recovering = false;
  source.onerror = () => {
    if (source.readyState !== EventSource.CLOSED || recovering) return;
    recovering = true;
    void fetch("/api/runs/active")
      .then((response) => (response.ok ? response.json() : Promise.reject()))
      .then(
        (
          active: import("./api-types").components["schemas"]["ActiveRun"][],
        ) => {
          if (!active.some((run) => run.run_id === id)) {
            closed = true;
            rememberFinished(id);
            source.close();
            attached.delete(id);
            if (frame) cancelAnimationFrame(frame);
            void query
              .invalidateQueries({ queryKey: ["chat", chatId] })
              .then(() => useRuns.getState().remove(id));
          }
        },
      )
      .catch(() => {
        /* EventSource reconnects when the network recovers. */
      });
  };
  return source;
}

const transcriptionStreams = new Map<string, EventSource>();
export function detachTranscription(id: string) {
  transcriptionStreams.get(id)?.close();
  transcriptionStreams.delete(id);
}
export function attachTranscription(attachment: import("./api").Attachment) {
  if (transcriptionStreams.has(attachment.id)) return;
  useTranscripts.getState().put(attachment);
  if (
    !attachment.transcript ||
    (!["queued", "transcribing"].includes(attachment.transcript.status) &&
      attachment.transcript.cleanup?.status !== "running")
  )
    return;
  const source = new EventSource(`/api/attachments/${attachment.id}/events`);
  transcriptionStreams.set(attachment.id, source);
  for (const type of [
    "transcription.queued",
    "transcription.started",
    "transcription.done",
    "transcription.failed",
    "transcription.cancelled",
    "cleanup.started",
    "cleanup.progress",
    "cleanup.done",
    "cleanup.failed",
    "stream.closed",
  ]) {
    source.addEventListener(type, (event) => {
      const payload = {
        type,
        data: JSON.parse((event as MessageEvent<string>).data),
      } as TranscriptionEvent;
      const item = useTranscripts.getState().attachments[attachment.id];
      if (payload.type === "transcription.started" && item?.transcript)
        useTranscripts.getState().put({
          ...item,
          transcript: {
            ...item.transcript,
            status: "transcribing",
            started_at: payload.data.started_at,
          },
        });
      if (payload.type === "transcription.queued" && item?.transcript)
        useTranscripts.getState().put({
          ...item,
          transcript: { ...item.transcript, status: "queued" },
        });
      if (payload.type === "cleanup.progress" && item?.transcript?.cleanup)
        useTranscripts.getState().put({
          ...item,
          transcript: {
            ...item.transcript,
            cleanup: {
              ...item.transcript.cleanup,
              done: payload.data.done,
              chunks: payload.data.total,
            },
          },
        });
      if ("attachment" in payload.data)
        useTranscripts
          .getState()
          .put(payload.data.attachment as import("./api").Attachment);
      if (payload.type === "stream.closed") detachTranscription(attachment.id);
    });
  }
  // EventSource resumes using Last-Event-ID after a disconnect, without polling.
}

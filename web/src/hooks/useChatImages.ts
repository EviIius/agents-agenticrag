import { useEffect, useRef, useState } from "react";
import type { QueryClient } from "@tanstack/react-query";
import type { NavigateFunction } from "react-router";
import {
  api,
  ApiError,
  type Chat,
  type Detail,
  type Message,
  type Model,
} from "@/lib/api";
import type { components } from "@/lib/api-types";
import { imageSeeds } from "@/lib/image-seeds";
import {
  imageActive,
  imageEvents,
  receiveImages,
  useImageJobs,
} from "@/lib/image-events";
import { drafts } from "@/lib/composer-drafts";
import { useFreshRows } from "@/stores/fresh";
import type { PhotoSubmission } from "./usePhotoEdit";

type Accepted = components["schemas"]["ChatImageResponse"];
type Submission = {
  signature: string;
  chat?: Chat;
  key: string;
  seeds: number[];
};
const submissions = new Map<string, Submission>();

export function useChatImages({
  chatId,
  query,
  navigate,
  current,
  blocked,
  messages,
  enabled,
}: {
  chatId?: string;
  query: QueryClient;
  navigate: NavigateFunction;
  current?: Model;
  blocked: boolean;
  messages: Message[];
  enabled: boolean;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const activeChat = useRef(chatId);
  activeChat.current = chatId;
  const live = useImageJobs((state) => state.jobs);
  const merged = messages.map((message) =>
    message.images?.length
      ? {
          ...message,
          images: message.images.map((job) =>
            live[job.id]?.updated_at > job.updated_at ? live[job.id] : job,
          ),
        }
      : message,
  );
  const active = merged.some((message) => message.images?.some(imageActive));
  const hasEdits = messages.some((message) =>
    message.images?.some((job) => job.mode === "edit"),
  );
  useEffect(() => {
    setError("");
  }, [chatId]);
  useEffect(() => {
    if (!enabled || (!active && !hasEdits)) return;
    // Seed accepted jobs before the first snapshot so session completions reveal.
    receiveImages(messages.flatMap((message) => message.images ?? []));
    return imageEvents();
    // Subscribe for the lifetime of active jobs, not each progress tick.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled, active, hasEdits, chatId]);

  function commit(id: string, response: Accepted, chat?: Chat) {
    const rows = [response.user, response.assistant].filter(
      (row) => row != null,
    );
    query.setQueryData<Detail>(["chat", id], (old) => ({
      ...(old ?? { chat: chat!, messages: [] }),
      chat: { ...(old?.chat ?? chat!), current_leaf_id: response.assistant.id },
      messages: [
        ...(old?.messages ?? []).filter(
          (message) => !rows.some((row) => row.id === message.id),
        ),
        ...rows,
      ],
    }));
    for (const row of rows) useFreshRows.getState().add(row.id);
    receiveImages(response.assistant.images ?? []);
    void query.invalidateQueries({ queryKey: ["chat", id] });
    void query.invalidateQueries({ queryKey: ["chats"] });
    void query.invalidateQueries({ queryKey: ["context", id] });
  }

  async function send(
    prompt: string,
    count: number,
    fixed?: number[],
    sourceJob?: string,
    photo?: PhotoSubmission,
  ) {
    if (busy || blocked) return false;
    const origin = chatId ?? "new";
    const signature = JSON.stringify([
      prompt,
      count,
      fixed,
      sourceJob,
      photo?.reference.id,
      photo?.selection,
    ]);
    let saved = submissions.get(origin);
    if (!saved || saved.signature !== signature) {
      saved = {
        signature,
        chat:
          photo && saved?.chat?.id !== photo.reference.chat_id
            ? undefined
            : saved?.chat,
        key: crypto.randomUUID(),
        seeds: fixed ?? imageSeeds(count),
      };
      submissions.set(origin, saved);
    }
    setBusy(true);
    setError("");
    try {
      if (!saved.chat)
        saved.chat = chatId
          ? query.getQueryData<Detail>(["chat", chatId])?.chat
          : photo
            ? (await api<Detail>(`/chats/${photo.reference.chat_id}`)).chat
            : await api<Chat>(
                "/chats",
                current
                  ? {
                      connection_id: current.connection_id,
                      model_id: current.model_id,
                    }
                  : {},
              );
      const id = chatId ?? saved.chat!.id;
      const response = await api<Accepted>(`/chats/${id}/images`, {
        request_key: saved.key,
        prompt,
        count,
        seeds: saved.seeds,
        ...(sourceJob ? { source_job_id: sourceJob } : {}),
        ...(photo ? { reference_id: photo.reference.id } : {}),
        ...(photo?.selection ? { selection: photo.selection } : {}),
      });
      commit(id, response, saved.chat);
      submissions.delete(origin);
      photo?.accepted(id, !chatId && activeChat.current === chatId);
      if (!chatId && activeChat.current === chatId) {
        if (drafts.has("new")) drafts.set(id, drafts.get("new")!);
        navigate(`/c/${id}`, { flushSync: true, state: { imageMode: !photo } });
      }
      return true;
    } catch (failure) {
      photo?.rejected(failure instanceof ApiError ? failure.code : undefined);
      if (activeChat.current === chatId)
        setError(
          failure instanceof Error
            ? failure.message
            : "Couldn't submit this image. Retry uses the same inputs.",
        );
      return false;
    } finally {
      setBusy(false);
    }
  }

  async function action(message: Message, kind: "retry" | "cancel") {
    if (busy || (kind === "retry" && blocked)) return;
    setBusy(true);
    setError("");
    try {
      const origin = `retry-${message.id}`;
      let saved = submissions.get(origin);
      if (!saved) {
        saved = {
          signature: origin,
          key: crypto.randomUUID(),
          seeds: imageSeeds(message.images?.length ?? 1),
        };
        submissions.set(origin, saved);
      }
      const response = await api<Accepted>(
        `/chats/${message.chat_id}/messages/${message.id}/images/${kind}`,
        kind === "retry" ? { request_key: saved.key, seeds: saved.seeds } : {},
      );
      if (kind === "retry") submissions.delete(origin);
      if (kind === "retry") commit(message.chat_id, response);
      else {
        receiveImages(response.assistant.images ?? []);
        void query.invalidateQueries({ queryKey: ["chat", message.chat_id] });
      }
    } catch (failure) {
      setError(
        failure instanceof Error
          ? failure.message
          : "Image action failed. Try again.",
      );
    } finally {
      setBusy(false);
    }
  }
  return {
    messages: merged,
    jobs: Object.values(live),
    busy,
    error,
    send,
    action,
  };
}

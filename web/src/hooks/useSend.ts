import {
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  type Dispatch,
  type SetStateAction,
  type RefObject,
} from "react";
import type { NavigateFunction } from "react-router";
import type { QueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  api,
  ApiError,
  type Attachment,
  type Bootstrap,
  type Chat,
  type Detail,
  type Message,
  type Model,
  type Params,
  type RunResponse,
} from "@/lib/api";
import { errorCopy } from "@/lib/errors";
import { attachRun } from "@/lib/sse";
export function useSendState(chatId?: string) {
  const [busy, setBusy] = useState(false),
    [pending, setPending] = useState("");
  const [sendError, setSendError] = useState("");
  const stopRequested = useRef(false);
  const restoreComposerFocus = useRef(false);
  useLayoutEffect(() => {
    if (restoreComposerFocus.current) {
      restoreComposerFocus.current = false;
      document
        .querySelector<HTMLTextAreaElement>(".composer textarea")
        ?.focus();
    }
  }, [chatId]);
  useEffect(() => {
    setPending("");
  }, [chatId]);
  return {
    busy,
    setBusy,
    pending,
    setPending,
    sendError,
    setSendError,
    stopRequested,
    restoreComposerFocus,
  };
}
export function useSend({
  query,
  navigate,
  chatId,
  current,
  running,
  modelOperation,
  waitingForTranscript,
  detail,
  web,
  draftParams,
  draftPrompt,
  effectiveFiles,
  setFiles,
  bootstrap,
  runEntry,
  refresh,
  busy,
  setBusy,
  setPending,
  setSendError,
  stopRequested,
  restoreComposerFocus,
}: {
  query: QueryClient;
  navigate: NavigateFunction;
  chatId?: string;
  current?: Model;
  running: boolean;
  modelOperation: RefObject<boolean>;
  waitingForTranscript: boolean;
  detail: { data?: Detail };
  web: boolean;
  draftParams: Params;
  draftPrompt: string | null;
  effectiveFiles: Attachment[];
  setFiles: Dispatch<SetStateAction<Attachment[]>>;
  bootstrap: { data?: Bootstrap };
  runEntry?: [string, { stage: string; message: Message }];
  refresh: () => void;
} & ReturnType<typeof useSendState>) {
  const onSend = async (text: string, parent?: string | null) => {
    if (!current || running || modelOperation.current || waitingForTranscript)
      return false;
    setSendError("");
    stopRequested.current = false;
    setBusy(true);
    setPending(text);
    try {
      let id = chatId;
      let chat = detail.data?.chat;
      if (!id) {
        chat = await api<Chat>("/chats", {
          connection_id: current.connection_id,
          model_id: current.model_id,
          web_enabled: web,
        });
        id = chat.id;
        if (Object.keys(draftParams).length || draftPrompt !== null)
          await api(
            "/chats/" + id,
            { params: draftParams, system_prompt: draftPrompt },
            "PATCH",
          );
      }
      const response = await api<RunResponse>("/chats/" + id + "/messages", {
        content: text,
        parent_id:
          parent === undefined ? (chat?.current_leaf_id ?? null) : parent,
        attachment_ids: effectiveFiles.map((f) => f.id),
        web: chat?.web_enabled ?? web,
      });
      if (!chatId) {
        restoreComposerFocus.current =
          document.activeElement?.matches(".composer textarea") ?? false;
        navigate("/c/" + id);
      }
      setFiles([]);
      void query.invalidateQueries({ queryKey: ["pending-recordings"] });
      setPending("");
      attachRun(response.run_id, id, response.assistant_message, query);
      if (stopRequested.current) {
        await api(`/runs/${response.run_id}/cancel`, {});
        stopRequested.current = false;
      }
      void query.invalidateQueries({ queryKey: ["chat", id] });
      void query.invalidateQueries({ queryKey: ["chats"] });
      if (bootstrap.data?.settings["new_chat_model"] !== "fixed")
        void api(
          "/settings",
          {
            default_connection_id: current.connection_id,
            default_model_id: current.model_id,
          },
          "PATCH",
        );
      return true;
    } catch (e) {
      setSendError(
        errorCopy(
          e instanceof ApiError ? e.code : "provider_error",
          e instanceof Error ? e.message : String(e),
          current,
          bootstrap.data?.connections.find(
            (c) => c.id === current.connection_id,
          ),
        ),
      );
      setPending("");
      return false;
    } finally {
      setBusy(false);
    }
  };
  const regenerate = async (message: Message, force = false, model?: Model) => {
    if (running) return;
    stopRequested.current = false;
    setBusy(true);
    try {
      const response = await api<RunResponse>(
        "/messages/" + message.id + "/regenerate",
        {
          force_web: force,
          ...(model
            ? { connection_id: model.connection_id, model_id: model.model_id }
            : {}),
        },
      );
      attachRun(
        response.run_id,
        message.chat_id,
        response.assistant_message,
        query,
      );
      if (stopRequested.current) {
        await api(`/runs/${response.run_id}/cancel`, {});
        stopRequested.current = false;
      }
      refresh();
    } catch (e) {
      toast(String(e));
    } finally {
      setBusy(false);
    }
  };
  const stop = () => {
    document.querySelector<HTMLTextAreaElement>(".composer textarea")?.focus();
    if (runEntry && runEntry[1].stage !== "done")
      void api("/runs/" + runEntry[0] + "/cancel", {}).catch(() =>
        toast.error("Couldn’t stop the response. Try again."),
      );
    else if (busy) stopRequested.current = true;
  };
  return { onSend, regenerate, stop };
}

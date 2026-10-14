import { useCallback, useEffect, useRef, useState } from "react";
import { ConflictError, saveDefinition } from "./api";
import type { StudioStore } from "./store";
import { useStudio } from "./store";
import { useQueryClient } from "@tanstack/react-query";
export function useAutosave(store: StudioStore, enabled = true) {
  const draft = useStudio((s) => s.draft),
    revision = useStudio((s) => s.revision),
    status = useStudio((s) => s.saveState);
  const [retry, setRetry] = useState(0);
  const busy = useRef(false),
    forceNext = useRef(false);
  const query = useQueryClient();
  const flush = useCallback(async () => {
    if (
      !enabled ||
      busy.current ||
      store.getState().dragging ||
      (store.getState().saveState === "conflict" && !forceNext.current)
    )
      return false;
    const s = store.getState();
    if (JSON.stringify(s.draft) === s.saved) {
      s.status("saved");
      return true;
    }
    busy.current = true;
    const sent = structuredClone(s.draft);
    const force = forceNext.current;
    forceNext.current = false;
    s.status("saving");
    try {
      const accepted = await saveDefinition(s.id, sent, s.version, force);
      store.getState().accepted(accepted, sent);
      void query.invalidateQueries({ queryKey: ["workflow-definitions"] });
      return true;
    } catch (e) {
      store
        .getState()
        .status(
          e instanceof ConflictError ? "conflict" : "failed",
          e instanceof ConflictError ? e.current : undefined,
        );
      return false;
    } finally {
      busy.current = false;
      setRetry((v) => v + 1);
    }
  }, [enabled, query, store]);
  useEffect(() => {
    if (
      !enabled ||
      status === "conflict" ||
      status === "failed" ||
      JSON.stringify(draft) === store.getState().saved
    )
      return;
    const timer = setTimeout(() => void flush(), 800);
    return () => clearTimeout(timer);
  }, [draft, revision, status, retry, flush, enabled, store]);
  useEffect(() => {
    const online = () => {
      if (store.getState().saveState !== "conflict") {
        store.getState().status("saving");
        setRetry((v) => v + 1);
      }
    };
    const leave = (event: BeforeUnloadEvent) => {
      if (
        enabled &&
        JSON.stringify(store.getState().draft) !== store.getState().saved
      ) {
        event.preventDefault();
        event.returnValue = "";
      }
    };
    window.addEventListener("online", online);
    window.addEventListener("beforeunload", leave);
    return () => {
      window.removeEventListener("online", online);
      window.removeEventListener("beforeunload", leave);
    };
  }, [enabled, store]);
  return {
    flush,
    retry: () => {
      store.getState().status("saving");
      setRetry((v) => v + 1);
    },
    keepMine: async () => {
      const s = store.getState();
      if (!s.conflict) return;
      store.setState({
        version: s.conflict.version,
        conflict: undefined,
        saveState: "saving",
      });
      forceNext.current = true;
      await flush();
    },
  };
}

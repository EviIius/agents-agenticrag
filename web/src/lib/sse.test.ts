import { afterEach, expect, it, vi } from "vitest";
import { QueryClient } from "@tanstack/react-query";
import type { Message } from "./api";
import { attachRun } from "./sse";
import { useRuns } from "@/stores/runs";

afterEach(() => {
  vi.unstubAllGlobals();
  useRuns.setState({ runs: {} });
});

it("a stale active-run snapshot cannot restart a completed stream", async () => {
  const listeners = new Map<string, (event: { data: string }) => void>();
  const close = vi.fn();
  const construct = vi.fn();
  vi.stubGlobal(
    "EventSource",
    class {
      constructor() {
        construct();
      }
      addEventListener(
        type: string,
        callback: (event: { data: string }) => void,
      ) {
        listeners.set(type, callback);
      }
      close = close;
    },
  );
  const query = new QueryClient();
  const streaming = {
    id: "assistant-race",
    chat_id: "chat-race",
    status: "streaming",
    content: "",
    reasoning: null,
  } as Message;
  attachRun("closed-race", "chat-race", streaming, query);
  const final = {
    ...streaming,
    status: "complete",
    content: "Finished answer",
  };
  listeners.get("message.done")!({ data: JSON.stringify({ message: final }) });
  listeners.get("run.closed")!({ data: "{}" });
  // A stale bootstrap response arrives before the final chat refetch settles.
  attachRun("closed-race", "chat-race", streaming, query);
  expect(construct).toHaveBeenCalledTimes(1);
  expect(useRuns.getState().runs["closed-race"]?.message.content).toBe(
    "Finished answer",
  );
  expect(close).toHaveBeenCalledOnce();
  await vi.waitFor(() =>
    expect(useRuns.getState().runs["closed-race"]).toBeUndefined(),
  );
});

it("terminal message snapshots never attach a new stream", () => {
  const construct = vi.fn();
  vi.stubGlobal("EventSource", construct);
  for (const status of [
    "complete",
    "stopped",
    "error",
    "interrupted",
  ] as const) {
    attachRun(status, "chat", { status } as Message, new QueryClient());
  }
  expect(construct).not.toHaveBeenCalled();
});

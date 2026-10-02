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

it("a late streaming chat fetch cannot discard the final SSE answer", async () => {
  const listeners = new Map<string, (event: { data: string }) => void>();
  vi.stubGlobal(
    "EventSource",
    class {
      addEventListener(
        type: string,
        callback: (event: { data: string }) => void,
      ) {
        listeners.set(type, callback);
      }
      close() {}
    },
  );
  const query = new QueryClient();
  const streaming = {
    id: "late-fetch-message",
    chat_id: "late-fetch-chat",
    status: "streaming",
    content: "",
    reasoning: null,
  } as Message;
  let release!: () => void;
  const pending = new Promise<void>((resolve) => {
    release = resolve;
  });
  vi.spyOn(query, "invalidateQueries").mockImplementation(() => pending);
  attachRun("late-fetch-run", "late-fetch-chat", streaming, query);
  const final = {
    ...streaming,
    status: "complete",
    content: "Authoritative final answer",
  };
  listeners.get("message.done")!({ data: JSON.stringify({ message: final }) });
  listeners.get("run.closed")!({ data: "{}" });
  query.setQueryData(["chat", "late-fetch-chat"], {
    messages: [streaming],
    sources: {},
    reads: {},
  });
  release();
  await vi.waitFor(() =>
    expect(useRuns.getState().runs["late-fetch-run"]).toBeUndefined(),
  );
  const detail = query.getQueryData<{ messages: Message[] }>([
    "chat",
    "late-fetch-chat",
  ]);
  expect(detail!.messages[0].status).toBe("complete");
  expect(detail!.messages[0].content).toBe("Authoritative final answer");
});

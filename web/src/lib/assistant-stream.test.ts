import { afterEach, expect, it, vi } from "vitest";
import { attachDesktopTask, type DesktopTask } from "./assistant-stream";

afterEach(() => vi.unstubAllGlobals());

function harness() {
  let listener: (event: { data: string }) => void = () => {};
  let paint: FrameRequestCallback = () => {};
  const close = vi.fn();
  const cancel = vi.fn();
  const snapshot = vi.fn();
  const connection = vi.fn();
  let source: { onopen?: () => void; onerror?: () => void } = {};
  vi.stubGlobal(
    "requestAnimationFrame",
    vi.fn((callback: FrameRequestCallback) => {
      paint = callback;
      return 42;
    }),
  );
  vi.stubGlobal("cancelAnimationFrame", cancel);
  vi.stubGlobal(
    "EventSource",
    class {
      onopen?: () => void;
      onerror?: () => void;
      constructor() {
        source = this;
      }
      addEventListener(_name: string, callback: typeof listener) {
        listener = callback;
      }
      close = close;
    },
  );
  const stop = attachDesktopTask("synthetic", snapshot, connection);
  const emit = (revision: number, state = "running", id = "synthetic") =>
    listener({
      data: JSON.stringify({
        type: "assistant.snapshot",
        task: { id, revision, state } as DesktopTask,
      }),
    });
  return {
    emit,
    paint: () => paint(0),
    stop,
    close,
    cancel,
    snapshot,
    connection,
    source,
  };
}

it("batches task snapshots per frame and ignores out-of-order/replayed revisions", () => {
  const h = harness();
  h.emit(2);
  h.emit(1);
  h.emit(3);
  expect(requestAnimationFrame).toHaveBeenCalledOnce();
  expect(h.snapshot).not.toHaveBeenCalled();
  h.paint();
  expect(h.snapshot).toHaveBeenCalledExactlyOnceWith({
    id: "synthetic",
    revision: 3,
    state: "running",
  });
  h.emit(3);
  h.emit(2);
  expect(requestAnimationFrame).toHaveBeenCalledOnce();
});

it("pauses for approval without closing the stream; flushes a terminal snapshot and closes", () => {
  const h = harness();
  h.emit(1, "awaiting_approval");
  h.paint();
  expect(h.close).not.toHaveBeenCalled();
  h.emit(2, "outcome_unknown");
  h.paint();
  expect(h.close).toHaveBeenCalledOnce();
  expect(h.snapshot).toHaveBeenLastCalledWith(
    expect.objectContaining({ state: "outcome_unknown" }),
  );
});

it("closes and discards pending paint on unmount, without cancelling a durable task", () => {
  const h = harness();
  h.emit(1);
  h.stop();
  h.paint();
  expect(h.close).toHaveBeenCalledOnce();
  expect(h.cancel).toHaveBeenCalledWith(42);
  expect(h.snapshot).not.toHaveBeenCalled();
});

it("reports reconnect status and ignores a snapshot from another task", () => {
  const h = harness();
  h.source.onerror?.();
  h.source.onopen?.();
  expect(h.connection.mock.calls).toEqual([[true], [false]]);
  h.emit(99, "complete", "other-task");
  expect(requestAnimationFrame).not.toHaveBeenCalled();
  expect(h.close).not.toHaveBeenCalled();
});

import { beforeEach, expect, it } from "vitest";
import {
  beginDraftSend,
  drafts,
  editDraft,
  finishDraftSend,
  subscribeDraft,
  writeDraft,
} from "./composer-drafts";

beforeEach(() => drafts.clear());

it("restores a rejected source draft after unmount without changing a new chat", () => {
  writeDraft("source", "Original source");
  const send = beginDraftSend("source", "Original source", true);
  writeDraft("new", "Another chat");
  finishDraftSend(send, false);
  expect(drafts.get("source")).toBe("Original source");
  expect(drafts.get("new")).toBe("Another chat");
});

it.each(["A newer draft", ""])(
  "preserves an intentional newer edit: %s",
  (text) => {
    writeDraft("source", "Original source");
    const send = beginDraftSend("source", "Original source", true);
    editDraft("source");
    writeDraft("source", text);
    finishDraftSend(send, false);
    expect(drafts.get("source")).toBe(text);
  },
);

it("publishes a late rollback to a remounted composer and unsubscribes cleanly", () => {
  writeDraft("source", "Original");
  const send = beginDraftSend("source", "Original", true);
  const changes: string[] = [];
  const unsubscribe = subscribeDraft("source", () =>
    changes.push(drafts.get("source") ?? ""),
  );
  finishDraftSend(send, false);
  unsubscribe();
  writeDraft("source", "After unsubscribe");
  expect(changes).toEqual(["Original"]);
});

it("an older result cannot overwrite a newer submission of the same draft", () => {
  writeDraft("source", "Original");
  const first = beginDraftSend("source", "Original", true);
  writeDraft("source", "New submission");
  const second = beginDraftSend("source", "New submission", false);
  finishDraftSend(first, false);
  expect(drafts.get("source")).toBe("New submission");
  finishDraftSend(second, true);
  expect(drafts.has("source")).toBe(false);
});

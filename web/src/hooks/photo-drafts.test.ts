import { beforeEach, describe, expect, it } from "vitest";
import {
  clearPhotoInputs,
  photoSubmission,
  usePhotoDrafts,
  type PhotoDraft,
} from "./usePhotoEdit";

const ready = (text = "Synthetic change"): PhotoDraft => ({
  active: true,
  text,
  version: 4,
  input: {
    token: "synthetic",
    phase: "ready",
    reference: {
      id: "a".repeat(32),
      chat_id: "c".repeat(32),
      available: true,
      original_bytes: 120,
      working_bytes: 100,
      width: 80,
      height: 100,
      original_format: "PNG",
      created_at: "2026-10-20T12:00:00Z",
    },
  },
});
beforeEach(() => usePhotoDrafts.setState({ entries: {} }));
describe("photo draft ownership across asynchronous acceptance", () => {
  it("clears the exact accepted draft while retaining the editing tool", () => {
    usePhotoDrafts.setState({ entries: { one: ready() } });
    photoSubmission("one")!.accepted("one", false);
    expect(usePhotoDrafts.getState().entries.one).toMatchObject({
      active: true,
      text: "",
      input: undefined,
    });
  });
  it("moves a newer new-chat instruction intact and never changes another chat", () => {
    usePhotoDrafts.setState({
      entries: { new: ready(), other: ready("Other draft") },
    });
    const send = photoSubmission("new")!;
    usePhotoDrafts.setState((s) => ({
      entries: {
        ...s.entries,
        new: { ...s.entries.new, version: 5, text: "Newer instruction" },
      },
    }));
    send.accepted("accepted-chat", true);
    const entries = usePhotoDrafts.getState().entries;
    expect(entries.new).toBeUndefined();
    expect(entries["accepted-chat"]).toMatchObject({
      text: "Newer instruction",
      input: { reference: send.reference },
    });
    expect(entries.other.text).toBe("Other draft");
  });
  it("keeps a replacement photo when an earlier send is accepted", () => {
    usePhotoDrafts.setState({ entries: { one: ready() } });
    const send = photoSubmission("one")!;
    const replacement = ready("Different photo instruction");
    replacement.version++;
    replacement.input!.reference!.id = "b".repeat(32);
    usePhotoDrafts.setState({ entries: { one: replacement } });
    send.accepted("one", false);
    expect(usePhotoDrafts.getState().entries.one).toEqual(replacement);
  });
  it("a rejected transport preserves a retry; an unavailable reference is explained on its owner", () => {
    usePhotoDrafts.setState({
      entries: { one: ready(), other: ready("Other") },
    });
    const send = photoSubmission("one")!;
    send.rejected("http_error");
    expect(photoSubmission("one")).toBeDefined();
    send.rejected("reference_unavailable");
    expect(photoSubmission("one")).toBeUndefined();
    expect(usePhotoDrafts.getState().entries.one.text).toBe("Synthetic change");
    expect(usePhotoDrafts.getState().entries.other.input?.phase).toBe("ready");
  });
  it("bulk input clearing invalidates references while retaining instructions", () => {
    usePhotoDrafts.setState({
      entries: { one: ready(), two: ready("Retained") },
    });
    clearPhotoInputs();
    expect(usePhotoDrafts.getState().entries.two.text).toBe("Retained");
    expect(usePhotoDrafts.getState().entries.one.input).toMatchObject({
      phase: "unavailable",
      reference: { available: false },
    });
    expect(photoSubmission("one")).toBeUndefined();
  });
  it("an old rejection cannot invalidate a reattached upload with the same reference ID", () => {
    usePhotoDrafts.setState({ entries: { one: ready() } });
    const old = photoSubmission("one")!;
    const newer = ready();
    newer.version++;
    newer.input!.token = "replacement-upload";
    usePhotoDrafts.setState({ entries: { one: newer } });
    old.rejected("reference_unavailable");
    expect(photoSubmission("one")).toBeDefined();
  });
});

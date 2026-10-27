import { describe, expect, it } from "vitest";
import type { Chat, Message, Model } from "./api";
import type { ImageJob } from "./image-events";
import {
  followupImage,
  modelLabel,
  replyState,
  thinkingLabel,
  recentChats,
} from "./chat-presentation";
import { modelRows } from "./model-groups";
const base: Message = {
  id: "a",
  chat_id: "c",
  role: "assistant",
  status: "complete",
  content: "",
  created_at: "2026-10-25",
};
const job: ImageJob = {
  id: "a".repeat(32),
  prompt: "Synthetic image",
  seed: 1,
  state: "complete",
  mode: "generate",
  stage: "Done",
  completed_steps: 4,
  steps: 4,
  created_at: "2026-10-25",
  updated_at: "2026-10-25",
  image_bytes: 100,
  metadata_bytes: 0,
  export_bytes: 0,
};
describe("truthful chat presentation", () => {
  it("honors user names, limits aliases to the reviewed exact tag and never guesses unknown names", () => {
    const model = {
      model_id: "qwen3.8:27b-atelier-eval-32k",
      display_name: "qwen3.8:27b-atelier-eval-32k",
    };
    expect(modelLabel(model)).toBe("Qwen 3.8 27B · Atelier eval · 32K");
    expect(modelLabel({ ...model, display_name: "My own model" })).toBe(
      "My own model",
    );
    expect(
      modelLabel({ model_id: "qwen-anything", display_name: "qwen-anything" }),
    ).toBe("qwen-anything");
    expect(thinkingLabel("xhigh")).toBe("Max");
  });
  it("shows stopped and empty outcomes without classifying reasoning as an answer", () => {
    expect(replyState({ ...base, status: "stopped", content: "I'd" })).toBe(
      "Stopped",
    );
    expect(replyState({ ...base, reasoning: "A thought", content: "  " })).toBe(
      "No answer",
    );
    expect(replyState({ ...base, status: "streaming" })).toBeUndefined();
    expect(replyState({ ...base, kind: "image" })).toBeUndefined();
    expect(replyState({ ...base, content: "Answer" })).toBeUndefined();
  });
  it("uses only the last visible image reply, with available output and no active batch", () => {
    const image = { ...base, kind: "image" as const, images: [job] };
    expect(followupImage([image])).toEqual(job);
    expect(
      followupImage([image, { ...base, id: "b", content: "Text after image" }]),
    ).toBeUndefined();
    expect(
      followupImage([{ ...image, images: [{ ...job, image_bytes: 0 }] }]),
    ).toBeUndefined();
    expect(
      followupImage([
        { ...image, images: [job, { ...job, state: "running" }] },
      ]),
    ).toBeUndefined();
    expect(followupImage([{ ...image, role: "user" }])).toBeUndefined();
  });
});
describe("runtime family grouping", () => {
  const model: Model = {
    connection_id: "fake",
    model_id: "one",
    display_name: "First",
    family: "runtime-family",
    loaded: false,
    vision: false,
    reasoning: null,
    tools: false,
    chat_capable: true,
    hidden: false,
    embedding: false,
  };
  const second: Model = {
    ...model,
    model_id: "two",
    display_name: "Second",
    vision: true,
    loaded: true,
  };
  it("selects the current variant and retains its own capabilities", () => {
    const rows = modelRows([model, second], model);
    expect(rows).toHaveLength(1);
    expect(rows[0]).toMatchObject({ model, count: 2 });
    expect(rows[0].model.vision).toBe(false);
    const expanded = modelRows([model, second], model, [rows[0].key]);
    expect(expanded.map((row) => row.model.vision)).toEqual([false, true]);
  });
  it("keeps distinct connections and unknown families separate, and makes every variant searchable", () => {
    expect(
      modelRows([model, { ...second, connection_id: "other" }]),
    ).toHaveLength(2);
    expect(
      modelRows([
        { ...model, family: null },
        { ...second, family: null },
      ]),
    ).toHaveLength(2);
    expect(modelRows([model, second], model, [], true)).toHaveLength(2);
  });
});

it("recent starters ignore pinned-first ordering and exclude empty chats", () => {
  const chat: Chat = {
    id: "old-pinned",
    title: "Synthetic old pinned chat",
    title_source: "user",
    pinned: true,
    current_leaf_id: "reply",
    created_at: "2020-01-01",
    updated_at: "2020-01-01",
    params: {},
    web_enabled: false,
    library_enabled: false,
  };
  const newest = {
    ...chat,
    id: "newest",
    pinned: false,
    updated_at: "2026-10-26",
  };
  const second = {
    ...chat,
    id: "second",
    pinned: false,
    updated_at: "2026-10-25",
  };
  const empty = {
    ...newest,
    id: "empty",
    current_leaf_id: null,
    updated_at: "2026-10-27",
  };
  expect(
    recentChats([chat, empty, second, newest]).map((row) => row.id),
  ).toEqual(["newest", "second"]);
});

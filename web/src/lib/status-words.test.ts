import { expect, it } from "vitest";
import {
  STATUS_WORDS,
  statusSequence,
  thoughtTail,
  workingPhase,
} from "./status-words";
import type { Message } from "./api";

const message = {
  status: "streaming",
  content: "",
  reasoning: "",
  model: { model_id: "synthetic-model" },
} as Message;
it("seeds all 36 words without repeats, with reconnect-stable ordering", () => {
  const words = statusSequence("synthetic-a");
  expect(words).toHaveLength(36);
  expect(new Set(words)).toEqual(new Set(STATUS_WORDS));
  expect(words).toEqual(statusSequence("synthetic-a"));
  expect(words).not.toEqual(statusSequence("synthetic-b"));
});
it("uses known stages before reasoning or cosmetic waiting", () => {
  const reasoning = { ...message, reasoning: "Synthetic thought" };
  expect(workingPhase(reasoning, "queued", [], 2)).toMatchObject({
    kind: "queued",
    label: "Waiting for synthetic-model · #2 in line",
    announcement: "Waiting for synthetic-model",
  });
  expect(workingPhase(reasoning, "loading-model")?.kind).toBe("loading");
  expect(workingPhase(reasoning, "search")?.kind).toBe("search");
  expect(workingPhase(reasoning, "reasoning")?.kind).toBe("thinking");
  expect(workingPhase(message)?.kind).toBe("working");
});
it("counts actual unique active pages and distinguishes library search", () => {
  const steps = ["a", "a", "b", "c", "d"].map((detail) => ({
    label: "reading",
    detail,
    status: "ok",
  }));
  expect(workingPhase(message, "search", steps)?.label).toBe("Reading 4 pages");
  steps.push({ label: "read", detail: "a", status: "ok" });
  expect(workingPhase(message, "search", steps)?.label).toBe("Reading 3 pages");
  steps.push(
    ...["b", "c", "d"].map((detail) => ({
      label: "read",
      detail,
      status: "ok",
    })),
  );
  expect(workingPhase(message, "search", steps)?.label).toBe("Read 4 pages");
  expect(
    workingPhase(
      { ...message, library: {} as Message["library"] },
      "search",
      steps,
    )?.label,
  ).toBe("Searching your files");
});
it("hides activity on the first answer token and every terminal state", () => {
  expect(workingPhase({ ...message, content: "A" }, "queued")).toBeNull();
  for (const status of ["complete", "stopped", "error", "interrupted"] as const)
    expect(workingPhase({ ...message, status }, "search")).toBeNull();
});
it("returns only the literal reasoning suffix, compacted and bounded", () => {
  const text =
    "Earlier reasoning. ".repeat(40) + "Newest line\nwith   original words.   ";
  const tail = thoughtTail(text);
  expect(tail.length).toBeLessThanOrEqual(160);
  expect(text.replace(/\s+/g, " ").trim().endsWith(tail)).toBe(true);
  expect(tail).toMatch(/Newest line with original words\.$/);
  expect(thoughtTail("<script>literal</script>\n& text")).toBe(
    "<script>literal</script> & text",
  );
  expect(thoughtTail("")).toBe("");
});

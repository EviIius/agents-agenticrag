import { it, expect } from "vitest";
import type { Message } from "./api";
import { visiblePath, siblings, latestLeaf } from "./tree";
const message = (
  id: string,
  parent: string | null,
  date = id,
  role: "user" | "assistant" = "assistant",
) =>
  ({
    id,
    parent_id: parent,
    created_at: date,
    role,
    content: "",
    chat_id: "c",
    status: "complete",
  }) as Message;
it("branches preserve the chosen path and latest descendant", () => {
  const all = [
    message("u", null, "1", "user"),
    message("a", "u", "2"),
    message("b", "u", "3"),
    message("u2", "a", "4", "user"),
    message("a2", "u2", "5"),
  ];
  expect(visiblePath(all, "a2").map((m) => m.id)).toEqual([
    "u",
    "a",
    "u2",
    "a2",
  ]);
  expect(siblings(all, all[1]!).map((m) => m.id)).toEqual(["a", "b"]);
  expect(latestLeaf(all, "a")).toBe("a2");
  expect(latestLeaf(all, "b")).toBe("b");
});
it("tree walks stop on cycles and missing parents", () => {
  expect(visiblePath([message("a", "b"), message("b", "a")], "a")).toHaveLength(
    2,
  );
  expect(latestLeaf([message("a", "b"), message("b", "a")], "a")).toBe("a");
  expect(visiblePath([], "missing")).toEqual([]);
});

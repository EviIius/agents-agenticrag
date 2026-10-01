import { describe, it, expect } from "vitest";
import vectors from "../../../shared/citation_cases.json";
import { normalize, renderCitations, bestPassage } from "./citations";
import type { Source } from "./api";
describe("citation normalization", () => {
  for (const v of vectors)
    it(v.in, () => expect(normalize(v.in, v.n)).toBe(v.out));
});
it("groups citations but preserves code and links", () =>
  expect(renderCitations("Yes [1][2] `x[9]` [1](https://a.b)", 2)).toBe(
    "Yes [cite](#cite-1-2) `x[9]` [1](https://a.b)",
  ));
it("picks a sentence-matching passage, ties first, and bounds the preview", () => {
  const s = {
    passages: [
      { text: "Tokyo has many museums." },
      { text: "Paris is the capital of France." },
    ],
  } as Source;
  expect(bestPassage(s, "French capital Paris")).toContain("Paris");
  expect(bestPassage(s, "zzz")).toContain("Tokyo");
  expect(
    bestPassage({ passages: [{ text: "a".repeat(500) }] } as Source, ""),
  ).toHaveLength(280);
});

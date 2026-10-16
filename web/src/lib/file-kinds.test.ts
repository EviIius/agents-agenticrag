import { describe, expect, it } from "vitest";
import {
  fileAccept,
  fileKind,
  fileLimit,
  fileTone,
  splitFilename,
} from "./file-kinds";
const extensions = {
  text: [".txt", ".csv", ".json"],
  document: [".pdf", ".docx"],
};
describe("attachment classification and native accept list", () => {
  for (const [name, mime, expected] of [
    ["Photo-fake.PNG", "", "image"],
    ["Photo-fake.heic", "", "image"],
    ["Odd-name-fake.bin", "image/jpeg", "image"],
    ["Notes-fake.PDF", "", "document"],
    ["Notes-fake.docx", "", "document"],
    ["Notes-fake.txt", "", "text"],
    ["Prices-fake.csv", "", "text"],
    ["Recording-fake.m4a", "", "audio"],
    ["Archive-fake.zip", "application/zip", "unsupported"],
  ])
    it(`classifies ${name}`, () =>
      expect(
        fileKind(new File(["fake"], name, { type: mime }), extensions, [
          ".m4a",
        ]),
      ).toBe(expected));
  it("includes all accepted types, and audio only when enabled", () => {
    expect(fileAccept(extensions, [".m4a"], false)).toBe(
      "image/*,.heic,.heif,.pdf,.docx,.txt,.csv,.json",
    );
    expect(fileAccept(extensions, [".m4a"], true)).toContain(",.m4a");
  });
  it("preserves every character in the adaptive middle ellipsis", () => {
    for (const name of [
      "Plan-fake-2026.pdf",
      "A very long fake document [final].docx",
      "fake.txt",
      "README",
    ])
      expect(splitFilename(name).join("")).toBe(name);
    expect(splitFilename("Plan-fake-2026.pdf")[1]).toBe("-2026.pdf");
  });
  it("keeps the published limits and category tones", () => {
    expect(fileLimit("image").bytes).toBe(20 * 1024 ** 2);
    expect(fileLimit("text").bytes).toBe(512 * 1024);
    expect(fileLimit("document").bytes).toBe(50 * 1024 ** 2);
    expect(fileLimit("audio").bytes).toBe(4 * 1024 ** 3);
    expect(fileTone("Plan-fake.pdf")).toBe("review");
    expect(fileTone("Notes-fake.docx")).toBe("ai");
    expect(fileTone("Data-fake.csv")).toBe("knowledge");
  });
});

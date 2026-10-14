import { it, expect } from "vitest";
import { renderPreview } from "./preview";

it("previews literal values without recursively interpreting them or adding messages", () => {
  expect(
    renderPreview("Use {{start.text}}", { start: { text: "{{secret.text}}" } }),
  ).toBe("Use {{secret.text}}");
  expect(renderPreview("\\{{start.text}}", {})).toBe("{{start.text}}");
  expect(() => renderPreview("{{missing.text}}", {})).toThrow(
    "Run once or set an input default",
  );
});
it("escapes only tagged values and drops empty tagged lines with host-compatible spacing", () => {
  expect(
    renderPreview("{{start.text | tagged:source}}", {
      start: { text: '<b>"x" & y</b>' },
    }),
  ).toBe("<source>\n&lt;b&gt;&quot;x&quot; &amp; y&lt;/b&gt;\n</source>");
  expect(
    renderPreview("Heading\n{{start.text | tagged:source}}\nEnd", {
      start: { text: "" },
    }),
  ).toBe("Heading\nEnd");
  expect(renderPreview("{{start.text}}", {}, new Set(["start"]))).toBe("");
});

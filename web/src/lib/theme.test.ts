import { describe, expect, it } from "vitest";
import { resolvedTheme } from "./theme";
describe("Theme preference", () => {
  it("tracks OS changes only when System is selected", () => {
    expect(resolvedTheme("system", true)).toBe("dark");
    expect(resolvedTheme("system", false)).toBe("light");
    expect(resolvedTheme("light", true)).toBe("light");
    expect(resolvedTheme("dark", false)).toBe("dark");
  });
});

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

describe("Overlapping appearance changes", () => {
  let root: {
    dataset: Record<string, string>;
    style: { setProperty: ReturnType<typeof vi.fn> };
  };
  let pending: {
    update: () => void;
    finish: () => void;
    skipTransition: ReturnType<typeof vi.fn>;
  }[];
  beforeEach(() => {
    vi.resetModules();
    root = {
      dataset: { palette: "cobalt", theme: "light" },
      style: { setProperty: vi.fn() },
    };
    pending = [];
    vi.stubGlobal("innerWidth", 390);
    vi.stubGlobal("innerHeight", 844);
    vi.stubGlobal("getComputedStyle", () => ({
      getPropertyValue: () => "#ffffff",
    }));
    vi.stubGlobal("document", {
      documentElement: root,
      querySelectorAll: () => [],
      startViewTransition: (update: () => void) => {
        let finish!: () => void;
        const finished = new Promise<void>((resolve) => {
          finish = resolve;
        });
        const skipTransition = vi.fn();
        pending.push({ update, finish, skipTransition });
        return { finished, ready: Promise.resolve(), skipTransition };
      },
    });
  });
  afterEach(() => vi.unstubAllGlobals());

  it("a delayed snapshot cannot overwrite a newer palette", async () => {
    const { applyAppearance } = await import("./appearance");
    applyAppearance({
      theme: "light",
      palette: "lime",
      systemDark: false,
      animate: true,
    });
    applyAppearance({
      theme: "light",
      palette: "ember",
      systemDark: false,
      animate: true,
    });
    pending[1].update();
    pending[0].update();
    expect(root.dataset.palette).toBe("ember");
  });

  it("an older transition cannot clear the newer circle", async () => {
    const { applyAppearance } = await import("./appearance");
    applyAppearance({
      theme: "light",
      palette: "lime",
      systemDark: false,
      animate: true,
    });
    applyAppearance({
      theme: "light",
      palette: "ember",
      systemDark: false,
      animate: true,
    });
    pending[0].finish();
    await Promise.resolve();
    await Promise.resolve();
    expect(root.dataset.themeReveal).toBe("circle");
    pending[1].finish();
    await Promise.resolve();
    await Promise.resolve();
    expect(root.dataset.themeReveal).toBeUndefined();
  });

  it("reduced motion cancels a pending snapshot and applies the latest choice", async () => {
    const { applyAppearance } = await import("./appearance");
    applyAppearance({
      theme: "light",
      palette: "lime",
      systemDark: false,
      animate: true,
    });
    applyAppearance({
      theme: "light",
      palette: "mono",
      systemDark: false,
      animate: false,
    });
    pending[0].update();
    expect(pending[0].skipTransition).toHaveBeenCalledOnce();
    expect(root.dataset.palette).toBe("mono");
    expect(root.dataset.themeReveal).toBeUndefined();
  });
});

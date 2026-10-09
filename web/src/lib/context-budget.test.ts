import { describe, expect, it } from "vitest";
import { contextBudget } from "./context-budget";
import type { Model } from "./api";

const model = { context_length: 32768, params_defaults: {} } as Model;
describe("context input allowance", () => {
  it("explains a transcript that fits the raw window but not the input allowance", () => {
    const budget = contextBudget(model);
    expect(budget).toEqual({ maximum: 32768, reserve: 8192, available: 24320 });
    expect(28509).toBeLessThan(budget.maximum);
    expect(26861).toBeGreaterThan(budget.available);
  });
  it("uses the user's output override before their saved model default", () => {
    const saved = { ...model, params_defaults: { max_tokens: 4096 } };
    expect(contextBudget(saved).available).toBe(28416);
    expect(contextBudget(saved, 3072).available).toBe(29440);
    expect(28509).toBeLessThan(contextBudget(saved, 3072).available);
    expect(saved.params_defaults).toEqual({ max_tokens: 4096 });
  });
  it("retains the default clamps and never reports negative input space", () => {
    expect(contextBudget({ ...model, context_length: 2048 }).reserve).toBe(
      1024,
    );
    expect(contextBudget({ ...model, context_length: 131072 }).reserve).toBe(
      8192,
    );
    expect(contextBudget(model, 40000).available).toBe(0);
  });
});

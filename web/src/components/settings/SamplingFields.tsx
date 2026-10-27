import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import type { Params } from "@/lib/api";
export const samplingControls = [
  ["temperature", "Temperature", 0, 2, 0.05],
  ["top_p", "Top P", 0, 1, 0.05],
  ["top_k", "Top K", 1, 200, 1],
  ["max_tokens", "Max output tokens", 1, 32768, 1],
  ["seed", "Seed", -Number.MAX_SAFE_INTEGER, Number.MAX_SAFE_INTEGER, 1],
] as const;
export type SamplingKey = (typeof samplingControls)[number][0];
export type SamplingDraft = Partial<Record<SamplingKey, string>>;
export function samplingDraft(params: Params): SamplingDraft {
  return Object.fromEntries(
    samplingControls.flatMap(([key]) =>
      params[key] == null ? [] : [[key, String(params[key])]],
    ),
  );
}
export function samplingError(key: SamplingKey, value?: string) {
  if (value === undefined) return "";
  const control = samplingControls.find(([k]) => k === key)!;
  const n = Number(value);
  if (!value.trim() || !Number.isFinite(n)) return "Enter a number.";
  if (control[4] === 1 && !Number.isSafeInteger(n))
    return "Enter a whole number.";
  if (n < control[2] || n > control[3])
    return key === "seed"
      ? "Enter a safe whole number."
      : `Choose a value from ${control[2]} to ${control[3]}.`;
  return "";
}
export function samplingValid(values: SamplingDraft) {
  return samplingControls.every(([key]) => !samplingError(key, values[key]));
}
export function samplingParams(values: SamplingDraft): Params {
  return Object.fromEntries(
    Object.entries(values).map(([key, value]) => [key, Number(value)]),
  );
}
export function SamplingFields({
  values,
  onChange,
  prefix = "sampling",
  labelPrefix = "",
}: {
  values: SamplingDraft;
  onChange: (values: SamplingDraft) => void;
  prefix?: string;
  labelPrefix?: string;
}) {
  return samplingControls.map(([key, name, min, max, step]) => {
    const label = labelPrefix + name;
    const value = values[key],
      error = samplingError(key, value),
      id = `${prefix}-${key}-error`;
    const change = (value?: string) => {
      const next = { ...values };
      if (value === undefined) delete next[key];
      else next[key] = value;
      onChange(next);
    };
    return (
      <fieldset key={key} className="mb-5">
        <legend className="flex w-full justify-between gap-2 text-sm font-medium">
          <span>{label}</span>
          <span className="font-normal text-fg-2">
            {value === undefined ? "Model default" : value}
          </span>
        </legend>
        <label className="my-2 flex min-h-11 items-center gap-2 text-xs text-fg-2">
          <Switch
            aria-label={`Use model default for ${label}`}
            checked={value === undefined}
            onCheckedChange={(checked) =>
              change(checked ? undefined : String(key === "seed" ? 0 : min))
            }
          />
          <span className="sr-only">Use model default</span>
        </label>
        {value !== undefined && (
          <>
            {key !== "seed" && (
              <Slider
                className="my-4"
                aria-label={`${label} slider`}
                min={min}
                max={max}
                step={step}
                value={[error ? min : Number(value)]}
                onValueChange={([n]) => change(String(n))}
              />
            )}
            <Input
              type="number"
              aria-label={label}
              min={min}
              max={max}
              step={step}
              value={value}
              aria-invalid={!!error}
              aria-describedby={error ? id : undefined}
              onChange={(e) => change(e.target.value)}
            />
            {error && (
              <p id={id} className="mt-2 text-xs text-danger">
                {error}
              </p>
            )}
          </>
        )}
      </fieldset>
    );
  });
}

import { useState } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { IconButton } from "@/components/app/IconButton";
import type { Chat, Model, Params } from "@/lib/api";
import { useUI } from "@/stores/ui";
const controls = [
  ["temperature", "Temperature", 0, 2, 0.05],
  ["top_p", "Top P", 0, 1, 0.05],
  ["top_k", "Top K", 1, 200, 1],
  ["max_tokens", "Max output tokens", 64, 32768, 1],
  ["seed", "Seed", 0, 2147483647, 1],
] as const;
export function LiveChatSettings({
  chat,
  model,
  onSave,
  onDefaults,
  onContext,
  draftParams,
  draftPrompt,
  defaultsOnly = false,
  drawer = false,
}: {
  chat?: Chat;
  model?: Model;
  onSave: (prompt: string | null, params: Params) => void;
  onDefaults: (params: Params) => void;
  onContext: (context: number) => void;
  defaultsOnly?: boolean;
  drawer?: boolean;
  draftParams?: Params;
  draftPrompt?: string | null;
}) {
  const [params, setParams] = useState<Params>(
      defaultsOnly
        ? (model?.params_defaults ?? {})
        : (chat?.params ?? draftParams ?? {}),
    ),
    [prompt, setPrompt] = useState(chat?.system_prompt ?? draftPrompt ?? ""),
    [useDefault, setDefault] = useState(
      (chat?.system_prompt ?? draftPrompt) == null,
    ),
    [context, setContext] = useState(model?.context_length ?? 8192);
  const limit = model?.context_limit ?? model?.context_max;
  const validContext =
    Number.isInteger(context) &&
    context >= 1024 &&
    (!limit || context <= limit);
  return (
    <section className="p-5" aria-label="Chat settings controls">
      {!drawer && (
        <header className="sticky top-0 z-10 -mx-5 -mt-5 mb-6 flex items-center justify-between bg-surface px-5 py-3">
          <h2 className="font-medium">
            {defaultsOnly ? "Model defaults" : "Chat settings"}
          </h2>
          {!defaultsOnly && (
            <IconButton
              label="Close chat settings"
              onClick={() => useUI.getState().set({ panel: false })}
            >
              <X />
            </IconButton>
          )}
        </header>
      )}
      <p className="mb-3 text-xs text-fg-2" aria-label="Settings model">
        {model?.display_name ?? "Choose a model"}
      </p>
      {!defaultsOnly && (
        <>
          <label className="mb-3 flex min-h-11 items-center gap-2 text-sm">
            <Switch
              aria-label="Use default system prompt"
              checked={useDefault}
              onCheckedChange={setDefault}
            />
            Use default system prompt
          </label>
          <Textarea
            aria-label="System prompt"
            disabled={useDefault}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="mb-6 min-h-28"
          />
        </>
      )}
      {controls.map(([key, label, min, max, step]) => (
        <fieldset key={key} className="mb-5">
          <legend className="text-sm font-medium">{label}</legend>
          <label className="my-2 flex min-h-11 items-center gap-2 text-xs text-fg-2">
            <Switch
              aria-label={`Use model default for ${label}`}
              checked={params[key] == null}
              onCheckedChange={(checked) =>
                setParams((p) => ({
                  ...p,
                  [key]: checked ? null : min,
                }))
              }
            />
            Model default
          </label>
          {key !== "seed" && params[key] != null && (
            <Slider
              className="my-4"
              aria-label={`${label} slider`}
              min={min}
              max={max}
              step={step}
              value={[params[key]]}
              onValueChange={([value]) =>
                setParams((previous) => ({ ...previous, [key]: value }))
              }
            />
          )}
          <Input
            type="number"
            aria-label={label}
            min={min}
            max={max}
            step={step}
            disabled={params[key] == null}
            value={params[key] ?? ""}
            onChange={(e) =>
              setParams((p) => ({ ...p, [key]: Number(e.target.value) }))
            }
          />
        </fieldset>
      ))}
      {model?.reasoning && (
        <label className="mb-5 block text-sm">
          Reasoning
          <Select
            value={params.reasoning ?? "default"}
            onValueChange={(value) =>
              setParams((p) => ({
                ...p,
                reasoning: value === "default" ? null : value,
              }))
            }
          >
            <SelectTrigger aria-label="Reasoning">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="default">Model default</SelectItem>
              {model.reasoning.options.map((value) => (
                <SelectItem key={value} value={value}>
                  {value[0].toUpperCase() + value.slice(1)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </label>
      )}
      <label className="mb-5 block text-sm">
        Context length
        <Input
          aria-label="Context length"
          type="number"
          min={1024}
          max={limit ?? undefined}
          aria-invalid={!validContext}
          aria-describedby="context-limit"
          value={context}
          onChange={(e) => setContext(Number(e.target.value))}
        />
      </label>
      <p
        id="context-limit"
        className={`mb-3 text-xs ${validContext ? "text-fg-3" : "text-danger"}`}
      >
        {limit
          ? `Configured limit: ${limit / 1024}K tokens.`
          : "Minimum: 1K tokens."}
        {!validContext && " Choose a context within this limit."}
      </p>
      <div className="mb-4 flex flex-wrap gap-1">
        {[4096, 8192, 16384, 32768, 65536]
          .filter((n) => !limit || n <= limit)
          .map((n) => (
            <Button
              key={n}
              variant="outline"
              size="sm"
              aria-pressed={context === n}
              onClick={() => setContext(n)}
            >
              {n / 1024}K
            </Button>
          ))}
      </div>
      <div className="flex flex-col gap-2">
        {!defaultsOnly && (
          <Button
            disabled={!model || !validContext}
            onClick={() => {
              onSave(useDefault ? null : prompt, params);
              onContext(context);
            }}
          >
            Save settings
          </Button>
        )}
        <Button
          variant="outline"
          disabled={!model || !validContext}
          onClick={() => {
            setParams({});
            setContext(model?.context_length ?? 8192);
            onSave(useDefault ? null : prompt, {});
          }}
        >
          Reset to model defaults
        </Button>
        <Button
          variant="ghost"
          disabled={!model || !validContext}
          onClick={() => {
            onDefaults(params);
            if (defaultsOnly) onContext(context);
          }}
        >
          Save as model defaults
        </Button>
      </div>
    </section>
  );
}

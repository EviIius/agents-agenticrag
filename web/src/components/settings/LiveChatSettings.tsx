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
  defaultsOnly = false,
}: {
  chat?: Chat;
  model?: Model;
  onSave: (prompt: string | null, params: Params) => void;
  onDefaults: (params: Params) => void;
  onContext: (context: number) => void;
  defaultsOnly?: boolean;
}) {
  const [params, setParams] = useState<Params>(
      defaultsOnly ? (model?.params_defaults ?? {}) : (chat?.params ?? {}),
    ),
    [prompt, setPrompt] = useState(chat?.system_prompt ?? ""),
    [useDefault, setDefault] = useState(chat?.system_prompt == null),
    [context, setContext] = useState(model?.context_length ?? 8192);
  return (
    <section className="p-5" aria-label="Chat settings controls">
      <header className="mb-6 flex items-center justify-between">
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
                  {value}
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
          max={model?.context_max ?? undefined}
          value={context}
          onChange={(e) => setContext(Number(e.target.value))}
        />
      </label>
      <div className="mb-4 flex flex-wrap gap-1">
        {[4096, 8192, 16384, 32768, 65536]
          .filter((n) => !model?.context_max || n <= model.context_max)
          .map((n) => (
            <Button
              key={n}
              variant="outline"
              size="sm"
              onClick={() => setContext(n)}
            >
              {n / 1024}K
            </Button>
          ))}
      </div>
      <div className="flex flex-col gap-2">
        {!defaultsOnly && (
          <Button
            disabled={!model}
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
          disabled={!model}
          onClick={() => {
            setParams({});
            onSave(useDefault ? null : prompt, {});
          }}
        >
          Reset to model defaults
        </Button>
        <Button
          variant="ghost"
          disabled={!model}
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

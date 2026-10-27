import { lazy, Suspense, useEffect, useId, useRef, useState } from "react";
import { Check, X } from "lucide-react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectSeparator,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { IconButton } from "@/components/app/IconButton";
import {
  api,
  type Chat,
  type Model,
  type Params,
  type Preset,
} from "@/lib/api";
import { modelLabel } from "@/lib/chat-presentation";
import { useUI } from "@/stores/ui";
import {
  controlsKey,
  useControlDrafts,
  type ControlDraft,
} from "@/stores/control-drafts";
import {
  SamplingFields,
  samplingDraft,
  samplingParams,
  samplingValid,
} from "./SamplingFields";
const PresetEditor = lazy(() => import("./PresetEditor"));
type SaveResult = unknown;
const signature = (d: ControlDraft) =>
  JSON.stringify([d.values, d.useDefault ? null : d.prompt, d.reasoning]);
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
  request = api,
  queryScope = [],
  initialPreset = "none",
  imageOnly = false,
}: {
  chat?: Chat;
  model?: Model;
  onSave: (prompt: string | null, params: Params) => SaveResult;
  onDefaults: (params: Params) => SaveResult;
  onContext: (context: number) => SaveResult;
  draftParams?: Params;
  draftPrompt?: string | null;
  defaultsOnly?: boolean;
  drawer?: boolean;
  request?: typeof api;
  queryScope?: string[];
  initialPreset?: string;
  imageOnly?: boolean;
}) {
  const contextId = useId();
  const key = controlsKey(
      chat?.id,
      model?.connection_id,
      model?.model_id,
      defaultsOnly,
    ),
    query = useQueryClient();
  const initialParams = defaultsOnly
    ? (model?.params_defaults ?? {})
    : (chat?.params ?? draftParams ?? {});
  const initialPrompt = chat?.system_prompt ?? draftPrompt;
  const initial: ControlDraft = {
    values: samplingDraft(initialParams),
    defaultValues: samplingDraft(model?.params_defaults ?? {}),
    prompt: initialPrompt ?? "",
    useDefault: initialPrompt == null,
    reasoning:
      typeof initialParams.reasoning === "string"
        ? initialParams.reasoning
        : "default",
    context: String(model?.context_length ?? 8192),
    preset: initialPreset,
  };
  const kept = useControlDrafts.getState().drafts[key];
  const sourceReasoning =
    typeof initialParams.reasoning === "string"
      ? initialParams.reasoning
      : "default";
  const restored =
    kept && kept.sourceReasoning !== sourceReasoning
      ? {
          ...kept,
          draft: { ...kept.draft, reasoning: sourceReasoning },
          baseline: JSON.stringify([
            ...(JSON.parse(kept.baseline) as unknown[]).slice(0, 2),
            sourceReasoning,
          ]),
        }
      : kept;
  const [draft, setDraft] = useState(restored?.draft ?? initial),
    [baseline, setBaseline] = useState(
      restored?.baseline ?? signature(initial),
    ),
    [contextBaseline, setContextBaseline] = useState(
      kept?.contextBaseline ?? initial.context,
    ),
    [saved, setSaved] = useState(false),
    [busy, setBusy] = useState(false),
    [defaultsBaseline, setDefaultsBaseline] = useState(
      kept?.defaultsBaseline ?? JSON.stringify(initial.defaultValues),
    ),
    [editor, setEditor] = useState(false),
    [presetOpen, setPresetOpen] = useState(false);
  const externalReasoning =
    typeof initialParams.reasoning === "string"
      ? initialParams.reasoning
      : "default";
  const previousReasoning = useRef(externalReasoning);
  useEffect(() => {
    if (externalReasoning === previousReasoning.current) return;
    previousReasoning.current = externalReasoning;
    setDraft((old) => ({ ...old, reasoning: externalReasoning }));
    setBaseline((old) => {
      const [values, prompt] = JSON.parse(old) as [
        ControlDraft["values"],
        string | null,
      ];
      return JSON.stringify([values, prompt, externalReasoning]);
    });
  }, [externalReasoning]);
  const choosePreset = useUI((s) => s.choosePreset);
  useEffect(() => {
    if (choosePreset && !defaultsOnly) {
      setPresetOpen(true);
      useUI.getState().set({ choosePreset: false });
    }
  }, [choosePreset, defaultsOnly]);
  const chatDirty = signature(draft) !== baseline,
    defaultsDirty =
      !defaultsOnly && JSON.stringify(draft.defaultValues) !== defaultsBaseline,
    dirty = chatDirty || defaultsDirty,
    contextDirty = draft.context !== contextBaseline;
  useEffect(() => {
    useControlDrafts.getState().keep(
      key,
      dirty || contextDirty
        ? {
            draft,
            baseline,
            contextBaseline,
            defaultsBaseline,
            sourceReasoning,
          }
        : undefined,
    );
  }, [
    key,
    draft,
    baseline,
    contextBaseline,
    defaultsBaseline,
    sourceReasoning,
    dirty,
    contextDirty,
  ]);
  useEffect(() => {
    if (!saved) return;
    const timer = setTimeout(() => setSaved(false), 1500);
    return () => clearTimeout(timer);
  }, [saved]);
  const presets = useQuery({
    queryKey: ["presets", ...queryScope],
    queryFn: () => request<Preset[]>("/presets"),
    enabled: !defaultsOnly,
  });
  const change = (patch: Partial<ControlDraft>) => {
    setSaved(false);
    setDraft((d) => ({ ...d, ...patch }));
  };
  const params: Params = {
    ...samplingParams(draft.values),
    ...(draft.reasoning !== "default" ? { reasoning: draft.reasoning } : {}),
  };
  const valid = samplingValid(draft.values),
    limit = model?.context_limit ?? model?.context_max,
    context = Number(draft.context);
  const validContext =
    !!draft.context.trim() &&
    Number.isSafeInteger(context) &&
    context >= 1024 &&
    (!limit || context <= limit);
  const save = async () => {
    if (
      busy ||
      !model ||
      !valid ||
      !validContext ||
      !samplingValid(draft.defaultValues ?? {})
    )
      return;
    setBusy(true);
    try {
      if (chatDirty && !imageOnly) {
        const result = defaultsOnly
          ? await onDefaults(params)
          : await onSave(draft.useDefault ? null : draft.prompt, params);
        if (result === false) return;
        setBaseline(signature(draft));
      }
      if (defaultsDirty && !imageOnly) {
        const next = {
          ...samplingParams(draft.defaultValues ?? {}),
          ...(typeof model.params_defaults?.reasoning === "string"
            ? { reasoning: model.params_defaults?.reasoning }
            : {}),
        };
        if ((await onDefaults(next)) === false) return;
        setDefaultsBaseline(JSON.stringify(draft.defaultValues));
      }
      if (contextDirty) {
        if ((await onContext(context)) === false) return;
        setContextBaseline(draft.context);
      }
      setSaved(true);
    } finally {
      setBusy(false);
    }
  };
  useEffect(() => {
    const escape = (event: KeyboardEvent) => {
      if (
        event.key === "Escape" &&
        !event.defaultPrevented &&
        !document.querySelector(
          '[data-slot="select-content"], [data-slot="dialog-content"], [data-slot="dropdown-menu-content"]',
        )
      )
        useUI.getState().set({ panel: false });
    };
    window.addEventListener("keydown", escape);
    return () => window.removeEventListener("keydown", escape);
  }, []);
  return (
    <section className="p-5" aria-label="Chat controls">
      {!drawer && (
        <header className="sticky top-0 z-10 -mx-5 -mt-5 mb-6 flex items-center justify-between bg-surface px-5 py-3">
          <h2 className="font-medium">
            {defaultsOnly ? "Model defaults" : "Chat controls"}
          </h2>
          {!defaultsOnly && (
            <IconButton
              label="Close chat controls"
              onClick={() => useUI.getState().set({ panel: false })}
            >
              <X />
            </IconButton>
          )}
        </header>
      )}
      <fieldset disabled={busy} className="min-w-0">
        <p className="mb-3 text-xs text-fg-2" aria-label="Settings model">
          {model ? modelLabel(model) : "Choose a model"}
        </p>
        {!defaultsOnly && !imageOnly && (
          <>
            <h3 className="mb-4 text-sm font-medium">This chat</h3>
            <label className="mb-5 block text-sm">
              Preset
              <Select
                open={presetOpen}
                onOpenChange={setPresetOpen}
                value={draft.preset}
                onValueChange={(id) => {
                  if (id === "save") {
                    setEditor(true);
                    return;
                  }
                  if (id === "manage") {
                    useUI
                      .getState()
                      .set({ settings: true, settingsPane: "Presets" });
                    return;
                  }
                  const p = presets.data?.find((p) => p.id === id);
                  change({
                    preset: id,
                    reasoning:
                      typeof p?.params?.reasoning === "string"
                        ? p.params!.reasoning
                        : "default",
                    values: samplingDraft(p?.params ?? {}),
                    prompt: p?.system_prompt ?? "",
                    useDefault: p?.system_prompt == null,
                  });
                }}
              >
                <SelectTrigger aria-label="Preset">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  {presets.data?.map((p) => (
                    <SelectItem key={p.id} value={p.id}>
                      {p.name}
                    </SelectItem>
                  ))}
                  <SelectSeparator />
                  <SelectItem value="save" disabled={!valid}>
                    Save as preset…
                  </SelectItem>
                  <SelectItem value="manage">Manage presets…</SelectItem>
                </SelectContent>
              </Select>
            </label>
            {presets.isError && (
              <p role="alert" className="mb-3 text-sm text-danger">
                Couldn't load presets.{" "}
                <Button variant="ghost" onClick={() => void presets.refetch()}>
                  Retry
                </Button>
              </p>
            )}
            <h3 className="mb-3 text-sm font-medium">System prompt</h3>
            <label className="mb-3 flex min-h-11 items-center gap-2 text-sm">
              <Switch
                aria-label="Use default system prompt"
                checked={draft.useDefault}
                onCheckedChange={(useDefault) => change({ useDefault })}
              />
              Use default system prompt
            </label>
            <Textarea
              aria-label="System prompt"
              disabled={draft.useDefault}
              value={draft.prompt}
              onChange={(e) => change({ prompt: e.target.value })}
              className="mb-6 min-h-28"
            />
          </>
        )}
        {imageOnly ? (
          <p className="mb-5 text-sm text-fg-2">
            Image turns use the image engine's settings. Your text model
            settings are kept.
          </p>
        ) : (
          <>
            <h3 className="mb-4 text-sm font-medium">
              {defaultsOnly ? "Every chat with this model" : "Sampling"}
            </h3>
            <SamplingFields
              values={draft.values}
              onChange={(values) => change({ values })}
            />
            {!defaultsOnly && (
              <details className="mb-5 border-t border-line pt-4">
                <summary className="min-h-11 cursor-pointer text-sm font-medium">
                  Every chat with this model
                </summary>
                <p className="mb-4 text-xs text-fg-2">
                  Saved model defaults. Explicit chat and preset values take
                  precedence.
                </p>
                <SamplingFields
                  prefix="model-sampling"
                  labelPrefix="Model "
                  values={draft.defaultValues ?? {}}
                  onChange={(defaultValues) => change({ defaultValues })}
                />
              </details>
            )}
          </>
        )}
        <fieldset disabled={busy} className="mb-6 border-t border-line pt-5">
          <legend className="text-sm font-medium">Context length</legend>
          <p className="mb-3 text-xs text-fg-2">
            Applies to {model ? modelLabel(model) : "this model"} in every chat.
          </p>
          <Input
            aria-label="Context length"
            type="number"
            min={1024}
            max={limit ?? undefined}
            aria-invalid={!validContext}
            aria-describedby={contextId}
            value={draft.context}
            onChange={(e) => change({ context: e.target.value })}
          />
          <p
            id={contextId}
            className={`my-3 text-xs ${validContext ? "text-fg-3" : "text-danger"}`}
          >
            {limit
              ? `Configured limit: ${limit / 1024}K tokens.`
              : "Minimum: 1K tokens."}
            {!validContext &&
              " Choose a whole-number context within this limit."}
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
                  onClick={() => change({ context: String(n) })}
                >
                  {n / 1024}K
                </Button>
              ))}
          </div>
        </fieldset>
        <footer className="sticky bottom-0 -mx-5 -mb-5 flex flex-col gap-2 border-t border-line bg-surface p-5">
          {(dirty || contextDirty) && (
            <p className="text-xs text-fg-2" role="status">
              Unsaved changes
            </p>
          )}
          <Button
            aria-label={
              defaultsOnly ? "Save as model defaults" : "Save settings"
            }
            disabled={
              !model ||
              !valid ||
              !validContext ||
              (!dirty && !contextDirty) ||
              busy ||
              !samplingValid(draft.defaultValues ?? {}) ||
              (imageOnly && !contextDirty)
            }
            onClick={() => void save()}
          >
            {saved ? (
              <>
                <Check className="size-4" />
                Saved
              </>
            ) : busy ? (
              "Saving…"
            ) : defaultsOnly ? (
              "Save as model defaults"
            ) : (
              "Save settings"
            )}
          </Button>
          <Button
            variant="ghost"
            disabled={!model || busy || imageOnly}
            onClick={() => change({ values: {} })}
          >
            Reset to model defaults
          </Button>
        </footer>
      </fieldset>
      {editor && (
        <Suspense fallback={<p role="status">Opening preset editor…</p>}>
          <PresetEditor
            request={request}
            params={params}
            prompt={draft.useDefault ? null : draft.prompt}
            onClose={() => setEditor(false)}
            onSaved={() =>
              void query.invalidateQueries({
                queryKey: ["presets", ...queryScope],
              })
            }
          />
        </Suspense>
      )}
    </section>
  );
}

export function ChatControlsUnavailable({
  failed = false,
  drawer = false,
  retry,
}: {
  failed?: boolean;
  drawer?: boolean;
  retry: () => void;
}) {
  return (
    <section className="p-5" aria-label="Chat controls">
      {!drawer && (
        <header className="mb-5 flex items-center justify-between">
          <h2 className="font-medium">Chat controls</h2>
          <IconButton
            label="Close chat controls"
            onClick={() => useUI.getState().set({ panel: false })}
          >
            <X />
          </IconButton>
        </header>
      )}
      <p role={failed ? "alert" : "status"} className="text-sm text-fg-2">
        {failed ? "Couldn't load chat controls." : "Loading chat controls…"}
      </p>
      {failed && (
        <Button variant="outline" onClick={retry}>
          Retry
        </Button>
      )}
    </section>
  );
}

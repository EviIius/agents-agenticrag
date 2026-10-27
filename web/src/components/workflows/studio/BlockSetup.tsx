import { modelLabel } from "@/lib/chat-presentation";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { IconButton } from "@/components/app/IconButton";
import { X } from "lucide-react";
import type { Block, ModelChoice } from "./types";
import type { Model } from "@/lib/api";
import { useStudio } from "./store";
import { uniqueKey, renameField } from "./graph";
import { useResources } from "./api";
import { VariableField } from "./VariableField";
import { TextField, Choice, Toggle, Segments, Advanced } from "./fields";
export const modelKey = (m: { connection_id: string; model_id: string }) =>
  JSON.stringify([m.connection_id, m.model_id]);
export function ModelField({
  value,
  onChange,
  allowDefault = true,
  label = "Model",
}: {
  value: ModelChoice | null;
  onChange: (v: ModelChoice | null) => void;
  allowDefault?: boolean;
  label?: string;
}) {
  const { models, compatible } = useResources();
  const defaultModel = useStudio((s) => s.draft.graph.settings.default_model);
  const defaultInfo = models.find(
    (m) => defaultModel && modelKey(m) === modelKey(defaultModel),
  );
  const defaultName = defaultInfo
    ? modelLabel(defaultInfo)
    : defaultModel?.model_id;
  const selected =
    value === "workflow_default" ? "default" : value ? modelKey(value) : "none";
  const choices = models
    .filter((m) => m.chat_capable && (!m.hidden || modelKey(m) === selected))
    .map((m) => ({
      value: modelKey(m),
      label:
        modelLabel(m) +
        (compatible.some(
          (c) =>
            c.connection_id === m.connection_id && c.model_id === m.model_id,
        )
          ? " · tested with images"
          : ""),
    }));
  if (
    value &&
    value !== "workflow_default" &&
    !choices.some((c) => c.value === selected)
  )
    choices.push({ value: selected, label: value.model_id + " · unavailable" });
  return (
    <Choice
      label={label}
      value={selected}
      choices={[
        { value: "none", label: "Choose a model" },
        ...(allowDefault
          ? [
              {
                value: "default",
                label: defaultName
                  ? "Workflow default (" + defaultName + ")"
                  : "Workflow default",
              },
            ]
          : []),
        ...choices,
      ]}
      onChange={(v) => {
        if (v === "default") onChange("workflow_default");
        else if (v === "none") onChange(null);
        else {
          const [connection_id, model_id] = JSON.parse(v) as [string, string];
          onChange({ connection_id, model_id });
        }
      }}
    />
  );
}
export function BlockSetup({
  node,
  onPreview,
}: {
  node: Block;
  onPreview: () => void;
}) {
  const update = useStudio((s) => s.block),
    doc = useStudio((s) => s.draft.graph);
  const { models } = useResources();
  const set = (config: Block["config"], field?: string) =>
    update(
      node.id,
      (n) => ({ ...n, config }) as Block,
      field ? node.id + ":" + field : undefined,
    );
  switch (node.kind) {
    case "start":
      return (
        <>
          <h3 className="wf-label">Inputs</h3>
          {node.config.fields.map((f, index) => {
            const change = (next: typeof f) =>
              set(
                {
                  ...node.config,
                  fields: node.config.fields.map((item, i) =>
                    i === index ? next : item,
                  ),
                },
                `field-${index}`,
              );
            return (
              <fieldset key={index} className="wf-input-card">
                <legend className="sr-only">Input {index + 1}</legend>
                <div className="flex items-center gap-2">
                  <TextField
                    label="Input label"
                    value={f.label}
                    maxLength={80}
                    onChange={(label) => change({ ...f, label })}
                  />
                  <IconButton
                    label={`Remove input ${f.label}`}
                    onClick={() =>
                      set({
                        ...node.config,
                        fields: node.config.fields.filter(
                          (_, i) => i !== index,
                        ),
                      })
                    }
                  >
                    <X />
                  </IconButton>
                </div>
                <StartReferenceName key={f.name} node={node} name={f.name} />
                <Choice
                  label="Input type"
                  value={f.type}
                  choices={Object.entries({
                    short_text: "Short text",
                    long_text: "Long text",
                    number: "Number",
                    boolean: "Yes / No",
                    choice: "Choice",
                    recording: "Recording",
                    document: "Document",
                    image: "Image",
                  }).map(([value, label]) => ({ value, label }))}
                  onChange={(type) =>
                    change({ ...f, type: type as typeof f.type, default: null })
                  }
                />
                <Toggle
                  label="Required input"
                  checked={f.required}
                  onChange={(required) => change({ ...f, required })}
                />
                {f.type === "choice" && (
                  <TextField
                    label="Choices (comma separated)"
                    value={f.choices.join(",")}
                    onChange={(v) =>
                      change({
                        ...f,
                        choices: v
                          .split(",")
                          .map((x) => x.trim())
                          .filter(Boolean),
                      })
                    }
                  />
                )}
                {!["recording", "document", "image"].includes(f.type) &&
                  (f.type === "boolean" ? (
                    <Toggle
                      label="Default value"
                      checked={Boolean(f.default)}
                      onChange={(v) => change({ ...f, default: v })}
                    />
                  ) : (
                    <TextField
                      label="Default value"
                      type={f.type === "number" ? "number" : "text"}
                      value={f.default == null ? "" : String(f.default)}
                      onChange={(v) =>
                        change({
                          ...f,
                          default: !v
                            ? null
                            : f.type === "number"
                              ? Number(v)
                              : v,
                        })
                      }
                    />
                  ))}
                <TextField
                  label="Help text"
                  value={f.help}
                  onChange={(help) => change({ ...f, help })}
                  maxLength={500}
                />
              </fieldset>
            );
          })}
          <Button
            variant="ghost"
            className="wf-addlink"
            disabled={node.config.fields.length >= 12}
            onClick={() => {
              const name = uniqueKey(
                "input",
                new Set(node.config.fields.map((f) => f.name)),
              );
              set({
                fields: [
                  ...node.config.fields,
                  {
                    name,
                    label: "New input",
                    type: "long_text",
                    required: false,
                    default: null,
                    choices: [],
                    help: "",
                  },
                ],
              });
            }}
          >
            + Add an input
          </Button>
        </>
      );
    case "generate": {
      const selected =
        node.config.model === "workflow_default"
          ? doc.settings.default_model
          : node.config.model;
      const model = models.find(
        (m) => selected && modelKey(m) === modelKey(selected),
      );
      return (
        <>
          <ModelField
            value={node.config.model}
            onChange={(model) =>
              set({ ...node.config, model: model ?? "workflow_default" })
            }
          />
          <VariableField
            nodeId={node.id}
            label="Instructions"
            value={node.config.instructions}
            onChange={(instructions) =>
              set({ ...node.config, instructions }, "instructions")
            }
            help="Sent as the system message."
          />
          <VariableField
            nodeId={node.id}
            label="Prompt"
            value={node.config.prompt}
            onChange={(prompt) => set({ ...node.config, prompt }, "prompt")}
            help="Type {{ or press {x} to insert output from an earlier block."
          />
          <Segments
            label="Output"
            value={node.config.format}
            options={[
              ["text", "Text"],
              ["markdown", "Markdown"],
              ["json", "JSON fields"],
            ]}
            onChange={(format) =>
              set({
                ...node.config,
                format: format as typeof node.config.format,
                json_fields: format === "json" ? node.config.json_fields : [],
              })
            }
          />
          {node.config.format === "json" && (
            <div className="wf-field-stack">
              {node.config.json_fields.map((f, i) => (
                <fieldset className="wf-input-card" key={i}>
                  <legend className="sr-only">JSON field {i + 1}</legend>
                  <TextField
                    label="JSON field name"
                    value={f.name}
                    onChange={(name) =>
                      set(
                        {
                          ...node.config,
                          json_fields: node.config.json_fields.map((v, n) =>
                            n === i ? { ...v, name } : v,
                          ),
                        },
                        `json-${i}`,
                      )
                    }
                  />
                  <Choice
                    label="JSON field type"
                    value={f.type}
                    choices={["string", "number", "boolean"].map((v) => ({
                      value: v,
                      label: v,
                    }))}
                    onChange={(type) =>
                      set({
                        ...node.config,
                        json_fields: node.config.json_fields.map((v, n) =>
                          n === i ? { ...v, type: type as typeof f.type } : v,
                        ),
                      })
                    }
                  />
                  <TextField
                    label="JSON field description"
                    value={f.description}
                    onChange={(description) =>
                      set(
                        {
                          ...node.config,
                          json_fields: node.config.json_fields.map((v, n) =>
                            n === i ? { ...v, description } : v,
                          ),
                        },
                        `json-${i}`,
                      )
                    }
                  />
                  <Button
                    variant="ghost"
                    onClick={() =>
                      set({
                        ...node.config,
                        json_fields: node.config.json_fields.filter(
                          (_, n) => n !== i,
                        ),
                      })
                    }
                  >
                    Remove field
                  </Button>
                </fieldset>
              ))}
              <Button
                variant="ghost"
                disabled={node.config.json_fields.length >= 20}
                onClick={() =>
                  set({
                    ...node.config,
                    json_fields: [
                      ...node.config.json_fields,
                      {
                        name: uniqueKey(
                          "field",
                          new Set(node.config.json_fields.map((f) => f.name)),
                        ),
                        type: "string",
                        description: "",
                      },
                    ],
                  })
                }
              >
                + Add JSON field
              </Button>
            </div>
          )}
          <Advanced title="Optional overrides">
            <Sampling node={node} model={model} set={set} />
            <p className="wf-help">
              Empty fields send nothing of their own: your saved model defaults
              apply, then the runtime's.
            </p>
          </Advanced>
          <Button variant="outline" className="self-start" onClick={onPreview}>
            Preview prompt
          </Button>
        </>
      );
    }
    case "transcribe":
      return (
        <VariableField
          nodeId={node.id}
          label="Recording"
          value={node.config.recording}
          typed="recording"
          onChange={(recording) => set({ recording }, "recording")}
          help="A Recording input from Start. Uses your glossary from Settings."
        />
      );
    case "clean_transcript":
      return (
        <>
          <VariableField
            nodeId={node.id}
            label="Transcript"
            value={node.config.transcript}
            typed="transcript"
            onChange={(transcript) =>
              set({ ...node.config, transcript }, "transcript")
            }
          />
          <ModelField
            value={node.config.model}
            onChange={(model) =>
              set({ ...node.config, model: model ?? "workflow_default" })
            }
          />
          <p className="wf-help">
            Uses your transcription clean-up settings. The original transcript
            is always kept and stays the source.
          </p>
        </>
      );
    case "generate_image":
      return (
        <>
          <VariableField
            nodeId={node.id}
            label="Prompt"
            value={node.config.prompt}
            onChange={(prompt) => set({ ...node.config, prompt }, "prompt")}
            help="At most 4,000 characters after variables are filled."
          />
          <Segments
            label="Images"
            value={String(node.config.count)}
            options={[
              ["1", "1"],
              ["2", "2"],
              ["3", "3"],
            ]}
            onChange={(count) =>
              set({
                ...node.config,
                count: Number(count),
                seeds:
                  node.config.seeds === "auto"
                    ? "auto"
                    : Array.from({ length: Number(count) }, (_, i) =>
                        node.config.seeds === "auto"
                          ? 0
                          : (node.config.seeds[i] ?? 0),
                      ),
              })
            }
          />
          <Segments
            label="Seeds"
            value={node.config.seeds === "auto" ? "auto" : "advanced"}
            options={[
              ["auto", "Automatic"],
              ["advanced", "Advanced"],
            ]}
            onChange={(v) =>
              set({
                ...node.config,
                seeds:
                  v === "auto"
                    ? "auto"
                    : (Array(node.config.count).fill(0) as number[]),
              })
            }
          />
          {Array.isArray(node.config.seeds) &&
            node.config.seeds.map((seed, index) => (
              <TextField
                key={index}
                type="number"
                min={0}
                max={4294967295}
                label={`Seed ${index + 1}`}
                value={String(seed)}
                onChange={(v) => {
                  const num = Number(v);
                  if (Number.isInteger(num) && num >= 0 && num <= 4294967295)
                    set(
                      {
                        ...node.config,
                        seeds: (node.config.seeds as number[]).map((s, i) =>
                          i === index ? num : s,
                        ),
                      },
                      `seed-${index}`,
                    );
                }}
              />
            ))}
        </>
      );
    case "review":
      return (
        <>
          <VariableField
            nodeId={node.id}
            label="Show"
            value={node.config.show}
            onChange={(show) => set({ ...node.config, show }, "show")}
            help="The text you'll check when the run pauses here."
          />
          <Toggle
            label="Allow editing"
            checked={node.config.editable}
            onChange={(editable) => set({ ...node.config, editable })}
          />
          <TextField
            label="Message"
            value={node.config.message}
            maxLength={1000}
            onChange={(message) => set({ ...node.config, message }, "message")}
          />
        </>
      );
    case "pick":
      return (
        <>
          <Choice
            label="Choose from"
            value={node.config.type}
            choices={[
              { value: "image_list", label: "Images" },
              { value: "text", label: "Text outputs" },
            ]}
            onChange={(type) =>
              set({
                ...node.config,
                type: type as "text" | "image_list",
                from: [],
              })
            }
          />
          {node.config.from.map((value, index) => (
            <div key={index} className="wf-field">
              <VariableField
                nodeId={node.id}
                label={`From ${index + 1}`}
                value={value}
                typed={node.config.type}
                onChange={(v) =>
                  set({
                    ...node.config,
                    from: node.config.from.map((old, i) =>
                      i === index ? v : old,
                    ),
                  })
                }
              />
              <Button
                variant="ghost"
                onClick={() =>
                  set({
                    ...node.config,
                    from: node.config.from.filter((_, i) => i !== index),
                  })
                }
              >
                Remove choice source {index + 1}
              </Button>
            </div>
          ))}
          <Button
            variant="outline"
            onClick={() =>
              set({ ...node.config, from: [...node.config.from, ""] })
            }
            disabled={node.config.from.length >= 20}
          >
            Add choice source
          </Button>
          <TextField
            label="Maximum favorites"
            type="number"
            value={String(node.config.maximum)}
            onChange={(v) =>
              set({
                ...node.config,
                maximum: Math.max(1, Math.min(20, Number(v) || 1)),
              })
            }
          />
        </>
      );
    case "output":
      return (
        <>
          <h3 className="wf-label">Include</h3>
          {node.config.include.map((item, i) => (
            <div key={i} className="wf-input-card">
              <TextField
                label="Result label"
                value={item.label}
                maxLength={80}
                onChange={(label) =>
                  set(
                    {
                      ...node.config,
                      include: node.config.include.map((v, index) =>
                        index === i ? { ...v, label } : v,
                      ),
                    },
                    `result-label-${i}`,
                  )
                }
              />
              <VariableField
                nodeId={node.id}
                label="Result"
                value={item.ref}
                typed="any"
                onChange={(ref) =>
                  set(
                    {
                      ...node.config,
                      include: node.config.include.map((v, index) =>
                        index === i ? { ...v, ref } : v,
                      ),
                    },
                    `result-ref-${i}`,
                  )
                }
              />
              <Button
                variant="ghost"
                onClick={() =>
                  set({
                    ...node.config,
                    include: node.config.include.filter(
                      (_, index) => index !== i,
                    ),
                  })
                }
              >
                Remove item
              </Button>
            </div>
          ))}
          <Button
            className="wf-addlink"
            variant="ghost"
            disabled={node.config.include.length >= 40}
            onClick={() =>
              set({
                ...node.config,
                include: [...node.config.include, { label: "Result", ref: "" }],
              })
            }
          >
            + Add an item
          </Button>
          <div className="wf-field">
            <span className="wf-label">Formats</span>
            <div className="wf-segments">
              {(["md", "json"] as const).map((format) => (
                <Button
                  key={format}
                  variant="ghost"
                  aria-pressed={node.config.formats.includes(format)}
                  onClick={() => {
                    const formats = node.config.formats.includes(format)
                      ? node.config.formats.filter((f) => f !== format)
                      : [...node.config.formats, format];
                    if (formats.length) set({ ...node.config, formats });
                  }}
                >
                  {format === "md" ? "Markdown" : "JSON"}
                </Button>
              ))}
            </div>
            <p className="wf-help">Images are always saved as PNG.</p>
          </div>
          <Toggle
            label="Include original sources"
            checked={node.config.include_sources}
            onChange={(include_sources) =>
              set({ ...node.config, include_sources })
            }
            help="Original transcripts travel with the export."
          />
        </>
      );
  }
}
function Sampling({
  node,
  model,
  set,
}: {
  node: Extract<Block, { kind: "generate" }>;
  model?: Model;
  set: (config: Block["config"], group?: string) => void;
}) {
  const [invalid, setInvalid] = useState("");
  return (
    <>
      {(
        [
          ["temperature", "Temperature", 0, 2, 0.1],
          ["top_p", "Top-p", 0, 1, 0.05],
          ["top_k", "Top-k", 1, 100000, 1],
          ["max_tokens", "Output limit", 1, 1000000, 1],
          ["seed", "Seed", 0, 4294967295, 1],
        ] as const
      ).map(([name, label, min, max, step]) => (
        <TextField
          key={name}
          label={label}
          value={
            node.config.params[name] == null
              ? ""
              : String(node.config.params[name])
          }
          type="number"
          min={min}
          max={max}
          step={step}
          placeholder="Model default"
          onChange={(v) => {
            const params = { ...node.config.params };
            if (!v) {
              delete params[name];
              setInvalid("");
            } else {
              const num = Number(v);
              if (
                !Number.isFinite(num) ||
                num < min ||
                num > max ||
                (step === 1 && !Number.isInteger(num))
              ) {
                setInvalid(`${label} must be within ${min}–${max}.`);
                return;
              }
              params[name] = num;
              setInvalid("");
            }
            set({ ...node.config, params }, name);
          }}
        />
      ))}
      {invalid && (
        <p role="alert" className="text-sm text-danger">
          {invalid}
        </p>
      )}
      {model?.reasoning?.options.length ? (
        <Choice
          label="Thinking"
          value={node.config.params.reasoning ?? "default"}
          choices={[
            { value: "default", label: "Model default" },
            ...model.reasoning.options.map((v) => ({ value: v, label: v })),
          ]}
          onChange={(v) => {
            const params = { ...node.config.params };
            if (v === "default") delete params.reasoning;
            else params.reasoning = v;
            set({ ...node.config, params });
          }}
        />
      ) : null}
    </>
  );
}

function StartReferenceName({
  node,
  name,
}: {
  node: Extract<Block, { kind: "start" }>;
  name: string;
}) {
  const [value, setValue] = useState(name),
    [error, setError] = useState("");
  const edit = useStudio((s) => s.edit);
  const commit = () => {
    if (
      !/^[a-z][a-z0-9_]{0,31}$/.test(value) ||
      node.config.fields.some((f) => f.name === value && f.name !== name)
    ) {
      setError(
        "Use a unique reference name beginning with a lowercase letter.",
      );
      return;
    }
    edit((d) => ({ ...d, graph: renameField(d.graph, node.key, name, value) }));
    setError("");
  };
  return (
    <>
      <TextField
        label="Input reference name"
        value={value}
        onChange={setValue}
        onBlur={commit}
        onKeyDown={(e) => {
          if (e.key === "Enter") commit();
        }}
      />
      {error && (
        <p role="alert" className="wf-help text-danger">
          {error}
        </p>
      )}
    </>
  );
}

import { BlockOutput } from "./BlockOutput";
import { useState } from "react";
import { X, Copy } from "lucide-react";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { IconButton } from "@/components/app/IconButton";
import { useStudio } from "./store";
import { ports, outputs, registry } from "./registry";
import { connect, canConnect, renameKey, pasteRemap, remove } from "./graph";
import { BlockMenu } from "./BlockMenu";
import { BlockSetup, ModelField } from "./BlockSetup";
import { Advanced, Choice, TextField, Toggle } from "./fields";
import { workflowIcons } from "./icons";
import type { Block, Run } from "./types";
export function Inspector({
  close,
  settings = false,
  preview,
  latest,
  structureDisabled = false,
}: {
  close: () => void;
  settings?: boolean;
  preview: () => void;
  latest?: Run;
  structureDisabled?: boolean;
}) {
  const draft = useStudio((s) => s.draft),
    selection = useStudio((s) => s.selection),
    edit = useStudio((s) => s.edit),
    update = useStudio((s) => s.block);
  const node = draft.graph.nodes.find((n) => n.id === selection[0]);
  if (settings)
    return (
      <div className="wf-inspector">
        <header className="wf-panel-head">
          <h2>Workflow settings</h2>
          <IconButton label="Close settings panel" onClick={close}>
            <X />
          </IconButton>
        </header>
        <div className="wf-panel-body">
          <TextField
            label="Workflow name"
            value={draft.name}
            maxLength={80}
            onChange={(name) => edit((d) => ({ ...d, name }), "name")}
          />
          <TextField
            label="Description"
            value={draft.description}
            maxLength={1000}
            onChange={(description) =>
              edit((d) => ({ ...d, description }), "description")
            }
          />
          <Choice
            label="Icon"
            value={draft.icon}
            choices={Object.keys(workflowIcons).map((value) => ({
              value,
              label: value.charAt(0).toUpperCase() + value.slice(1),
            }))}
            onChange={(icon) =>
              edit((d) => ({ ...d, icon: icon as typeof d.icon }))
            }
          />
          <ModelField
            label="Default text model"
            allowDefault={false}
            value={draft.graph.settings.default_model ?? null}
            onChange={(model) =>
              edit((d) => ({
                ...d,
                graph: {
                  ...d.graph,
                  settings: {
                    ...d.graph.settings,
                    default_model: model === "workflow_default" ? null : model,
                  },
                },
              }))
            }
          />
          <Toggle
            label="Keep test runs for 7 days"
            checked={draft.graph.settings.keep_test_runs_days === 7}
            onChange={(keep) =>
              edit((d) => ({
                ...d,
                graph: {
                  ...d.graph,
                  settings: {
                    ...d.graph.settings,
                    keep_test_runs_days: keep ? 7 : 1,
                  },
                },
              }))
            }
          />
          <p className="wf-help">
            Test runs are hidden from Recent runs. Saved versions can be
            restored from the workflow menu.
          </p>
        </div>
      </div>
    );
  if (selection.length > 1)
    return (
      <div className="wf-inspector">
        <header className="wf-panel-head">
          <h2>{selection.length} blocks selected</h2>
          <IconButton label="Close Inspector" onClick={close}>
            <X />
          </IconButton>
        </header>
        <div className="wf-panel-body">
          <Button
            variant="outline"
            onClick={() =>
              edit((d) => ({
                ...d,
                graph: pasteRemap(d.graph, {
                  nodes: d.graph.nodes.filter((n) => selection.includes(n.id)),
                  edges: d.graph.edges.filter(
                    (e) =>
                      selection.includes(e.source) &&
                      selection.includes(e.target),
                  ),
                  notes: d.graph.notes.filter((n) => selection.includes(n.id)),
                }),
              }))
            }
          >
            Duplicate selected blocks
          </Button>
          <Button
            variant="outline"
            onClick={() =>
              edit((d) => ({
                ...d,
                graph: {
                  ...d.graph,
                  nodes: d.graph.nodes.map((n) =>
                    selection.includes(n.id) && n.kind !== "start"
                      ? { ...n, disabled: true }
                      : n,
                  ),
                },
              }))
            }
          >
            Disable selected blocks
          </Button>
          <Button
            variant="outline"
            onClick={() => {
              edit((d) => ({ ...d, graph: remove(d.graph, selection) }));
              close();
            }}
          >
            Delete selected blocks
          </Button>
        </div>
      </div>
    );
  if (!node) return null;
  const meta = registry[node.kind];

  return (
    <div className="wf-inspector" key={node.id}>
      <header className="wf-panel-head">
        <span className="wf-tile" data-cat={meta.tone}>
          <meta.Icon />
        </span>
        <div className="min-w-0 flex-1">
          <input
            className="wf-title-input"
            aria-label="Block name"
            maxLength={80}
            value={node.title}
            onChange={(e) =>
              update(
                node.id,
                (n) => ({ ...n, title: e.target.value }),
                node.id + ":title",
              )
            }
          />
          <p className="wf-help">{meta.label}</p>
        </div>
        <BlockMenu node={node} structureDisabled={structureDisabled} />
        <IconButton label="Close Inspector" onClick={close}>
          <X />
        </IconButton>
      </header>
      <Tabs defaultValue="setup" className="wf-inspector-tabs">
        <TabsList className="wf-tabs" aria-label="Block settings">
          <TabsTrigger value="setup">Setup</TabsTrigger>
          <TabsTrigger value="output">Output</TabsTrigger>
        </TabsList>
        <TabsContent value="setup" className="wf-panel-body">
          <BlockSetup node={node} onPreview={preview} />
          <Connections node={node} disabled={structureDisabled} />
          <div className="wf-field">
            <h3 className="wf-section-title">PRODUCES</h3>
            {Object.keys(outputs(node)).length ? (
              <div className="flex flex-wrap gap-1">
                {Object.keys(outputs(node)).map((field) => (
                  <Button
                    key={field}
                    variant="ghost"
                    className="wf-chip"
                    aria-label={`Copy reference ${node.key}.${field}`}
                    onClick={() =>
                      void navigator.clipboard.writeText(
                        `{{${node.key}.${field}}}`,
                      )
                    }
                  >
                    <Copy className="size-3" />
                    {`{{${node.key}.${field}}}`}
                  </Button>
                ))}
              </div>
            ) : (
              <p className="wf-help">Save results ends this path.</p>
            )}
          </div>
          <ReferenceName node={node} />
        </TabsContent>
        <TabsContent value="output" className="wf-panel-body">
          <BlockOutput nodeId={node.id} latest={latest} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
function ReferenceName({ node }: { node: Block }) {
  const doc = useStudio((s) => s.draft.graph),
    edit = useStudio((s) => s.edit);
  const [value, setValue] = useState(node.key);
  const [error, setError] = useState("");
  const commit = () => {
    const next = renameKey(doc, node.key, value);
    if (next === doc && value !== node.key)
      setError(
        "Use a unique name starting with a lowercase letter, followed by letters, numbers or underscores.",
      );
    else {
      setError("");
      edit((d) => ({ ...d, graph: next }));
    }
  };
  return (
    <Advanced>
      <TextField
        label="Reference name"
        value={value}
        onChange={(v) => {
          setValue(v);
          setError("");
        }}
        onBlur={commit}
        onKeyDown={(e) => {
          if (e.key === "Enter") commit();
        }}
        help="Other blocks use this name. Renaming updates every reference."
      />
      {error && (
        <p role="alert" className="text-xs text-danger">
          {error}
        </p>
      )}
    </Advanced>
  );
}
function Connections({ node, disabled }: { node: Block; disabled: boolean }) {
  const doc = useStudio((s) => s.draft.graph),
    edit = useStudio((s) => s.edit);
  const remove = (id: string) =>
    edit((d) => ({
      ...d,
      graph: { ...d.graph, edges: d.graph.edges.filter((e) => e.id !== id) },
    }));
  const incoming = doc.edges.filter((e) => e.target === node.id),
    outgoing = doc.edges.filter((e) => e.source === node.id);
  return (
    <section className="wf-connections wf-field-stack" aria-label="Connections">
      <h3 className="wf-section-title">GETS INPUT FROM</h3>
      {incoming.map((e) => (
        <div className="wf-connection-row" key={e.id}>
          <span>
            {doc.nodes.find((n) => n.id === e.source)?.title}{" "}
            {e.source_port !== "out" ? `· ${e.source_port}` : ""}
          </span>
          <IconButton
            label={`Remove input connection ${e.id}`}
            disabled={disabled}
            onClick={() => remove(e.id)}
          >
            <X />
          </IconButton>
        </div>
      ))}
      {node.kind !== "start" && (
        <Choice
          label="Add an input connection"
          disabled={disabled}
          value="add"
          choices={[
            { value: "add", label: "Add connection…" },
            ...doc.nodes.flatMap((n) =>
              ports(n)
                .filter((port) => canConnect(doc, n.id, node.id, port))
                .map((port) => ({
                  value: JSON.stringify([n.id, port]),
                  label: n.title + (port !== "out" ? ` · ${port}` : ""),
                })),
            ),
          ]}
          onChange={(v) => {
            if (v !== "add") {
              const [source, port] = JSON.parse(v) as [string, string];
              edit((d) => ({
                ...d,
                graph: connect(d.graph, source, node.id, port),
              }));
            }
          }}
        />
      )}
      {node.kind === "start" && (
        <p className="wf-help">Start begins the run.</p>
      )}
      <h3 className="wf-section-title">SENDS OUTPUT TO</h3>
      {outgoing.map((e) => (
        <div className="wf-connection-row" key={e.id}>
          <span>
            {doc.nodes.find((n) => n.id === e.target)?.title}
            {e.source_port !== "out" ? ` · ${e.source_port}` : ""}
          </span>
          <IconButton
            label={`Remove output connection ${e.id}`}
            disabled={disabled}
            onClick={() => remove(e.id)}
          >
            <X />
          </IconButton>
        </div>
      ))}
      {ports(node).length > 0 && (
        <Choice
          label="Add an output connection"
          disabled={disabled}
          value="add"
          choices={[
            { value: "add", label: "Add connection…" },
            ...doc.nodes.flatMap((n) =>
              ports(node)
                .filter((port) => canConnect(doc, node.id, n.id, port))
                .map((port) => ({
                  value: JSON.stringify([n.id, port]),
                  label: n.title + (port !== "out" ? ` · ${port}` : ""),
                })),
            ),
          ]}
          onChange={(v) => {
            if (v !== "add") {
              const [target, port] = JSON.parse(v) as [string, string];
              edit((d) => ({
                ...d,
                graph: connect(d.graph, node.id, target, port),
              }));
            }
          }}
        />
      )}
    </section>
  );
}

import { useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import { uploadWithProgress } from "@/lib/attachments";
import type { components } from "@/lib/api-types";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Choice, TextField, Toggle } from "./fields";
import type { Doc, Run } from "./types";
export function RunInputs({
  doc,
  defId,
  beforeRun,
  accepted,
  preview = false,
}: {
  doc: Doc;
  defId: string;
  beforeRun: () => Promise<boolean>;
  accepted: (run: Run) => void;
  preview?: boolean;
}) {
  const start = doc.nodes.find((n) => n.kind === "start");
  const [values, setValues] = useState<Record<string, unknown>>({}),
    [busy, setBusy] = useState(false),
    [notice, setNotice] = useState("");
  const [recordings, setRecordings] = useState<
    components["schemas"]["WorkflowRecording"][]
  >([]);
  const [upload, setUpload] = useState<{ name: string; percent: number }>();
  const request = useRef<{ key: string; body: string } | undefined>(undefined);
  const controller = useRef<AbortController | undefined>(undefined);
  useEffect(() => {
    if (preview) return;
    let mounted = true;
    if (start?.config.fields.some((f) => f.type === "recording"))
      void api<components["schemas"]["WorkflowRecording"][]>(
        "/workflows/recordings",
      ).then(
        (v) => {
          if (mounted) setRecordings(v);
        },
        () => {
          if (mounted)
            setNotice(
              "Saved recordings couldn't be loaded. You can upload one below.",
            );
        },
      );
    return () => {
      mounted = false;
      controller.current?.abort();
    };
  }, [preview, start]);
  const fieldValue = (name: string, fallback: unknown) =>
    name in values ? values[name] : fallback;
  const missing =
    start?.config.fields.filter(
      (f) =>
        f.required &&
        (fieldValue(f.name, f.default) == null ||
          fieldValue(f.name, f.default) === ""),
    ) ?? [];
  const submit = async () => {
    if (preview || busy || missing.length) return;
    setBusy(true);
    setNotice("");
    try {
      if (!(await beforeRun())) {
        setNotice(
          "Save the workflow before running. Resolve the save conflict or retry.",
        );
        return;
      }
      const body = JSON.stringify(values);
      if (request.current?.body !== body)
        request.current = { key: crypto.randomUUID(), body };
      const run = await api<Run>(`/workflows/defs/${defId}/runs`, {
        request_key: request.current!.key,
        inputs: values,
      });
      request.current = undefined;
      accepted(run);
    } catch (error) {
      setNotice(
        error instanceof Error
          ? error.message
          : "Couldn't start the run. Try again with the same inputs.",
      );
    } finally {
      setBusy(false);
    }
  };
  async function addFile(name: string, file: File) {
    setNotice("");
    const c = new AbortController();
    controller.current = c;
    setUpload({ name, percent: 0 });
    try {
      const attachment = await uploadWithProgress(
        file,
        (p) => setUpload({ name, percent: p }),
        c.signal,
      );
      setValues((v) => ({ ...v, [name]: attachment.id }));
    } catch (error) {
      setNotice(
        error instanceof Error ? error.message : "Upload failed. Try again.",
      );
    } finally {
      setUpload(undefined);
    }
  }
  return (
    <form
      className="wf-field-stack"
      onSubmit={(e) => {
        e.preventDefault();
        void submit();
      }}
      aria-label="Run workflow inputs"
    >
      <h2 className="text-base font-semibold">Run workflow</h2>
      {start?.config.fields.map((f) => {
        const value = fieldValue(f.name, f.default);
        const change = (v: unknown) =>
          setValues((old) => ({ ...old, [f.name]: v }));
        if (["recording", "document", "image"].includes(f.type))
          return (
            <div className="wf-field" key={f.name}>
              <span className="wf-label">
                {f.label}
                {f.required ? " *" : ""}
              </span>
              {f.type === "recording" && (
                <Choice
                  label="Saved recording"
                  value={typeof value === "string" && value ? value : "none"}
                  choices={[
                    { value: "none", label: "Choose a saved recording" },
                    ...recordings.map((r) => ({
                      value: r.id,
                      label: r.filename,
                    })),
                  ]}
                  onChange={(v) => change(v === "none" ? "" : v)}
                />
              )}
              <label className="wf-upload-label">
                Upload {f.label}
                <input
                  type="file"
                  aria-label={`Upload ${f.label}`}
                  accept={
                    f.type === "recording"
                      ? "audio/*,.wav,.m4a"
                      : f.type === "document"
                        ? ".pdf,.docx"
                        : "image/*"
                  }
                  disabled={!!upload || preview}
                  onChange={(e) => {
                    if (e.target.files?.[0])
                      void addFile(f.name, e.target.files[0]);
                  }}
                />
              </label>
              {upload?.name === f.name && (
                <p role="status">
                  Uploading · {upload.percent}%{" "}
                  <Button
                    variant="ghost"
                    onClick={() => controller.current?.abort()}
                  >
                    Cancel upload
                  </Button>
                </p>
              )}
              {value ? (
                <p role="status" className="wf-help">
                  File ready.
                </p>
              ) : null}
              {f.help && <p className="wf-help">{f.help}</p>}
            </div>
          );
        if (f.type === "boolean")
          return (
            <Toggle
              key={f.name}
              label={f.label}
              checked={Boolean(value)}
              onChange={change}
              help={f.help}
            />
          );
        if (f.type === "choice")
          return (
            <Choice
              key={f.name}
              label={f.label}
              value={typeof value === "string" ? value : ""}
              choices={f.choices
                .filter(Boolean)
                .map((c) => ({ value: c, label: c }))}
              onChange={change}
              help={f.help}
            />
          );
        if (f.type === "long_text")
          return (
            <label key={f.name} className="wf-field">
              {f.label}
              <Textarea
                aria-label={f.label}
                value={value == null ? "" : String(value)}
                maxLength={20000}
                rows={5}
                onChange={(e) => change(e.target.value)}
              />
              <span className="wf-help">{f.help}</span>
            </label>
          );
        return (
          <TextField
            key={f.name}
            label={f.label}
            value={value == null ? "" : String(value)}
            type={f.type === "number" ? "number" : "text"}
            onChange={(v) =>
              change(v === "" ? null : f.type === "number" ? Number(v) : v)
            }
            help={f.help}
          />
        );
      })}
      {missing.length > 0 && (
        <p className="wf-help">
          Add {missing.map((f) => f.label).join(", ")} to start.
        </p>
      )}
      {notice && (
        <p role="alert" className="text-sm text-danger">
          {notice}
        </p>
      )}
      <Button type="submit" disabled={busy || !!upload || !!missing.length}>
        {busy ? "Starting…" : "Run workflow"}
      </Button>
      <p className="wf-help">
        Accepted runs keep going on your Mac. Text outputs are drafts for your
        review.
      </p>
    </form>
  );
}

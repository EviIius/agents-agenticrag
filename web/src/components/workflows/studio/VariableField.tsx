import { useId, useRef, useState } from "react";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { useStudio } from "./store";
import { ancestors, references, topoOrder } from "./graph";
import { outputs } from "./registry";
export function VariableField({
  nodeId,
  label,
  value,
  onChange,
  help,
  rows = 3,
  typed,
}: {
  nodeId: string;
  label: string;
  value: string;
  onChange: (v: string) => void;
  help?: string;
  rows?: number;
  typed?: string;
}) {
  const id = useId(),
    text = useRef<HTMLTextAreaElement>(null),
    highlight = useRef<HTMLDivElement>(null);
  const doc = useStudio((s) => s.draft.graph);
  const [open, setOpen] = useState(false),
    [composing, setComposing] = useState(false);
  const upstream = ancestors(doc, nodeId);
  let order: string[];
  try {
    order = topoOrder(doc).reverse();
  } catch {
    order = doc.nodes.map((n) => n.id);
  }
  const variables = order.flatMap((id) => {
    const block = doc.nodes.find((n) => n.id === id)!;
    return upstream.has(id)
      ? Object.entries(outputs(block))
          .filter(([, t]) => !typed || typed === "any" || typed === t)
          .map(([field, type]) => ({
            ref: `{{${block.key}.${field}}}`,
            title: block.title,
            type,
          }))
      : [];
  });
  const chunks = value.split(/((?<!\\)\{\{[\s\S]*?\}\})/g);
  const insert = (ref: string) => {
    const ta = text.current;
    const start = ta?.selectionStart ?? value.length,
      end = ta?.selectionEnd ?? value.length;
    const from =
      value.slice(Math.max(0, start - 2), start) === "{{" ? start - 2 : start;
    const next = typed ? ref : value.slice(0, from) + ref + value.slice(end);
    onChange(next);
    setOpen(false);
    requestAnimationFrame(() => {
      ta?.focus();
      const at = typed ? ref.length : from + ref.length;
      ta?.setSelectionRange(at, at);
    });
  };
  return (
    <div className="wf-field">
      <label htmlFor={id}>{label}</label>
      <div className="wf-variable">
        <div className="wf-highlight" aria-hidden="true" ref={highlight}>
          {chunks.map((chunk, i) => {
            if (!chunk.startsWith("{{")) return <span key={i}>{chunk}</span>;
            let valid = false;
            try {
              const r = references(chunk)[0];
              const source = doc.nodes.find((n) => n.key === r.key);
              valid = Boolean(
                source && upstream.has(source.id) && r.field in outputs(source),
              );
            } catch {
              /* Show incomplete syntax while it is being edited. */
            }
            return (
              <mark key={i} data-valid={valid}>
                {chunk}
              </mark>
            );
          })}
          {"\n"}
        </div>
        <Textarea
          id={id}
          ref={text}
          rows={rows}
          value={value}
          spellCheck={false}
          maxLength={20000}
          onCompositionStart={() => setComposing(true)}
          onCompositionEnd={() => setComposing(false)}
          onScroll={(e) => {
            if (highlight.current) {
              highlight.current.scrollTop = e.currentTarget.scrollTop;
              highlight.current.scrollLeft = e.currentTarget.scrollLeft;
            }
          }}
          onChange={(e) => {
            onChange(e.target.value);
            if (
              !composing &&
              e.target.value.slice(0, e.target.selectionStart).endsWith("{{")
            )
              setOpen(true);
          }}
        />
        <Popover open={open} onOpenChange={setOpen}>
          <PopoverTrigger asChild>
            <Button
              variant="ghost"
              className="wf-variable-button"
              aria-label={`Insert a variable in ${label}`}
            >
              {"{x}"}
            </Button>
          </PopoverTrigger>
          <PopoverContent
            className="wf-variable-picker"
            align="end"
            onOpenAutoFocus={(e) => {
              if (document.activeElement === text.current) e.preventDefault();
            }}
          >
            <p className="wf-section-title">OUTPUT FROM EARLIER BLOCKS</p>
            {variables.length ? (
              variables.map((v) => (
                <Button
                  key={v.ref}
                  variant="ghost"
                  onClick={() => insert(v.ref)}
                  className="wf-variable-option"
                >
                  <span>
                    <span className="block text-xs text-fg-3">{v.title}</span>
                    <code>{v.ref}</code>
                  </span>
                  <span className="text-xs text-fg-3">{v.type}</span>
                </Button>
              ))
            ) : (
              <p className="wf-help">
                Connect a block with an output before this one.
              </p>
            )}
          </PopoverContent>
        </Popover>
      </div>
      {help && <p className="wf-help">{help}</p>}
    </div>
  );
}

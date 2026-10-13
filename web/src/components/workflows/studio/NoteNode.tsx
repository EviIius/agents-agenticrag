import { NodeResizer, type Node, type NodeProps } from "@xyflow/react";
import { useStudio } from "./store";
import { Choice } from "./fields";
import type { Note } from "./types";
import { useContext } from "react";
import { StudioContext } from "./store";
export type NoteFlowNode = Node<{ note: Note; readonly: boolean }, "note">;
export function NoteNode({ data, selected }: NodeProps<NoteFlowNode>) {
  const edit = useStudio((s) => s.edit),
    begin = useStudio((s) => s.beginDrag),
    end = useStudio((s) => s.endDrag);
  const note = data.note;
  const store = useContext(StudioContext)!;
  const change = (patch: Partial<Note>) =>
    edit(
      (d) => ({
        ...d,
        graph: {
          ...d.graph,
          notes: d.graph.notes.map((n) =>
            n.id === note.id ? { ...n, ...patch } : n,
          ),
        },
      }),
      note.id + ":text",
    );
  return (
    <div className="wf-note" data-tone={note.tone}>
      <NodeResizer
        isVisible={selected && !data.readonly}
        minWidth={160}
        minHeight={100}
        onResizeStart={begin}
        onResizeEnd={end}
        onResize={(_, p) => {
          const s = store.getState();
          store.setState({
            draft: {
              ...s.draft,
              graph: {
                ...s.draft.graph,
                notes: s.draft.graph.notes.map((n) =>
                  n.id === note.id
                    ? {
                        ...n,
                        size: { w: p.width, h: p.height },
                        position: { x: p.x, y: p.y },
                      }
                    : n,
                ),
              },
            },
          });
        }}
      />
      <span className="wf-help">Note</span>
      <textarea
        aria-label="Note text"
        readOnly={data.readonly}
        className="nodrag nowheel"
        value={note.text}
        maxLength={4000}
        onChange={(e) => change({ text: e.target.value })}
      />
      {selected && !data.readonly && (
        <div className="nodrag nopan">
          <Choice
            label="Note tone"
            value={note.tone}
            choices={["neutral", "amber", "rose", "teal"].map((t) => ({
              value: t,
              label: t,
            }))}
            onChange={(tone) => change({ tone: tone as Note["tone"] })}
          />
        </div>
      )}
    </div>
  );
}

import { useState } from "react";
import { Input } from "@/components/ui/input";
export function ChatTitle({
  title,
  onRename,
}: {
  title: string;
  onRename: (title: string) => Promise<boolean>;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(title);
  const [saving, setSaving] = useState(false);
  return editing ? (
    <Input
      autoFocus
      aria-label="Rename chat inline"
      className="topbar-title-input"
      value={draft}
      disabled={saving}
      onChange={(event) => setDraft(event.target.value)}
      onBlur={() => {
        if (!saving) setEditing(false);
      }}
      onKeyDown={async (event) => {
        if (event.key === "Escape") {
          event.preventDefault();
          setEditing(false);
        }
        if (event.key === "Enter" && draft.trim() && !saving) {
          event.preventDefault();
          setSaving(true);
          try {
            if (await onRename(draft.trim())) setEditing(false);
          } finally {
            setSaving(false);
          }
        }
      }}
    />
  ) : (
    <span
      className="topbar-title"
      title="Double-click to rename"
      onDoubleClick={() => {
        setDraft(title);
        setEditing(true);
      }}
    >
      {title}
    </span>
  );
}

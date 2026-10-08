import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import type { Model } from "@/lib/api";
export function ModelRename({
  model,
  onSave,
}: {
  model: Model;
  onSave: (name: string | null) => Promise<boolean>;
}) {
  const [open, setOpen] = useState(false),
    [name, setName] = useState(""),
    [busy, setBusy] = useState(false);
  return (
    <>
      <Button
        variant="outline"
        aria-label={`Rename ${model.display_name}`}
        onClick={() => {
          setName(
            model.display_name === model.model_id ? "" : model.display_name,
          );
          setOpen(true);
        }}
      >
        Rename
      </Button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Rename model</DialogTitle>
            <DialogDescription>
              Leave the name empty to restore the runtime name.
            </DialogDescription>
          </DialogHeader>
          <label className="text-sm">
            Display name
            <Input
              aria-label={`Display name for ${model.model_id}`}
              maxLength={120}
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </label>
          <p className="text-xs text-fg-3 break-all">{model.model_id}</p>
          <div className="flex justify-end gap-2">
            <Button
              variant="ghost"
              disabled={busy}
              onClick={() => setOpen(false)}
            >
              Cancel
            </Button>
            <Button
              disabled={busy}
              onClick={async () => {
                setBusy(true);
                try {
                  if (await onSave(name.trim() || null)) setOpen(false);
                } finally {
                  setBusy(false);
                }
              }}
            >
              {busy ? "Saving…" : "Save name"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}

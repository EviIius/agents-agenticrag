import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { api, type Chat, type Folder } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
export type FolderAction = {
  kind: "create" | "rename" | "delete";
  folder?: Folder;
  chat?: Chat;
};
export default function FolderDialog({
  action,
  onClose,
  preview = false,
  fixture,
}: {
  action: FolderAction;
  onClose: () => void;
  preview?: boolean;
  fixture?: "busy" | "error";
}) {
  const query = useQueryClient();
  const [name, setName] = useState(action.folder?.name ?? "");
  const [busy, setBusy] = useState(fixture === "busy"),
    [error, setError] = useState(
      fixture === "error" ? "Couldn’t save the folder. Try again." : "",
    );
  const [created, setCreated] = useState<Folder>();
  const deleting = action.kind === "delete";
  const title = deleting
    ? "Delete folder?"
    : action.kind === "rename"
      ? "Rename folder"
      : "New folder";
  return (
    <Dialog
      open
      onOpenChange={(value) => {
        if (!value && !busy) onClose();
      }}
    >
      <DialogContent>
        <DialogTitle>{title}</DialogTitle>
        <DialogDescription>
          {deleting
            ? `Chats in “${action.folder?.name}” return to history. No chats are deleted.`
            : action.chat
              ? "Create a folder and move this chat into it."
              : "Organize chats in one-level folders."}
        </DialogDescription>
        <form
          className="space-y-4"
          onSubmit={async (event) => {
            event.preventDefault();
            if (busy || (!deleting && !name.trim())) return;
            if (preview) {
              onClose();
              return;
            }
            setBusy(true);
            setError("");
            try {
              if (deleting)
                await api(`/folders/${action.folder!.id}`, undefined, "DELETE");
              else if (action.kind === "rename")
                await api(
                  `/folders/${action.folder!.id}`,
                  { name: name.trim() },
                  "PATCH",
                );
              else {
                const folder =
                  created ??
                  (await api<Folder>("/folders", { name: name.trim() }));
                setCreated(folder);
                void query.invalidateQueries({ queryKey: ["folders"] });
                if (action.chat)
                  await api(
                    `/chats/${action.chat.id}`,
                    { folder_id: folder.id },
                    "PATCH",
                  );
              }
              await Promise.all([
                query.invalidateQueries({ queryKey: ["folders"] }),
                query.invalidateQueries({ queryKey: ["folder-chats"] }),
                query.invalidateQueries({ queryKey: ["chats"] }),
                query.invalidateQueries({ queryKey: ["chat"] }),
              ]);
              onClose();
            } catch (failure) {
              setError(
                failure instanceof Error
                  ? failure.message
                  : "Couldn't save the folder. Try again.",
              );
            } finally {
              setBusy(false);
            }
          }}
        >
          {!deleting && (
            <Input
              aria-label="Folder name"
              autoFocus
              maxLength={80}
              value={name}
              disabled={busy || !!created}
              onChange={(event) => setName(event.target.value)}
            />
          )}
          {error && (
            <p role="alert" className="text-sm text-danger">
              {error}
            </p>
          )}
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="outline"
              disabled={busy}
              onClick={onClose}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant={deleting ? "destructive" : "default"}
              disabled={busy || (!deleting && !name.trim())}
            >
              {busy ? "Saving…" : deleting ? "Delete folder" : "Save folder"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}

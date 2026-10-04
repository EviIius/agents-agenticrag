import { useState } from "react";
import { useOverlaySession } from "@/hooks/useOverlaySession";
import type { Chat } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogCancel,
  AlertDialogAction,
  AlertDialogFooter,
} from "@/components/ui/alert-dialog";
type ChatActionProps = {
  action: {
    chat: Chat;
    kind: "rename" | "delete" | "export-md" | "export-json";
  } | null;
  onClose: () => void;
  onApply: (title?: string) => void;
  preview?: boolean;
};
export function ChatActionDialog(props: ChatActionProps) {
  const session = useOverlaySession(
    props.action,
    `${props.action?.chat.id}:${props.action?.kind}`,
  );
  if (!session.value) return null;
  return (
    <ChatActionContent
      {...props}
      action={session.value}
      open={session.open}
      key={session.sequence}
    />
  );
}
function ChatActionContent({
  action,
  onClose,
  onApply,
  preview = false,
  open,
}: Omit<ChatActionProps, "action"> & {
  action: NonNullable<ChatActionProps["action"]>;
  open: boolean;
}) {
  const [title, setTitle] = useState(action?.chat.title ?? "");
  if (action.kind.startsWith("export-")) {
    const format = action.kind === "export-md" ? "md" : "json";
    const safeTitle = Array.from(action.chat.title, (character) =>
      character.charCodeAt(0) < 32 ||
      character.charCodeAt(0) === 127 ||
      '/\\:*?"<>|'.includes(character)
        ? "-"
        : character,
    )
      .join("")
      .replace(/^[ .]+|[ .]+$/g, "");
    const filename =
      (Array.from(safeTitle).slice(0, 120).join("") || "Untitled chat") +
      "." +
      format;
    return (
      <Dialog
        open={open}
        onOpenChange={(open) => {
          if (!open) onClose();
        }}
      >
        <DialogContent inert={!open}>
          <DialogTitle className="pr-12">
            Export {format === "md" ? "Markdown" : "JSON"}
          </DialogTitle>
          <DialogDescription>
            Download the current branch of “{action.chat.title}”. Other branches
            remain in Workbench.
          </DialogDescription>
          <p className="break-words text-sm text-fg-2">{filename}</p>
          <div className="flex flex-wrap justify-end gap-2">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button asChild>
              <a
                href={
                  "/api/chats/" + action.chat.id + "/export?format=" + format
                }
                download={filename}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(event) => {
                  if (preview) event.preventDefault();
                  setTimeout(onClose, 0);
                }}
              >
                Download
              </a>
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    );
  }
  if (action.kind === "delete")
    return (
      <AlertDialog
        open={open}
        onOpenChange={(open) => {
          if (!open) onClose();
        }}
      >
        <AlertDialogContent inert={!open}>
          <AlertDialogTitle>Delete chat?</AlertDialogTitle>
          <AlertDialogDescription>
            This removes “{action.chat.title}” and its messages.
          </AlertDialogDescription>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={() => onApply()}>
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    );
  return (
    <Dialog
      open={open}
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <DialogContent inert={!open}>
        <DialogTitle>Rename chat</DialogTitle>
        <DialogDescription>
          Choose a title for this conversation.
        </DialogDescription>
        <Input
          autoFocus
          aria-label="Chat title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && title.trim()) onApply(title.trim());
          }}
        />
        <Button disabled={!title.trim()} onClick={() => onApply(title.trim())}>
          Save title
        </Button>
      </DialogContent>
    </Dialog>
  );
}

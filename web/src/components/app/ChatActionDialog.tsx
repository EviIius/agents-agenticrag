import { FileSaveDialog } from "./FileSaveDialog";
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
    const basename =
      Array.from(safeTitle).slice(0, 120).join("") || "Untitled chat";
    return (
      <FileSaveDialog
        open={open}
        initial={format}
        onClose={onClose}
        preview={preview ? "ready" : undefined}
        title={format === "md" ? "Export Markdown" : "Export JSON"}
        closeLabel="Close chat export"
        downloadLabel="Download"
        description="Save the current branch. Choose a format before saving; other branches remain in Workbench."
        options={[
          { format: "md", label: "Markdown (.md)" },
          { format: "json", label: "JSON (.json)" },
        ].map((option) => ({
          ...option,
          url:
            "/api/chats/" + action.chat.id + "/export?format=" + option.format,
          filename: basename + "." + option.format,
        }))}
      />
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

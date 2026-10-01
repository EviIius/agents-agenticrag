import { useState } from "react";
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
export function ChatActionDialog({
  action,
  onClose,
  onApply,
}: {
  action: { chat: Chat; kind: "rename" | "delete" } | null;
  onClose: () => void;
  onApply: (title?: string) => void;
}) {
  const [title, setTitle] = useState(action?.chat.title ?? "");
  if (!action) return null;
  if (action.kind === "delete")
    return (
      <AlertDialog
        open
        onOpenChange={(open) => {
          if (!open) onClose();
        }}
      >
        <AlertDialogContent>
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
      open
      onOpenChange={(open) => {
        if (!open) onClose();
      }}
    >
      <DialogContent>
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

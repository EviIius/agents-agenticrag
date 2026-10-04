import type { Dispatch, SetStateAction } from "react";
import { Ellipsis } from "lucide-react";
import { toast } from "sonner";
import type { Chat } from "@/lib/api";
import { useUI } from "@/stores/ui";
import { IconButton } from "./IconButton";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
export type ChatAction = {
  chat: Chat;
  kind: "rename" | "delete" | "export-md" | "export-json";
};
export function ChatMenu({
  chat,
  ui,
  mutate,
  setAction,
}: {
  chat: Chat;
  ui: ReturnType<typeof useUI.getState>;
  mutate: (url: string, body: unknown, method?: string) => Promise<boolean>;
  setAction: Dispatch<SetStateAction<ChatAction | null>>;
}) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <IconButton label={`Actions for ${chat.title}`}>
          <Ellipsis />
        </IconButton>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem
          onSelect={() => {
            ui.set({ sidebar: false });
            setAction({ chat, kind: "rename" });
          }}
        >
          Rename
        </DropdownMenuItem>
        <DropdownMenuItem
          onSelect={async () => {
            if (
              await mutate(
                "/chats/" + chat.id,
                { pinned: !chat.pinned },
                "PATCH",
              )
            )
              toast.success(chat.pinned ? "Chat unpinned" : "Chat pinned", {
                description: chat.title,
              });
          }}
        >
          {chat.pinned ? "Unpin" : "Pin"}
        </DropdownMenuItem>
        {(["md", "json"] as const).map((format) => (
          <DropdownMenuItem
            key={format}
            onSelect={() => {
              ui.set({ sidebar: false });
              setAction({
                chat,
                kind: format === "md" ? "export-md" : "export-json",
              });
            }}
          >
            Export {format === "md" ? "Markdown" : "JSON"}
          </DropdownMenuItem>
        ))}
        <DropdownMenuItem
          onSelect={() => {
            ui.set({ sidebar: false });
            setAction({ chat, kind: "delete" });
          }}
        >
          Delete
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

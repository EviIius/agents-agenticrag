import type { FolderAction } from "./FolderDialog";
import type { Folder } from "@/lib/api";
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
  DropdownMenuSeparator,
  DropdownMenuSub,
  DropdownMenuSubTrigger,
  DropdownMenuSubContent,
  DropdownMenuPortal,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
export type ChatAction = {
  chat: Chat;
  kind: "rename" | "delete" | "export-md" | "export-json";
};
export function ChatMenu({
  folders = [],
  onFolderAction,
  chat,
  ui,
  mutate,
  setAction,
}: {
  folders?: Folder[];
  onFolderAction?: (action: FolderAction) => void;
  chat: Chat;
  ui: ReturnType<typeof useUI.getState>;
  mutate: (url: string, body: unknown, method?: string) => Promise<boolean>;
  setAction: Dispatch<SetStateAction<ChatAction | null>>;
}) {
  return (
    <DropdownMenu modal={false}>
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
        {onFolderAction && (
          <DropdownMenuSub>
            <DropdownMenuSubTrigger>Move to folder</DropdownMenuSubTrigger>
            <DropdownMenuPortal>
              <DropdownMenuSubContent className="max-h-72 max-w-[calc(100vw-2rem)] overflow-y-auto">
                {folders.map((folder) => (
                  <DropdownMenuItem
                    key={folder.id}
                    disabled={chat.folder_id === folder.id}
                    onSelect={() =>
                      void mutate(
                        "/chats/" + chat.id,
                        { folder_id: folder.id },
                        "PATCH",
                      )
                    }
                  >
                    {folder.name}
                  </DropdownMenuItem>
                ))}
                <DropdownMenuItem
                  onSelect={() => onFolderAction({ kind: "create", chat })}
                >
                  New folder…
                </DropdownMenuItem>
                <DropdownMenuItem
                  disabled={!chat.folder_id}
                  onSelect={() =>
                    void mutate(
                      "/chats/" + chat.id,
                      { folder_id: null },
                      "PATCH",
                    )
                  }
                >
                  Remove from folder
                </DropdownMenuItem>
              </DropdownMenuSubContent>
            </DropdownMenuPortal>
          </DropdownMenuSub>
        )}
        <DropdownMenuSeparator />
        <DropdownMenuItem
          variant="destructive"
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

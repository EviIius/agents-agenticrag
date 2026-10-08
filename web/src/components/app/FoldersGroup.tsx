import { useState, type ReactNode } from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import { ChevronRight, Ellipsis, FolderClosed, Plus } from "lucide-react";
import { api, type Chat, type Folder } from "@/lib/api";
import type { components } from "@/lib/api-types";
import { Button } from "@/components/ui/button";
import { IconButton } from "./IconButton";
import { ChatList } from "./ChatList";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";
import type { FolderAction } from "./FolderDialog";
export function FoldersGroup({
  folders,
  loading = false,
  failed = false,
  retry,
  onAction,
  menu,
  chatId,
  onOpen,
  fixture,
}: {
  folders: Folder[];
  loading?: boolean;
  failed?: boolean;
  retry: () => void;
  onAction: (action: FolderAction) => void;
  menu: (chat: Chat) => ReactNode;
  chatId?: string;
  onOpen: () => void;
  fixture?: Chat[] | "loading" | "error";
}) {
  return (
    <section aria-label="Folders">
      <div className="flex items-center justify-between pl-3">
        <h2 className="text-[11px] uppercase tracking-wide text-fg-3">
          Folders
        </h2>
        <IconButton
          label="New folder"
          onClick={() => onAction({ kind: "create" })}
        >
          <Plus />
        </IconButton>
      </div>
      {loading ? (
        <p role="status" className="p-3 text-sm text-fg-2">
          Loading folders…
        </p>
      ) : failed ? (
        <p role="alert" className="p-3 text-sm text-danger">
          Couldn't load folders.{" "}
          <Button variant="link" onClick={retry}>
            Retry folders
          </Button>
        </p>
      ) : !folders.length ? (
        <p className="px-3 pb-3 text-xs text-fg-3">No folders yet</p>
      ) : (
        folders.map((folder) => (
          <FolderRow
            key={folder.id}
            {...{ folder, onAction, menu, chatId, onOpen, fixture }}
          />
        ))
      )}
    </section>
  );
}
function FolderRow({
  folder,
  onAction,
  menu,
  chatId,
  onOpen,
  fixture,
}: {
  folder: Folder;
  onAction: (action: FolderAction) => void;
  menu: (chat: Chat) => ReactNode;
  chatId?: string;
  onOpen: () => void;
  fixture?: Chat[] | "loading" | "error";
}) {
  const [open, setOpen] = useState(false);
  const chats = useInfiniteQuery({
    queryKey: ["folder-chats", folder.id],
    initialPageParam: "",
    enabled: open && !fixture,
    queryFn: ({ pageParam }) =>
      api<components["schemas"]["ChatList"]>(
        `/chats?folder=${encodeURIComponent(folder.id)}${pageParam ? "&cursor=" + encodeURIComponent(pageParam) : ""}`,
      ),
    getNextPageParam: (last) => last.next_cursor ?? undefined,
  });
  const items = Array.isArray(fixture)
    ? fixture
    : (chats.data?.pages.flatMap((page) => page.items) ?? []);
  return (
    <Collapsible open={open} onOpenChange={setOpen}>
      <div className="flex min-h-11 items-center rounded-md hover:bg-surface-2">
        <CollapsibleTrigger asChild>
          <button
            type="button"
            aria-label={`Folder ${folder.name}, ${folder.count} chats`}
            className="flex min-h-11 min-w-0 flex-1 items-center gap-2 px-3 text-left text-sm"
          >
            <ChevronRight
              className={`size-4 shrink-0 ${open ? "rotate-90" : ""}`}
              aria-hidden
            />
            <FolderClosed className="size-4 shrink-0" aria-hidden />
            <span className="flex-1 truncate">{folder.name}</span>
            <span className="text-xs text-fg-3">{folder.count}</span>
          </button>
        </CollapsibleTrigger>
        <DropdownMenu modal={false}>
          <DropdownMenuTrigger asChild>
            <IconButton label={`Actions for folder ${folder.name}`}>
              <Ellipsis />
            </IconButton>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem
              onSelect={() => onAction({ kind: "rename", folder })}
            >
              Rename folder
            </DropdownMenuItem>
            <DropdownMenuItem
              variant="destructive"
              onSelect={() => onAction({ kind: "delete", folder })}
            >
              Delete folder
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      <CollapsibleContent className="pl-3">
        {fixture === "loading" || (!fixture && chats.isPending) ? (
          <p role="status" className="p-3 text-sm text-fg-2">
            Loading folder chats…
          </p>
        ) : fixture === "error" || (!fixture && chats.isError) ? (
          <p role="alert" className="p-3 text-sm text-danger">
            Couldn't load chats.{" "}
            <Button variant="link" onClick={() => void chats.refetch()}>
              Retry folder chats
            </Button>
          </p>
        ) : !items.length ? (
          <p className="p-3 text-xs text-fg-3">No chats in this folder</p>
        ) : (
          <ChatList
            chats={items}
            selected={chatId}
            search=""
            menu={menu}
            onOpen={onOpen}
            hasNext={!fixture && chats.hasNextPage}
            onNext={() => {
              if (!chats.isFetchingNextPage) void chats.fetchNextPage();
            }}
            grouped={false}
          />
        )}
      </CollapsibleContent>
    </Collapsible>
  );
}

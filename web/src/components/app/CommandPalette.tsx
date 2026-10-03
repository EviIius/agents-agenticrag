import { useEffect, useRef, useState } from "react";
import { useInfiniteQuery } from "@tanstack/react-query";
import {
  FileText,
  Globe,
  Keyboard,
  Moon,
  Plus,
  Settings,
  SlidersHorizontal,
  X,
  Layers,
} from "lucide-react";
import { api, type Chat } from "@/lib/api";
import type { components } from "@/lib/api-types";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  Command,
  CommandInput,
  CommandList,
  CommandGroup,
  CommandItem,
} from "@/components/ui/command";
import { IconButton } from "./IconButton";
import { Button } from "@/components/ui/button";
export type PaletteActions = {
  newChat: () => void;
  switchModel: () => void;
  toggleSearch: () => void;
  chatSettings: () => void;
  settings: () => void;
  toggleTheme: () => void;
  shortcuts: () => void;
};
export function CommandPalette({
  open,
  onOpenChange,
  actions,
  onChat,
  searchDisabled,
  previewChats,
  previewState,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  actions: PaletteActions;
  onChat: (chat: Chat) => void;
  searchDisabled?: boolean;
  previewChats?: Chat[];
  previewState?: "loading" | "error" | "empty";
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [text, setText] = useState("");
  const [query, setQuery] = useState("");
  useEffect(() => {
    if (!open) {
      setText("");
      setQuery("");
    }
  }, [open]);
  useEffect(() => {
    const timer = setTimeout(() => setQuery(text.trim()), 200);
    return () => clearTimeout(timer);
  }, [text]);
  const history = useInfiniteQuery({
    queryKey: ["palette-chats", query],
    initialPageParam: "",
    queryFn: ({ pageParam }) =>
      api<components["schemas"]["ChatList"]>(
        "/chats?q=" +
          encodeURIComponent(query) +
          (pageParam ? "&cursor=" + encodeURIComponent(pageParam) : ""),
      ),
    getNextPageParam: (last) => last.next_cursor ?? undefined,
    enabled: open && !previewChats,
    staleTime: 0,
  });
  const commands = (
    previewState === "empty"
      ? []
      : [
          { label: "New chat", icon: Plus, action: actions.newChat },
          { label: "Switch model…", icon: Layers, action: actions.switchModel },
          {
            label: "Toggle web search",
            icon: Globe,
            action: actions.toggleSearch,
            disabled: searchDisabled,
          },
          {
            label: "Chat settings",
            icon: SlidersHorizontal,
            action: actions.chatSettings,
          },
          { label: "Settings", icon: Settings, action: actions.settings },
          { label: "Toggle theme", icon: Moon, action: actions.toggleTheme },
          { label: "Shortcuts", icon: Keyboard, action: actions.shortcuts },
        ]
  ).filter((item) =>
    item.label.toLocaleLowerCase().includes(text.toLocaleLowerCase().trim()),
  );
  const chats =
    text !== query && !previewChats
      ? []
      : previewChats
        ? previewChats.filter((chat) =>
            chat.title.toLocaleLowerCase().includes(query.toLocaleLowerCase()),
          )
        : (history.data?.pages.flatMap((page) => page.items) ?? []);
  const choose = (action: () => void) => {
    onOpenChange(false);
    requestAnimationFrame(action);
  };
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        onOpenAutoFocus={(event) => {
          event.preventDefault();
          inputRef.current?.focus();
        }}
        showCloseButton={false}
        className="flex flex-col gap-0 overflow-clip p-0"
      >
        <header className="relative shrink-0 space-y-1 border-b border-line p-4 pr-16">
          <DialogTitle>Command palette</DialogTitle>
          <DialogDescription>
            Search chats or choose an action
          </DialogDescription>
          <IconButton
            label="Close command palette"
            className="absolute right-3 top-3"
            onClick={() => onOpenChange(false)}
          >
            <X />
          </IconButton>
        </header>
        <Command shouldFilter={false} className="min-h-0">
          <CommandInput
            ref={inputRef}
            aria-label="Search chats and actions"
            placeholder="Search chats and actions…"
            value={text}
            onValueChange={setText}
          />
          <CommandList className="min-h-0 max-h-[min(380px,45dvh)] p-2">
            {commands.length > 0 && (
              <CommandGroup heading="Actions">
                {commands.map(({ label, icon: Icon, action, disabled }) => (
                  <CommandItem
                    className="min-h-11"
                    key={label}
                    value={label}
                    disabled={disabled}
                    onSelect={() => choose(action)}
                  >
                    <Icon />
                    <span>{label}</span>
                  </CommandItem>
                ))}
              </CommandGroup>
            )}
            {(previewState === "loading" ||
              (!previewChats && history.isFetching)) && (
              <CommandItem
                disabled
                value="searching"
                className="p-3 text-sm text-fg-2"
              >
                Searching chats…
              </CommandItem>
            )}
            {(previewState === "error" ||
              (!previewChats && history.isError)) && (
              <CommandItem
                disabled
                value="search-error"
                className="p-3 text-sm"
              >
                Couldn't search chats.
              </CommandItem>
            )}
            {chats.length > 0 && (
              <CommandGroup heading="Chats">
                {chats.map((chat) => (
                  <CommandItem
                    className="min-h-11 items-start"
                    key={chat.id}
                    value={chat.id}
                    onSelect={() => choose(() => onChat(chat))}
                  >
                    <FileText />
                    <span className="min-w-0">
                      <span className="block truncate">{chat.title}</span>
                      {chat.snippet && (
                        <span className="block line-clamp-2 text-xs text-fg-2">
                          {chat.snippet}
                        </span>
                      )}
                    </span>
                  </CommandItem>
                ))}
              </CommandGroup>
            )}
            {!commands.length &&
              !chats.length &&
              (!previewState || previewState === "empty") &&
              (previewChats || (!history.isFetching && !history.isError)) && (
                <CommandItem
                  disabled
                  value="no-results"
                  className="justify-center p-6 text-sm text-fg-2"
                >
                  No chats or actions found
                </CommandItem>
              )}
            {history.hasNextPage && (
              <CommandItem
                className="min-h-11"
                value="more-chats"
                onSelect={() => void history.fetchNextPage()}
              >
                More chats
              </CommandItem>
            )}
          </CommandList>
        </Command>
        {(previewState === "error" || (!previewChats && history.isError)) && (
          <div role="alert" className="border-t border-line p-3 text-sm">
            <p className="sr-only">Couldn't search chats.</p>
            <Button
              variant="outline"
              onClick={() => {
                if (previewChats) return;
                void history.refetch();
              }}
            >
              Retry
            </Button>
          </div>
        )}
        {(previewState === "loading" ||
          (!previewChats && history.isFetching)) && (
          <p role="status" className="sr-only">
            Searching chats…
          </p>
        )}
      </DialogContent>
    </Dialog>
  );
}

import type { Dispatch, ReactNode, SetStateAction } from "react";
import type { Chat } from "@/lib/api";
import { useUI } from "@/stores/ui";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { ChatList } from "./ChatList";
export function HistoryList({
  folders,
  activeChats,
  search,
  setSearch,
  history,
  historyItems,
  chatId,
  menu,
  ui,
}: {
  folders?: ReactNode;
  activeChats?: string[];
  search: string;
  setSearch: Dispatch<SetStateAction<string>>;
  history: {
    isLoading: boolean;
    hasNextPage: boolean;
    isFetchingNextPage: boolean;
    fetchNextPage: () => Promise<unknown>;
  };
  historyItems: Chat[];
  chatId?: string;
  menu: (chat: Chat) => ReactNode;
  ui: ReturnType<typeof useUI.getState>;
}) {
  return (
    <>
      <div className="history-search relative mb-4">
        <Search className="pointer-events-none absolute left-3 top-3.5 size-4 text-fg-3" />
        <Input
          aria-label="Search history"
          placeholder="Search chats…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="min-h-11 border-0 bg-surface-2 pl-9 pr-12 shadow-none"
        />
        <kbd className="pointer-events-none absolute right-3 top-3.5 meta">
          ⌘K
        </kbd>
      </div>
      {!search && folders}
      {history.isLoading ? (
        <div role="status" aria-label="Loading chats" className="space-y-3 p-3">
          <div className="skeleton h-9" />
          <div className="skeleton h-9" />
          <div className="skeleton h-9" />
        </div>
      ) : historyItems.length ? (
        <ChatList
          activeChats={activeChats}
          chats={historyItems}
          selected={chatId}
          search={search}
          menu={menu}
          onOpen={() => ui.set({ sidebar: false })}
          hasNext={history.hasNextPage}
          onNext={() => {
            if (!history.isFetchingNextPage) void history.fetchNextPage();
          }}
        />
      ) : (
        <p className="p-3 text-sm text-fg-3">
          {search ? "No chats found" : "No chats yet"}
        </p>
      )}
    </>
  );
}

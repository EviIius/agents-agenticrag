import type { Dispatch, ReactNode, SetStateAction } from "react";
import type { Chat } from "@/lib/api";
import { useUI } from "@/stores/ui";
import { Input } from "@/components/ui/input";
import { ChatList } from "./ChatList";
export function HistoryList({
  activeChats,
  search,
  setSearch,
  history,
  historyItems,
  chatId,
  menu,
  ui,
}: {
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
      <Input
        aria-label="Search history"
        placeholder="Search chats…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="mb-4"
      />
      {history.isLoading ? (
        <p className="p-3 text-sm text-fg-3">Loading chats…</p>
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

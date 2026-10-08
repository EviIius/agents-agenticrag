import { useEffect, useRef, useState, type ReactNode } from "react";
import { Pin } from "lucide-react";
import { Link } from "react-router";
import type { Chat } from "@/lib/api";
function group(chat: Chat) {
  if (chat.pinned) return "Pinned";
  const now = new Date(),
    date = new Date(chat.updated_at);
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const age = Math.floor(
    (today.getTime() -
      new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime()) /
      86400000,
  );
  if (age <= 0) return "Today";
  if (age === 1) return "Yesterday";
  if (age < 7) return "Previous 7 days";
  if (age < 30) return "Previous 30 days";
  return date.toLocaleDateString(undefined, { month: "long", year: "numeric" });
}
export function ChatList({
  activeChats = [],
  chats,
  selected,
  search,
  menu,
  onOpen,
  hasNext,
  onNext,
  grouped = true,
}: {
  activeChats?: string[];
  chats: Chat[];
  selected?: string;
  search: string;
  menu: (chat: Chat) => ReactNode;
  onOpen: () => void;
  hasNext: boolean;
  onNext: () => void;
  grouped?: boolean;
}) {
  const sentinel = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!sentinel.current || !hasNext) return;
    const observer = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) onNext();
    });
    observer.observe(sentinel.current);
    return () => observer.disconnect();
  }, [hasNext, onNext]);
  let previous = "";
  return (
    <>
      {chats.map((chat) => {
        const heading = search ? "Search results" : group(chat);
        const show = heading !== previous;
        previous = heading;
        return (
          <div key={chat.id}>
            {grouped && show && (
              <p className="mt-4 px-3 py-2 text-[11px] tracking-wide text-fg-3 uppercase">
                {heading}
              </p>
            )}
            <div
              data-slot="history-row"
              data-current={selected === chat.id || undefined}
              className={`relative flex min-h-11 items-center rounded-md ${selected === chat.id ? "border-l-2 border-brand bg-surface-3" : "hover:bg-surface-2"}`}
            >
              <Link
                to={"/c/" + chat.id}
                aria-label={chat.title}
                onClick={onOpen}
                className="min-w-0 flex-1 truncate px-3 py-2 text-sm"
              >
                <ChatTitle title={chat.title} />
                {search && chat.folder_name && (
                  <span className="ml-2 text-xs text-fg-3">
                    · {chat.folder_name}
                  </span>
                )}
              </Link>
              {activeChats.includes(chat.id) && (
                <span
                  data-slot="run-dot"
                  role="img"
                  aria-label="Generating response"
                  className="size-1.5 shrink-0 rounded-full bg-brand"
                />
              )}
              {chat.pinned && (
                <Pin
                  className="size-4 shrink-0 text-brand"
                  role="img"
                  aria-label="Pinned chat"
                />
              )}
              {menu(chat)}
            </div>
          </div>
        );
      })}
      <div ref={sentinel} className="h-1" />
      {hasNext && <p className="p-3 text-xs text-fg-3">Loading more chats…</p>}
    </>
  );
}

function ChatTitle({ title }: { title: string }) {
  const [snapshot, setSnapshot] = useState({ title, fresh: false });
  if (snapshot.title !== title) setSnapshot({ title, fresh: true });
  useEffect(() => {
    if (!snapshot.fresh) return;
    const timer = setTimeout(() => setSnapshot({ title, fresh: false }), 200);
    return () => clearTimeout(timer);
  }, [title, snapshot.fresh]);
  return (
    <span data-slot="chat-title" data-fresh={snapshot.fresh || undefined}>
      {title}
    </span>
  );
}

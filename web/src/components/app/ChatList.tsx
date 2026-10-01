import { useEffect, useRef, type ReactNode } from "react";
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
  chats,
  selected,
  search,
  menu,
  onOpen,
  hasNext,
  onNext,
}: {
  chats: Chat[];
  selected?: string;
  search: string;
  menu: (chat: Chat) => ReactNode;
  onOpen: () => void;
  hasNext: boolean;
  onNext: () => void;
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
            {show && (
              <p className="mt-4 px-3 py-2 text-[11px] tracking-wide text-fg-3 uppercase">
                {heading}
              </p>
            )}
            <div
              className={`flex min-h-11 items-center rounded-md ${selected === chat.id ? "border-l-2 border-brand bg-surface-3" : "hover:bg-surface-2"}`}
            >
              <Link
                to={"/c/" + chat.id}
                title={chat.title}
                onClick={onOpen}
                className="min-w-0 flex-1 truncate px-3 py-2 text-sm"
              >
                {chat.title}
              </Link>
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

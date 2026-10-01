import {
  PanelLeftClose,
  PanelLeftOpen,
  Search,
  Settings,
  SquarePen,
  Ellipsis,
  MessageSquare,
} from "lucide-react";
import { Link } from "react-router";
import { useUI } from "@/stores/ui";
import { IconButton } from "./IconButton";
import { Button } from "@/components/ui/button";
import { fixtureTitles } from "@/design/fixtures";
import config from "../../../../shared/config.json";
export type SidebarState = "ready" | "loading" | "empty" | "search" | "error";
export function Sidebar({
  collapsed = false,
  state = "ready",
  close,
  history,
}: {
  collapsed?: boolean;
  state?: SidebarState;
  close?: () => void;
  history?: import("react").ReactNode;
}) {
  const { set } = useUI();
  return (
    <div className="flex h-full min-h-0 flex-col bg-sidebar-bg p-2">
      <header className="flex h-11 shrink-0 items-center gap-1">
        <IconButton
          label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          onClick={() => (close ? close() : set({ collapsed: !collapsed }))}
        >
          {collapsed ? <PanelLeftOpen /> : <PanelLeftClose />}
        </IconButton>
        {!collapsed && (
          <span className="min-w-0 flex-1 font-medium">{config.APP_NAME}</span>
        )}
        {!collapsed && (
          <IconButton label="New chat" asChild>
            <Link
              to={history !== undefined ? "/" : "/design/chat"}
              onClick={close}
            >
              <SquarePen />
            </Link>
          </IconButton>
        )}
      </header>
      {collapsed ? (
        <IconButton label="New chat" asChild>
          <Link to={history !== undefined ? "/" : "/design/chat"}>
            <SquarePen />
          </Link>
        </IconButton>
      ) : null}
      <Button
        variant="ghost"
        className={
          collapsed ? "icon-button" : "mb-5 h-11 justify-start gap-3 text-fg-2"
        }
        onClick={() => {
          set({ command: true });
          close?.();
        }}
        aria-label="Search chats"
      >
        <Search className="size-4" />
        {!collapsed && (
          <>
            <span className="flex-1 text-left">Search chats</span>
            <kbd className="meta">⌘K</kbd>
          </>
        )}
      </Button>
      <nav aria-label="Chat history" className="min-h-0 flex-1 overflow-y-auto">
        {!collapsed && (
          <>
            {history !== undefined ? (
              history
            ) : state === "loading" ? (
              <div
                className="space-y-3 p-2"
                role="status"
                aria-label="Loading chats"
              >
                <div className="skeleton h-9" />
                <div className="skeleton h-9" />
              </div>
            ) : state === "empty" ? (
              <p className="p-3 text-fg-2">No chats yet</p>
            ) : state === "error" ? (
              <div className="p-3 text-danger">
                Couldn’t load chats<Button variant="ghost">Retry</Button>
              </div>
            ) : (
              <>
                <p className="px-3 py-2 text-[11px] tracking-[.06em] text-fg-3">
                  {state === "search" ? "SEARCH RESULTS" : "TODAY"}
                </p>
                {fixtureTitles.map((title, index) => (
                  <div
                    key={title}
                    className={`group flex min-h-11 items-center rounded-md ${index === 0 ? "border-l-2 border-brand bg-surface-3" : "hover:bg-surface-2"}`}
                  >
                    <Link
                      to="/design/chat/fixture"
                      onClick={close}
                      className="min-w-0 flex-1 truncate px-3 py-2 text-sm"
                    >
                      {state === "search" ? (
                        <>
                          <mark className="bg-brand-soft text-fg">
                            {title.split(" ")[0]}
                          </mark>
                          {title.slice(title.indexOf(" "))}
                        </>
                      ) : (
                        title
                      )}
                    </Link>
                    <span className="px-2 text-fg-2" aria-hidden="true">
                      <Ellipsis className="size-4" />
                    </span>
                  </div>
                ))}
                <p className="mt-5 px-3 py-2 text-[11px] tracking-[.06em] text-fg-3">
                  YESTERDAY
                </p>
                <Link
                  to="/design/chat/fixture"
                  className="flex min-h-11 items-center gap-3 rounded-md px-3 hover:bg-surface-2"
                  onClick={close}
                >
                  <MessageSquare className="size-4" />A fresh perspective
                </Link>
              </>
            )}
          </>
        )}
      </nav>
      <footer className="shrink-0 border-t border-line pt-2">
        <Button
          variant="ghost"
          className={
            collapsed ? "icon-button" : "h-11 w-full justify-start gap-3"
          }
          aria-label="Settings"
          onClick={() => {
            set({ settings: true });
            close?.();
          }}
        >
          <Settings className="size-4" />
          {!collapsed && "Settings"}
        </Button>
      </footer>
    </div>
  );
}

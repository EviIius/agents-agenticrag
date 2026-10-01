import { useEffect, useRef, useState, type ReactNode } from "react";
import { useLocation, useNavigate } from "react-router";
import { ArrowDown } from "lucide-react";
import {
  Sheet,
  SheetContent,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import {
  Drawer,
  DrawerContent,
  DrawerTitle,
  DrawerDescription,
  DrawerHeader,
} from "@/components/ui/drawer";
import {
  CommandDialog,
  CommandInput,
  CommandList,
  CommandItem,
  CommandEmpty,
} from "@/components/ui/command";
import { Button } from "@/components/ui/button";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { SettingsDialog } from "@/components/settings/SettingsDialog";
import { ChatSettingsPanel } from "@/components/settings/ChatSettingsPanel";
import { Thread } from "@/components/chat/Thread";
import { Composer } from "@/components/chat/Composer";
import { useUI } from "@/stores/ui";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import { fixtureTitles } from "@/design/fixtures";
export function AppShell({ children }: { children?: ReactNode }) {
  const ui = useUI();
  const phone = useMediaQuery("(max-width: 639px)");
  const wide = useMediaQuery("(min-width: 1280px)");
  const location = useLocation();
  const navigate = useNavigate();
  const scroll = useRef<HTMLDivElement>(null);
  const empty = location.pathname === "/design/chat";
  const [message, setMessage] = useState<string | undefined>();
  const [starter, setStarter] = useState("");
  const [aboveBottom, setAboveBottom] = useState(false);
  useEffect(() => {
    const keys = (event: KeyboardEvent) => {
      if (!(event.metaKey || event.ctrlKey)) return;
      if (event.key.toLowerCase() === "k") {
        event.preventDefault();
        ui.set({ command: true });
      } else if (event.key === ",") {
        event.preventDefault();
        ui.set({ settings: true });
      } else if (event.shiftKey && event.key.toLowerCase() === "o") {
        event.preventDefault();
        navigate("/design/chat");
      }
    };
    window.addEventListener("keydown", keys);
    return () => window.removeEventListener("keydown", keys);
  }, [navigate, ui]);
  const composer = (
    <Composer
      autoFocus={Boolean(message) && !empty}
      key={starter}
      starter={starter}
      onSend={(text) => {
        setMessage(text);
        navigate("/design/chat/fixture");
        requestAnimationFrame(() =>
          document
            .querySelector<HTMLTextAreaElement>(".composer textarea")
            ?.focus(),
        );
      }}
    />
  );
  const panel = <ChatSettingsPanel />;
  return (
    <div className="app-shell">
      <aside className="sidebar-desktop" data-collapsed={ui.collapsed}>
        <Sidebar collapsed={ui.collapsed} />
      </aside>
      <main className="app-main">
        <TopBar />
        {children ? (
          <div className="thread-scroll">{children}</div>
        ) : empty ? (
          <section className="empty-chat" aria-label="New chat">
            <p className="mb-5 text-center text-xs text-fg-3">
              Foundation preview · Fake runtime
            </p>
            <h1 className="greeting">
              {new Date().getHours() < 12
                ? "Good morning"
                : new Date().getHours() < 18
                  ? "Good afternoon"
                  : "Good evening"}
              {ui.name ? `, ${ui.name}` : ""}
            </h1>
            {composer}
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              {["Explain", "Write", "Code"].map((suggestion) => (
                <Button
                  key={suggestion}
                  variant="outline"
                  className="min-h-11 rounded-full text-xs"
                  onClick={() => {
                    setStarter(`${suggestion} `);
                    setTimeout(
                      () =>
                        document
                          .querySelector<HTMLTextAreaElement>("textarea")
                          ?.focus(),
                      0,
                    );
                  }}
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          </section>
        ) : (
          <>
            <Thread
              message={message}
              scrollRef={scroll}
              onAboveBottomChange={setAboveBottom}
            />
            <div className="composer-row relative" data-testid="composer-row">
              {aboveBottom && (
                <Button
                  className="absolute -top-12 right-6 size-11 rounded-full border border-line bg-surface text-fg shadow-sm"
                  aria-label="Scroll to bottom"
                  onClick={() =>
                    scroll.current?.scrollTo({
                      top: scroll.current.scrollHeight,
                      behavior: "smooth",
                    })
                  }
                >
                  <ArrowDown className="size-4" />
                </Button>
              )}
              {composer}
              <p className="mt-2 text-center text-[11px] text-fg-3">
                Fake runtime · UI fixture · no model calls
              </p>
            </div>
          </>
        )}
      </main>
      {ui.panel && wide && <aside className="chat-panel">{panel}</aside>}
      <Sheet open={ui.sidebar} onOpenChange={(sidebar) => ui.set({ sidebar })}>
        <SheetContent
          side="left"
          className="w-[min(320px,90vw)] p-0"
          showCloseButton={false}
        >
          <SheetTitle className="sr-only">Chat history</SheetTitle>
          <SheetDescription className="sr-only">
            Fixture conversations and settings
          </SheetDescription>
          <Sidebar close={() => ui.set({ sidebar: false })} />
        </SheetContent>
      </Sheet>
      {!wide &&
        (phone ? (
          <Drawer open={ui.panel} onOpenChange={(panel) => ui.set({ panel })}>
            <DrawerContent className="overflow-y-auto">
              <DrawerHeader>
                <DrawerTitle>Chat settings</DrawerTitle>
                <DrawerDescription>
                  Fake runtime · preview controls
                </DrawerDescription>
              </DrawerHeader>
              {panel}
            </DrawerContent>
          </Drawer>
        ) : (
          <Sheet open={ui.panel} onOpenChange={(panel) => ui.set({ panel })}>
            <SheetContent
              className="overflow-y-auto p-0"
              showCloseButton={false}
            >
              <SheetTitle className="sr-only">Chat settings</SheetTitle>
              <SheetDescription className="sr-only">
                Fixture generation controls
              </SheetDescription>
              {panel}
            </SheetContent>
          </Sheet>
        ))}
      <SettingsDialog />
      <CommandDialog
        open={ui.command}
        onOpenChange={(command) => ui.set({ command })}
        title="Search chats"
        description="Find a fixture conversation"
      >
        <CommandInput placeholder="Search chats…" aria-label="Search chats" />
        <CommandList>
          <CommandEmpty>No chats found.</CommandEmpty>
          {fixtureTitles.map((title) => (
            <CommandItem
              key={title}
              onSelect={() => {
                navigate("/design/chat/fixture");
                ui.set({ command: false });
              }}
            >
              {title}
            </CommandItem>
          ))}
        </CommandList>
      </CommandDialog>
    </div>
  );
}

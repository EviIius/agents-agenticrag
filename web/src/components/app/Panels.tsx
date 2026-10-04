import type { ReactNode } from "react";
import { X } from "lucide-react";
import { useUI } from "@/stores/ui";
import { Sidebar } from "./Sidebar";
import { IconButton } from "./IconButton";
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
  DrawerHeader,
  DrawerDescription,
} from "@/components/ui/drawer";
export function Panels({
  ui,
  wide,
  phone,
  panel,
  list,
}: {
  ui: ReturnType<typeof useUI.getState>;
  wide: boolean;
  phone: boolean;
  panel: ReactNode;
  list: ReactNode;
}) {
  return (
    <>
      {ui.panel && wide && <aside className="chat-panel">{panel}</aside>}
      <Sheet open={ui.sidebar} onOpenChange={(sidebar) => ui.set({ sidebar })}>
        <SheetContent
          side="left"
          className="w-[min(320px,90vw)] p-0"
          showCloseButton={false}
        >
          <SheetTitle className="sr-only">Chat history</SheetTitle>
          <SheetDescription className="sr-only">
            Your saved conversations
          </SheetDescription>
          <Sidebar history={list} close={() => ui.set({ sidebar: false })} />
        </SheetContent>
      </Sheet>
      {!wide &&
        (phone ? (
          <Drawer open={ui.panel} onOpenChange={(panel) => ui.set({ panel })}>
            <DrawerContent className="overflow-clip">
              <DrawerHeader className="relative shrink-0 px-14">
                <IconButton
                  label="Close chat settings"
                  className="absolute right-3 top-2"
                  onClick={() => ui.set({ panel: false })}
                >
                  <X />
                </IconButton>
                <DrawerTitle>Chat settings</DrawerTitle>
                <DrawerDescription>
                  Sampling and context for this conversation
                </DrawerDescription>
              </DrawerHeader>
              <div className="min-h-0 overflow-y-auto">{panel}</div>
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
                Sampling and context
              </SheetDescription>
              {panel}
            </SheetContent>
          </Sheet>
        ))}
    </>
  );
}

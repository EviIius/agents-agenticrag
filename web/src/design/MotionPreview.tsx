import { ChatActionDialog } from "@/components/app/ChatActionDialog";
import { AudioChip } from "@/components/chat/AudioChip";
import { fakeRecording, fakeTranscript } from "./TranscriptionPreview";
import type { Chat } from "@/lib/api";
import { Button } from "@/components/ui/button";
import * as Dialog from "@/components/ui/dialog";
import * as Alert from "@/components/ui/alert-dialog";
import * as Popover from "@/components/ui/popover";
import * as Menu from "@/components/ui/dropdown-menu";
import * as Select from "@/components/ui/select";
import * as Sheet from "@/components/ui/sheet";
import * as Drawer from "@/components/ui/drawer";
import * as Tooltip from "@/components/ui/tooltip";
import { useState } from "react";
import { useUI } from "@/stores/ui";

/** Synthetic bindings to production primitives, including their real mount/exit behavior. */
const sampleRecording = {
  ...fakeRecording,
  id: "motion-fake-recording",
  filename: "fake-motion.wav",
};
const sampleTranscript = { ...fakeTranscript, attachment: sampleRecording };
export function MotionPreview() {
  const ui = useUI();
  const [tooltip, setTooltip] = useState(false);
  const [action, setAction] = useState<
    "rename" | "delete" | "export-md" | null
  >(null);
  const sampleChat: Chat = {
    id: "motion-fake-chat",
    title: "Synthetic motion chat",
    title_source: "user",
    pinned: false,
    params: {},
    web_enabled: false,
    library_enabled: false,
    research_enabled: false,
    created_at: "2026-10-04",
    updated_at: "2026-10-04",
  };
  return (
    <section className="design-card mb-8" aria-label="Motion foundation">
      <h2 className="mb-3 text-lg font-medium">Overlay motion</h2>
      <p className="mb-4 text-sm text-fg-2">
        Production primitives. Open and close each surface to inspect normal and
        reduced motion.
      </p>
      <div className="flex flex-wrap gap-3">
        <Button variant="outline" onClick={() => setAction("rename")}>
          Motion rename
        </Button>
        <Button variant="outline" onClick={() => setAction("delete")}>
          Motion delete
        </Button>
        <Button variant="outline" onClick={() => setAction("export-md")}>
          Motion export
        </Button>
        <ChatActionDialog
          preview
          action={action ? { chat: sampleChat, kind: action } : null}
          onClose={() => setAction(null)}
          onApply={() => setAction(null)}
        />
        <AudioChip fixture={sampleTranscript} attachment={sampleRecording} />
        <Button
          variant="outline"
          onClick={() =>
            ui.set({
              reduceMotion: ui.reduceMotion === "always" ? "system" : "always",
            })
          }
          aria-pressed={ui.reduceMotion === "always"}
        >
          Always reduce motion
        </Button>
        <Button variant="outline" onClick={() => ui.set({ settings: true })}>
          Motion settings
        </Button>
        <Popover.Popover>
          <Popover.PopoverTrigger asChild>
            <Button variant="outline">Motion popover</Button>
          </Popover.PopoverTrigger>
          <Popover.PopoverContent>
            <p>Synthetic popover</p>
          </Popover.PopoverContent>
        </Popover.Popover>
        <Dialog.Dialog>
          <Dialog.DialogTrigger asChild>
            <Button variant="outline">Motion dialog</Button>
          </Dialog.DialogTrigger>
          <Dialog.DialogContent>
            <Dialog.DialogTitle>Synthetic dialog</Dialog.DialogTitle>
            <Dialog.DialogDescription>
              Inspect the entrance and exit.
            </Dialog.DialogDescription>
          </Dialog.DialogContent>
        </Dialog.Dialog>
        <Alert.AlertDialog>
          <Alert.AlertDialogTrigger asChild>
            <Button variant="outline">Motion alert</Button>
          </Alert.AlertDialogTrigger>
          <Alert.AlertDialogContent>
            <Alert.AlertDialogTitle>
              Synthetic confirmation
            </Alert.AlertDialogTitle>
            <Alert.AlertDialogDescription>
              No data will be changed.
            </Alert.AlertDialogDescription>
            <Alert.AlertDialogCancel>Cancel</Alert.AlertDialogCancel>
          </Alert.AlertDialogContent>
        </Alert.AlertDialog>
        <Menu.DropdownMenu>
          <Menu.DropdownMenuTrigger asChild>
            <Button variant="outline">Motion menu</Button>
          </Menu.DropdownMenuTrigger>
          <Menu.DropdownMenuContent>
            <Menu.DropdownMenuItem>Example action</Menu.DropdownMenuItem>
            <Menu.DropdownMenuSub>
              <Menu.DropdownMenuSubTrigger>
                Example submenu
              </Menu.DropdownMenuSubTrigger>
              <Menu.DropdownMenuSubContent>
                <Menu.DropdownMenuItem>Nested action</Menu.DropdownMenuItem>
              </Menu.DropdownMenuSubContent>
            </Menu.DropdownMenuSub>
          </Menu.DropdownMenuContent>
        </Menu.DropdownMenu>
        <Select.Select defaultValue="text">
          <Select.SelectTrigger aria-label="Motion select">
            <Select.SelectValue />
          </Select.SelectTrigger>
          <Select.SelectContent>
            <Select.SelectItem value="text">Text</Select.SelectItem>
            <Select.SelectItem value="json">JSON</Select.SelectItem>
          </Select.SelectContent>
        </Select.Select>
        <Tooltip.Tooltip open={tooltip} onOpenChange={setTooltip}>
          <Tooltip.TooltipTrigger asChild>
            <Button variant="outline" onClick={() => setTooltip(!tooltip)}>
              Motion tooltip
            </Button>
          </Tooltip.TooltipTrigger>
          <Tooltip.TooltipContent>Synthetic tooltip</Tooltip.TooltipContent>
        </Tooltip.Tooltip>
        {(["left", "right", "top", "bottom"] as const).map((side) => (
          <Sheet.Sheet key={side}>
            <Sheet.SheetTrigger asChild>
              <Button variant="outline">Motion sheet {side}</Button>
            </Sheet.SheetTrigger>
            <Sheet.SheetContent side={side}>
              <Sheet.SheetTitle>Synthetic {side} sheet</Sheet.SheetTitle>
              <Sheet.SheetDescription>
                Inspect side-aware motion.
              </Sheet.SheetDescription>
            </Sheet.SheetContent>
          </Sheet.Sheet>
        ))}
        <Drawer.Drawer>
          <Drawer.DrawerTrigger asChild>
            <Button variant="outline">Motion drawer</Button>
          </Drawer.DrawerTrigger>
          <Drawer.DrawerContent>
            <Drawer.DrawerHeader>
              <Drawer.DrawerTitle>Synthetic drawer</Drawer.DrawerTitle>
              <Drawer.DrawerDescription>
                Vaul retains its drag physics.
              </Drawer.DrawerDescription>
            </Drawer.DrawerHeader>
            <Drawer.DrawerClose asChild>
              <Button variant="outline">Close motion drawer</Button>
            </Drawer.DrawerClose>
          </Drawer.DrawerContent>
        </Drawer.Drawer>
      </div>
    </section>
  );
}

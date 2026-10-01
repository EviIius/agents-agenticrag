import { useState } from "react";
import { Brain, Check, ChevronDown, Eye, LoaderCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Drawer,
  DrawerContent,
  DrawerTitle,
  DrawerDescription,
  DrawerHeader,
  DrawerClose,
} from "@/components/ui/drawer";
import { useMediaQuery } from "@/hooks/useMediaQuery";
export type PickerState =
  "ready" | "loading" | "offline" | "empty" | "loading-model";
export function ModelPicker({ state = "ready" }: { state?: PickerState }) {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState("fake-chat");
  const phone = useMediaQuery("(max-width: 639px)");
  const trigger = (
    <Button
      variant="ghost"
      className="h-11 min-w-0 max-w-full gap-2 px-2"
      aria-label="Choose model"
      onClick={() => setOpen(true)}
    >
      <span className="text-success" aria-hidden>
        ●
      </span>
      <span className="truncate font-medium">{selected}</span>
      <span className="hidden text-xs text-fg-3 sm:block">Fake runtime</span>
      <ChevronDown className="size-3 shrink-0" />
    </Button>
  );
  const content = (
    <Command>
      <CommandInput placeholder="Search models…" aria-label="Search models" />
      <CommandList className="max-h-[50dvh]">
        <CommandEmpty>No matching models.</CommandEmpty>
        <CommandGroup heading="Fake runtime · fixture connection">
          {state === "loading" ? (
            <div aria-label="Loading models" className="space-y-3 p-4">
              <div className="skeleton h-10" />
              <div className="skeleton h-10" />
            </div>
          ) : state === "empty" ? (
            <p className="p-4 text-fg-2">No models on this connection.</p>
          ) : state === "offline" ? (
            <div className="p-4 text-danger">
              Offline ·{" "}
              <Button variant="outline" onClick={() => setOpen(false)}>
                Retry
              </Button>
            </div>
          ) : (
            ["fake-chat", "fake-reasoning", "fake-vision"].map(
              (model, index) => (
                <CommandItem
                  key={model}
                  value={model}
                  onSelect={() => {
                    setSelected(model);
                    setOpen(false);
                  }}
                  className="min-h-14 gap-3"
                >
                  <span
                    className={index === 0 ? "text-success" : "text-fg-2"}
                    aria-hidden
                  >
                    {index === 0 ? "●" : "○"}
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      {model}
                      {index === 1 && (
                        <Brain
                          aria-label="Supports reasoning"
                          className="size-4"
                        />
                      )}
                      {index === 2 && (
                        <Eye aria-label="Accepts images" className="size-4" />
                      )}
                    </div>
                    <div className="meta">
                      Fixture · 16K context ·{" "}
                      {index === 0 ? "Loaded" : "Not loaded"}
                    </div>
                  </div>
                  {selected === model && <Check className="size-4" />}
                </CommandItem>
              ),
            )
          )}
          {state === "loading-model" && (
            <p className="flex items-center gap-2 p-4 text-fg-2">
              <LoaderCircle className="size-4 animate-spin" />
              Loading fake-chat… 12 s
            </p>
          )}
        </CommandGroup>
      </CommandList>
      <p className="border-t border-line p-3 text-xs text-fg-2">
        Fixture models only · connections arrive in Phase 1
      </p>
    </Command>
  );
  if (phone)
    return (
      <>
        <div className="min-w-0">{trigger}</div>
        <Drawer open={open} onOpenChange={setOpen}>
          <DrawerContent>
            <DrawerHeader>
              <DrawerTitle>Choose model</DrawerTitle>
              <DrawerDescription>Fake runtime · UI fixtures</DrawerDescription>
            </DrawerHeader>
            {content}
            <DrawerClose asChild>
              <Button variant="ghost" className="m-3">
                Close
              </Button>
            </DrawerClose>
          </DrawerContent>
        </Drawer>
      </>
    );
  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>{trigger}</PopoverTrigger>
      <PopoverContent
        align="start"
        className="w-[min(420px,calc(100vw-32px))] p-0"
      >
        {content}
      </PopoverContent>
    </Popover>
  );
}

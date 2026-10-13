import {
  Command,
  CommandEmpty,
  CommandInput,
  CommandList,
  CommandGroup,
  CommandItem,
} from "@/components/ui/command";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  Drawer,
  DrawerContent,
  DrawerTitle,
  DrawerDescription,
} from "@/components/ui/drawer";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import {
  availability,
  categories,
  registry,
  type CatalogKind,
} from "./registry";
import type { Catalog, Point } from "./types";
export function QuickAdd({
  open,
  close,
  add,
  catalog,
  anchor,
}: {
  open: boolean;
  close: () => void;
  add: (kind: CatalogKind) => void;
  catalog?: Catalog;
  anchor?: Point;
}) {
  const phone = useMediaQuery("(max-width:767px)");
  const content = (
    <Command className="wf-quick">
      <CommandInput placeholder="Search blocks" />
      <CommandList>
        <CommandEmpty>No matching blocks.</CommandEmpty>
        {categories.map((category) => (
          <CommandGroup heading={category} key={category}>
            {(Object.keys(registry) as CatalogKind[])
              .filter((k) => registry[k].category === category)
              .map((kind) => {
                const meta = registry[kind],
                  state = availability(kind, catalog);
                return (
                  <CommandItem
                    key={kind}
                    value={meta.label}
                    disabled={!state.available}
                    onSelect={() => {
                      add(kind);
                      close();
                    }}
                  >
                    <span className="wf-tile" data-cat={meta.tone}>
                      <meta.Icon />
                    </span>
                    <span>
                      <span className="block">{meta.label}</span>
                      <span className="wf-help">
                        {state.available ? meta.description : state.reason}
                      </span>
                    </span>
                  </CommandItem>
                );
              })}
          </CommandGroup>
        ))}
      </CommandList>
    </Command>
  );
  return phone ? (
    <Drawer open={open} onOpenChange={(v) => !v && close()}>
      <DrawerContent className="max-h-[85dvh] pb-safe">
        <DrawerTitle className="sr-only">Add a block</DrawerTitle>
        <DrawerDescription className="sr-only">
          Choose a block to insert in this workflow.
        </DrawerDescription>
        {content}
      </DrawerContent>
    </Drawer>
  ) : (
    <Dialog open={open} onOpenChange={(v) => !v && close()}>
      <DialogContent
        className="wf-quick-dialog"
        style={
          anchor
            ? {
                left: Math.min(Math.max(anchor.x, 176), innerWidth - 176),
                top: Math.min(Math.max(anchor.y, 240), innerHeight - 240),
              }
            : undefined
        }
      >
        <DialogTitle className="sr-only">Add a block</DialogTitle>
        <DialogDescription className="sr-only">
          Choose a block to insert in this workflow.
        </DialogDescription>
        {content}
      </DialogContent>
    </Dialog>
  );
}

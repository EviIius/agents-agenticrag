import * as React from "react";
import { ContextMenu as Primitive } from "radix-ui";
import { cn } from "@/lib/utils";
export const ContextMenu = Primitive.Root;
export const ContextMenuTrigger = Primitive.Trigger;
export function ContextMenuContent({
  className,
  ...props
}: React.ComponentProps<typeof Primitive.Content>) {
  return (
    <Primitive.Portal>
      <Primitive.Content
        data-slot="context-menu-content"
        collisionPadding={8}
        className={cn(
          "z-50 min-w-48 max-h-[min(420px,80dvh)] overflow-y-auto rounded-md border border-line bg-surface p-1 text-sm shadow-lg",
          className,
        )}
        {...props}
      />
    </Primitive.Portal>
  );
}
export function ContextMenuItem({
  className,
  ...props
}: React.ComponentProps<typeof Primitive.Item>) {
  return (
    <Primitive.Item
      data-slot="context-menu-item"
      className={cn(
        "relative flex min-h-9 cursor-default select-none items-center gap-2 rounded-sm px-2 py-1.5 outline-hidden focus:bg-surface-2 data-disabled:pointer-events-none data-disabled:opacity-50",
        className,
      )}
      {...props}
    />
  );
}
export function ContextMenuSeparator() {
  return <Primitive.Separator className="my-1 h-px bg-line" />;
}

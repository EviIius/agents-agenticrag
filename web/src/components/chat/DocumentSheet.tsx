import { useQuery } from "@tanstack/react-query";
import { X } from "lucide-react";
import { api, type Attachment } from "@/lib/api";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import { useCopyFeedback } from "@/hooks/useCopyFeedback";
import { useUI } from "@/stores/ui";
import { CopyFeedback } from "./CopyFeedback";
import { Button } from "@/components/ui/button";
import { IconButton } from "@/components/app/IconButton";
import {
  Sheet,
  SheetContent,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import {
  Drawer,
  DrawerContent,
  DrawerHeader,
  DrawerTitle,
  DrawerDescription,
} from "@/components/ui/drawer";
export default function DocumentSheet({
  attachment,
  open,
  onOpenChange,
  fixture,
}: {
  attachment: Attachment;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  fixture?: { text: string } | "loading" | "error";
}) {
  const phone = useMediaQuery("(max-width:639px)");
  const feedback = useCopyFeedback();
  const fetched = useQuery({
    queryKey: ["document-text", attachment.id],
    queryFn: () => api<{ text: string }>(`/attachments/${attachment.id}/text`),
    enabled: open && !fixture,
    staleTime: Infinity,
  });
  const data =
    typeof fixture === "object" ? fixture : fixture ? undefined : fetched.data;
  const failed = fixture === "error" || (!fixture && fetched.isError);
  const Title = phone ? DrawerTitle : SheetTitle,
    Description = phone ? DrawerDescription : SheetDescription;
  const header = (
    <div className="relative shrink-0 border-b border-line p-5 pr-16 text-left">
      <Title className="text-base">What the model received</Title>
      <Description className="break-words">
        {attachment.filename} · Extracted text only
      </Description>
      <IconButton
        label="Close document"
        className="absolute right-3 top-3"
        onClick={() => onOpenChange(false)}
      >
        <X />
      </IconButton>
    </div>
  );
  const body = (
    <>
      <div className="min-h-0 flex-1 overflow-y-auto p-5">
        {failed ? (
          <p role="alert">
            Couldn't open the document.{" "}
            <Button variant="link" onClick={() => void fetched.refetch()}>
              Retry
            </Button>
          </p>
        ) : !data ? (
          <p role="status">Opening document…</p>
        ) : (
          <pre className="whitespace-pre-wrap break-words font-sans text-sm leading-6">
            {data.text}
          </pre>
        )}
      </div>
      <footer className="flex shrink-0 gap-2 border-t border-line p-4">
        <Button
          variant="outline"
          disabled={!data}
          onClick={() => void feedback.copy(data?.text ?? "")}
        >
          <CopyFeedback {...feedback} /> Copy
        </Button>
      </footer>
    </>
  );
  const setOpen = (value: boolean) => {
    if (value && phone) useUI.getState().set({ sidebar: false, panel: false });
    onOpenChange(value);
  };
  return phone ? (
    <Drawer open={open} onOpenChange={setOpen}>
      <DrawerContent className="h-[85dvh] overflow-clip">
        <DrawerHeader className="p-0">{header}</DrawerHeader>
        {body}
      </DrawerContent>
    </Drawer>
  ) : (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetContent
        className="flex w-full flex-col gap-0 overflow-clip p-0 sm:max-w-xl"
        showCloseButton={false}
      >
        {header}
        {body}
      </SheetContent>
    </Sheet>
  );
}

import { useState } from "react";
import { Copy, Pencil } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { IconButton } from "@/components/app/IconButton";
import { toast } from "sonner";
export function UserMessage({
  text = "Explain a useful way to learn something new.",
  editing = false,
  attachment = false,
}: {
  text?: string;
  editing?: boolean;
  attachment?: boolean;
}) {
  const [edit, setEdit] = useState(editing);
  const [value, setValue] = useState(text);
  return (
    <article aria-label="Your message" className="mb-5 flex flex-col items-end">
      <h2 className="sr-only">You said</h2>
      {attachment && (
        <div className="mb-2 rounded-md border border-line bg-surface px-3 py-2 text-xs">
          notes.md · fixture attachment
        </div>
      )}
      {edit ? (
        <div className="w-full space-y-3">
          <Textarea
            aria-label="Edit message"
            value={value}
            onChange={(event) => setValue(event.target.value)}
            className="min-h-24"
          />
          <div className="flex justify-end gap-2">
            <Button
              variant="ghost"
              onClick={() => {
                setValue(text);
                setEdit(false);
              }}
            >
              Cancel
            </Button>
            <Button onClick={() => setEdit(false)}>Send</Button>
          </div>
        </div>
      ) : (
        <>
          <div className="max-w-[85%] rounded-[var(--radius-lg)] bg-user-bubble px-3.5 py-2.5 text-[15px] leading-[23px] break-words">
            {value}
          </div>
          <div className="mt-1 flex">
            <IconButton
              label="Copy message"
              onClick={() => {
                void navigator.clipboard
                  .writeText(value)
                  .then(() => toast("Copied"));
              }}
            >
              <Copy />
            </IconButton>
            <IconButton label="Edit message" onClick={() => setEdit(true)}>
              <Pencil />
            </IconButton>
          </div>
        </>
      )}
    </article>
  );
}

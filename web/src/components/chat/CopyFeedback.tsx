import { Check } from "lucide-react";
export function CopyFeedback({
  copied,
  failed,
}: {
  copied: boolean;
  failed?: boolean;
}) {
  return (
    <>
      {copied && (
        <Check data-slot="copy-check" aria-hidden="true" className="size-4" />
      )}
      <span role="status" aria-live="polite" className="sr-only">
        {failed ? "Couldn't copy. Try again." : copied ? "Copied" : ""}
      </span>
    </>
  );
}

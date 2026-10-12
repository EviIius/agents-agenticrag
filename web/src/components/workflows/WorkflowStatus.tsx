import { Button } from "@/components/ui/button";

export function WorkflowStatus({
  connection,
  notice,
  retry,
}: {
  connection: string;
  notice?: string;
  retry: () => void;
}) {
  return (
    <>
      <p role="status" className="mb-4 text-xs text-fg-3">
        {connection}
      </p>
      {notice && (
        <div
          role="status"
          className="mb-4 flex flex-wrap items-center gap-3 text-fg-2"
        >
          {notice}
          <Button variant="outline" onClick={retry}>
            Try again
          </Button>
        </div>
      )}
    </>
  );
}

export function WorkflowRunUnavailable({ failed }: { failed: boolean }) {
  return (
    <p role="status" className="text-fg-2">
      {failed ? "Run unavailable" : "Loading run…"}
    </p>
  );
}

import config from "../../../../shared/config.json";
import { Button } from "@/components/ui/button";
export function OfflineNotice({
  detail,
  onRetry,
}: {
  detail: string;
  onRetry: () => void;
}) {
  return (
    <div role="alert" className="m-auto max-w-md p-6">
      <h1 className="text-lg font-medium">Can't reach {config.APP_NAME}</h1>
      <p className="my-4 text-sm text-fg-2">
        Your Mac may be asleep or off the tailnet.
      </p>
      <details className="mb-4 text-xs text-fg-3">
        <summary className="min-h-11 cursor-pointer py-3">Details</summary>
        {detail}
      </details>
      <Button onClick={onRetry}>Try again</Button>
    </div>
  );
}

import { Button } from "@/components/ui/button";
import type { components } from "@/lib/api-types";
import config from "../../../../shared/config.json";
type Detection = components["schemas"]["Detection"];
export function Welcome({
  detections,
  error,
  onAdd,
  onRetry,
  onSettings,
}: {
  detections?: Detection[];
  error?: boolean;
  onAdd: (baseUrl: string) => void;
  onRetry: () => void;
  onSettings: () => void;
}) {
  return (
    <section className="empty-chat">
      <h1 className="greeting">Welcome to {config.APP_NAME}</h1>
      <p className="my-4 text-center text-sm text-fg-2">
        Connect the local models on your Mac.
      </p>
      {!detections && !error && (
        <p role="status" className="text-center text-sm text-fg-3">
          Looking for Ollama…
        </p>
      )}
      {detections
        ?.filter((d) => d.reachable)
        .map((d) => (
          <div
            key={d.base_url}
            className="my-4 flex max-w-full flex-wrap items-center gap-4 rounded-xl border border-line bg-surface p-4"
          >
            <div className="min-w-0 flex-1">
              <p>Ollama</p>
              <p className="meta break-all">
                {d.model_count} models · {d.base_url}
              </p>
            </div>
            <Button onClick={() => onAdd(d.base_url)}>Add all</Button>
          </div>
        ))}
      {(error || detections?.every((d) => !d.reachable)) && (
        <>
          <p className="text-sm text-fg-2">Start Ollama on your Mac:</p>
          <code className="my-3 block">ollama serve</code>
          <Button variant="outline" onClick={onRetry}>
            Try again
          </Button>
        </>
      )}
      <Button variant="ghost" className="mt-4" onClick={onSettings}>
        Configure a connection
      </Button>
    </section>
  );
}

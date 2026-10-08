import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, type BackupStatus } from "@/lib/api";
import { Button } from "@/components/ui/button";
export function BackupPane({
  fixture,
}: {
  fixture?: BackupStatus | "loading" | "error" | "busy";
}) {
  const fetched = useQuery({
    queryKey: ["backup"],
    queryFn: () => api<BackupStatus>("/backup"),
    enabled: !fixture,
    retry: false,
  });
  const [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  const data = typeof fixture === "object" ? fixture : fetched.data;
  const pending = busy || fixture === "busy";
  return (
    <section aria-label="Database backups" className="space-y-3">
      <h3 className="font-medium">Automatic backups</h3>
      {data ? (
        <p className="text-sm text-fg-2">
          Last backup:{" "}
          {data.last_at
            ? new Date(data.last_at).toLocaleString([], {
                dateStyle: "short",
                timeStyle: "short",
              })
            : "not yet"}{" "}
          · {data.count} kept · {(data.bytes / 1024 ** 2).toFixed(1)} MB
        </p>
      ) : fetched.isError || fixture === "error" ? (
        <p role="alert" className="text-sm text-danger">
          Couldn't load backup status.{" "}
          <Button variant="link" onClick={() => void fetched.refetch()}>
            Retry backup status
          </Button>
        </p>
      ) : (
        <p role="status" className="text-sm text-fg-2">
          Loading backup status…
        </p>
      )}
      {(data?.warning || error) && (
        <p role="alert" className="text-sm text-warning">
          {error || data?.warning}
        </p>
      )}
      <p className="text-sm text-fg-2">
        Daily at 03:30 on your Mac; seven copies kept. Attachment files are not
        included; restore instructions are in the README on your Mac.
      </p>
      <Button
        variant="outline"
        disabled={pending}
        onClick={async () => {
          if (fixture) return;
          setBusy(true);
          setError("");
          try {
            const result = await api<BackupStatus>("/backup", {});
            await fetched.refetch();
            if (result.warning) setError(result.warning);
          } catch (failure) {
            setError(
              failure instanceof Error
                ? failure.message
                : "Couldn't make a backup. Try again.",
            );
          } finally {
            setBusy(false);
          }
        }}
      >
        {pending ? "Backing up…" : "Back up now"}
      </Button>
    </section>
  );
}

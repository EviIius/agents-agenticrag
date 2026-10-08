import config from "../../../../shared/config.json";
import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api } from "@/lib/api";
import type { components } from "@/lib/api-types";
import { Button } from "@/components/ui/button";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogCancel,
} from "@/components/ui/alert-dialog";
export type ImportPreview =
  "ready" | "loading" | "missing" | "status-error" | "importing" | "failed";
export function LegacyImportDialog({ preview }: { preview?: ImportPreview }) {
  const query = useQueryClient();
  const [open, setOpen] = useState(false),
    [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  const status = useQuery({
    queryKey: ["legacy-status"],
    queryFn: () =>
      api<components["schemas"]["LegacyStatus"]>("/chats/legacy-import"),
    enabled: !preview,
  });
  const available = preview
    ? ["ready", "importing", "failed"].includes(preview)
    : status.data?.available;
  const isBusy = busy || preview === "importing";
  const statusError =
    preview === "status-error" || (!preview && status.isError);
  const loading = preview === "loading" || (!preview && status.isLoading);
  const visibleError =
    error ||
    (preview === "failed"
      ? "Couldn't import the old chats. Existing chats were kept. You can retry."
      : "");
  const run = async () => {
    if (preview) {
      toast("Synthetic import · no data changed");
      setOpen(false);
      return;
    }
    setBusy(true);
    setError("");
    try {
      const result = await api<components["schemas"]["LegacyImport"]>(
        "/chats/legacy-import",
        {},
      );
      toast.success(`Imported ${result.imported} chats`, {
        description: `${result.skipped} already imported`,
      });
      void query.invalidateQueries({ queryKey: ["chats"] });
      void query.invalidateQueries({ queryKey: ["palette-chats"] });
      setOpen(false);
    } catch {
      setError(
        "Couldn't import the old chats. Existing chats were kept. You can retry.",
      );
    } finally {
      setBusy(false);
    }
  };
  return (
    <div className="space-y-2">
      <Button
        variant="outline"
        disabled={!available}
        onClick={() => {
          setOpen(true);
          setError("");
        }}
      >
        Import old chats
      </Button>
      <p className="text-sm text-fg-2">
        {available
          ? "Copy chats from Chat & Web 0.5. Your old database stays unchanged."
          : statusError
            ? "Couldn't check the old database."
            : loading
              ? "Checking for old chats…"
              : "No Chat & Web 0.5 database was found on this Mac."}
      </p>
      {statusError && (
        <Button
          variant="outline"
          onClick={() => {
            if (preview) toast("Synthetic retry · no data changed");
            else void status.refetch();
          }}
        >
          Retry
        </Button>
      )}
      <AlertDialog open={open} onOpenChange={setOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Import old chats?</AlertDialogTitle>
            <AlertDialogDescription>
              Copy titles and messages into {config.APP_NAME} with an Imported
              label. Previously imported chats are skipped. The old database
              stays unchanged.
            </AlertDialogDescription>
          </AlertDialogHeader>
          {visibleError && (
            <p role="alert" className="text-sm text-danger">
              {visibleError}
            </p>
          )}
          {isBusy && (
            <p role="status" className="text-sm text-fg-2">
              Importing chats…
            </p>
          )}
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isBusy}>Cancel</AlertDialogCancel>
            <Button disabled={isBusy} onClick={() => void run()}>
              {isBusy ? "Importing…" : "Import chats"}
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

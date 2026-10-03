import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api, type Bootstrap, type TranscriptionStatus } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogHeader,
  AlertDialogFooter,
  AlertDialogCancel,
  AlertDialogAction,
} from "@/components/ui/alert-dialog";
import { Switch } from "@/components/ui/switch";
export function TranscriptionSettings({
  bootstrap,
  fixture,
  fixtureClearState,
}: {
  bootstrap?: Bootstrap;
  fixture?: TranscriptionStatus;
  fixtureClearState?: "removing" | "failed";
}) {
  const query = useQueryClient();
  const [clearOpen, setClearOpen] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [clearError, setClearError] = useState("");
  const isClearing = clearing || fixtureClearState === "removing";
  const visibleClearError =
    clearError ||
    (fixtureClearState === "failed"
      ? "Couldn’t remove stored audio. Try again."
      : "");
  const storage = useQuery({
    queryKey: ["audio-storage"],
    queryFn: () =>
      api<{ files: number; bytes: number; active_files: number }>(
        "/transcription/audio-storage",
      ),
    enabled: !fixture,
  });
  const clearAudio = async () => {
    setClearing(true);
    setClearError("");
    try {
      const result = await api<{ files: number }>(
        "/transcription/audio-storage",
        undefined,
        "DELETE",
      );
      toast.success(
        `${result.files} audio ${result.files === 1 ? "file removed" : "files removed"}. Transcripts kept.`,
      );
      setClearOpen(false);
      // Refresh attachment projections and finished SSE snapshots without polling.
      window.dispatchEvent(new Event("workbench:audio-cleared"));
      await Promise.all([
        query.invalidateQueries({ queryKey: ["audio-storage"] }),
        query.invalidateQueries({ queryKey: ["pending-recordings"] }),
        query.invalidateQueries({ queryKey: ["chat"] }),
      ]);
    } catch {
      setClearError("Couldn't remove stored audio. Try again.");
    } finally {
      setClearing(false);
    }
  };
  const status = useQuery({
    queryKey: ["transcription-status"],
    queryFn: () => api<TranscriptionStatus>("/transcription/status"),
    enabled: !fixture,
  });
  const data = fixture ?? status.data;
  return (
    <>
      <p className="text-sm">
        <span
          className={data?.ready ? "text-success" : "text-fg-3"}
          aria-hidden
        >
          {data?.ready ? "●" : "○"}
        </span>{" "}
        {data?.ready
          ? "Ready"
          : status.isLoading && !fixture
            ? "Checking setup…"
            : "Not set up"}
        {data?.version ? ` · ${data.version}` : ""}
      </p>
      <ul className="space-y-3 text-xs text-fg-2">
        {data?.checks?.map((check) => (
          <li key={check.name} className="break-words">
            <span className="font-medium">
              {check.name}: {check.ok ? "OK" : "Needs attention"}
            </span>
            {check.detail && <p>{check.detail}</p>}
          </li>
        ))}
      </ul>
      {data && !data.configured && (
        <p className="break-words text-sm text-fg-2">
          Set <code>WORKBENCH_TRANSCRIBE_HOME</code> to the transcription engine
          folder on your Mac, then restart Workbench.
        </p>
      )}
      {status.isError && !fixture && (
        <p role="alert">Couldn't check the transcription engine.</p>
      )}
      {!fixture && (
        <Button
          variant="outline"
          disabled={status.isFetching}
          onClick={() => {
            void api<TranscriptionStatus>(
              "/transcription/status?refresh=true",
            ).then(
              (value) => {
                query.setQueryData(["transcription-status"], value);
                void query.invalidateQueries({ queryKey: ["bootstrap"] });
              },
              (error) => toast.error(String(error)),
            );
          }}
        >
          Check setup
        </Button>
      )}
      <label className="flex items-start gap-3 text-sm">
        <Switch
          aria-label="Keep web search off in chats with a recording"
          checked={bootstrap?.settings["transcription.block_web"] !== false}
          onCheckedChange={(value) => {
            if (fixture) return;
            void api(
              "/settings",
              { "transcription.block_web": value },
              "PATCH",
            ).then(
              () => query.invalidateQueries({ queryKey: ["bootstrap"] }),
              (error) => toast.error(String(error)),
            );
          }}
        />
        <span>Keep web search off in chats with a recording</span>
      </label>
      <label className="flex items-start gap-3 text-sm">
        <Switch
          aria-label="Keep original audio after transcription"
          checked={bootstrap?.settings["transcription.keep_audio"] === true}
          onCheckedChange={(value) => {
            if (fixture) return;
            void api(
              "/settings",
              { "transcription.keep_audio": value },
              "PATCH",
            ).then(
              () => query.invalidateQueries({ queryKey: ["bootstrap"] }),
              () => toast.error("Couldn't save audio storage preference."),
            );
          }}
        />
        <span>Keep original audio after transcription</span>
      </label>
      <p className="text-xs text-fg-2">
        Off by default: audio is removed after the transcript is saved. Text,
        timestamps and JSON outputs stay available. Failed recordings are kept
        for Retry. To transcribe again after removal, upload the original again.
      </p>
      <div className="space-y-3 rounded-lg border border-line p-3">
        <h3 className="text-sm font-medium">Stored audio</h3>
        <p className="text-xs text-fg-2">
          {fixture
            ? "2 audio files · 128 MB"
            : storage.data
              ? `${storage.data.files} audio files · ${(storage.data.bytes / 1024 ** 2).toLocaleString(undefined, { maximumFractionDigits: 1 })} MB`
              : storage.isError
                ? "Couldn't check stored audio."
                : "Checking stored audio…"}
        </p>
        <Button
          variant="outline"
          disabled={
            !fixture &&
            (!storage.data || storage.data.files <= storage.data.active_files)
          }
          onClick={() => {
            setClearError("");
            setClearOpen(true);
          }}
        >
          Clear stored audio
        </Button>
        <p className="text-xs text-fg-3">
          Keeps all transcripts and chats. Audio currently being transcribed is
          skipped. Your original files on your phone or computer are unaffected.
        </p>
      </div>
      <AlertDialog
        open={clearOpen}
        onOpenChange={(open) => {
          if (!isClearing) setClearOpen(open);
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Clear stored audio?</AlertDialogTitle>
            <AlertDialogDescription>
              Permanently remove Workbench’s uploaded audio copies to free
              space. Transcripts, timestamps, JSON outputs and chats stay saved.
              Re-upload an original to transcribe again. Active jobs are
              skipped.
            </AlertDialogDescription>
          </AlertDialogHeader>
          {visibleClearError && (
            <p role="alert" className="text-sm text-danger">
              {visibleClearError}
            </p>
          )}
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isClearing}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              disabled={isClearing}
              onClick={(event) => {
                event.preventDefault();
                if (fixture) setClearOpen(false);
                else void clearAudio();
              }}
            >
              {isClearing ? "Removing…" : "Remove audio copies"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
      <p className="text-xs text-fg-3">
        Transcription stays on your Mac. Transcripts use your local Ollama
        model.
      </p>
    </>
  );
}

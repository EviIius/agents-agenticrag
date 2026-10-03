import { useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api, type Bootstrap, type TranscriptionStatus } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
export function TranscriptionSettings({
  bootstrap,
  fixture,
}: {
  bootstrap?: Bootstrap;
  fixture?: TranscriptionStatus;
}) {
  const query = useQueryClient();
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
      <p className="text-xs text-fg-3">
        Recordings stay on your Mac. Transcripts use your local Ollama model.
      </p>
    </>
  );
}

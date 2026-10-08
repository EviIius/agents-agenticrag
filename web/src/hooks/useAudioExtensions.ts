import { useQuery } from "@tanstack/react-query";
import { api, type TranscriptionStatus } from "@/lib/api";

/** File routing and the picker share the engine's reported extension list. */
export const transcriptionStatusQuery = {
  queryKey: ["transcription-status"],
  queryFn: () => api<TranscriptionStatus>("/transcription/status"),
};
export function useAudioExtensions(enabled: boolean) {
  const status = useQuery({ ...transcriptionStatusQuery, enabled });
  return status.data?.audio_extensions ?? [];
}

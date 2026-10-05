import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { api, type Attachment, type Model } from "@/lib/api";
import { attachTranscription, detachTranscription } from "@/lib/sse";
import { failureCopy, failureDetail } from "@/lib/errors";
export function useCleanup(item: Attachment, model?: Model, preview = false) {
  const query = useQueryClient();
  const [busy, setBusy] = useState(false);
  const refresh = async (next: Attachment) => {
    detachTranscription(item.id);
    attachTranscription(next);
    await Promise.all([
      query.invalidateQueries({ queryKey: ["transcript", item.id] }),
      query.invalidateQueries({ queryKey: ["chat"] }),
      query.invalidateQueries({ queryKey: ["pending-recordings"] }),
    ]);
  };
  const action = async (kind: "start" | "discard" | "cancel") => {
    if (preview || busy || (kind === "start" && !model)) return;
    setBusy(true);
    try {
      if (kind === "start") {
        const next = await api<Attachment>(`/attachments/${item.id}/cleanup`, {
          connection_id: model!.connection_id,
          model_id: model!.model_id,
        });
        await refresh(next);
      } else {
        await api(
          `/attachments/${item.id}/${kind === "discard" ? "cleanup" : "cancel"}`,
          kind === "discard" ? undefined : {},
          kind === "discard" ? "DELETE" : "POST",
        );
        await refresh(await api<Attachment>(`/attachments/${item.id}/info`));
      }
    } catch (error) {
      toast.error(failureCopy(error), { description: failureDetail(error) });
    } finally {
      setBusy(false);
    }
  };
  return {
    busy,
    start: () => void action("start"),
    discard: () => void action("discard"),
    cancel: () => void action("cancel"),
  };
}

import { useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { components } from "@/lib/api-types";

export function useLibraryIndex(enabled: boolean) {
  const query = useQueryClient();
  const index = useQuery({
    queryKey: ["library", "composer"],
    queryFn: () => api<components["schemas"]["LibraryIndex"]>("/library"),
    enabled,
  });
  useEffect(() => {
    if (!enabled || !index.data) return;
    const source = new EventSource(
      `/api/library/events?after=${index.data.event_id}`,
    );
    let frame = 0;
    const refresh = () => {
      if (!frame)
        frame = requestAnimationFrame(() => {
          frame = 0;
          void query.invalidateQueries({ queryKey: ["library", "composer"] });
        });
    };
    for (const type of [
      "library.changed",
      "document.queued",
      "document.extracting",
      "document.embedding",
      "document.ready",
      "document.failed",
    ])
      source.addEventListener(type, refresh);
    return () => {
      source.close();
      if (frame) cancelAnimationFrame(frame);
    };
    // Keep the initial cursor; EventSource resumes via Last-Event-ID.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [enabled, !!index.data, query]);
  return index;
}

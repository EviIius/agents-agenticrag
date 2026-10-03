import { create } from "zustand";
import type { Attachment } from "@/lib/api";
export const useTranscripts = create<{
  attachments: Record<string, Attachment>;
  put: (attachment: Attachment) => void;
  remove: (id: string) => void;
}>((set) => ({
  attachments: {},
  put: (attachment) =>
    set((state) => ({
      attachments: { ...state.attachments, [attachment.id]: attachment },
    })),
  remove: (id) =>
    set((state) => {
      const attachments = { ...state.attachments };
      delete attachments[id];
      return { attachments };
    }),
}));

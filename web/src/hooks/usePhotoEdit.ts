import { useMemo } from "react";
import { create } from "zustand";
import { api, ApiError, type Chat, type Model } from "@/lib/api";
import type { components } from "@/lib/api-types";
import type { ImageJob } from "@/lib/image-events";
import { uploadPhoto } from "@/lib/photo-upload";

export type PhotoReference = components["schemas"]["ImageReference"];
export type PhotoDraft = {
  active: boolean;
  text: string;
  version: number;
  input?: {
    token: string;
    phase: "preparing" | "ready" | "error" | "unavailable";
    preview?: string;
    file?: File;
    job?: ImageJob;
    reference?: PhotoReference;
    error?: string;
  };
};
export type PhotoSubmission = {
  reference: PhotoReference;
  accepted: (chat: string, adopt: boolean) => void;
  rejected: (code?: string) => void;
};
const empty: PhotoDraft = { active: false, text: "", version: 0 };
export const usePhotoDrafts = create<{ entries: Record<string, PhotoDraft> }>(
  () => ({ entries: {} }),
);
const uploads = new Map<string, AbortController>();
const chats = new Map<string, Promise<Chat>>();
function uploadOwner(token: string) {
  return Object.entries(usePhotoDrafts.getState().entries).find(
    ([, draft]) => draft.input?.token === token,
  )?.[0];
}
function read(key: string) {
  return usePhotoDrafts.getState().entries[key] ?? empty;
}
function write(key: string, patch: Partial<PhotoDraft>, advance = true) {
  usePhotoDrafts.setState((state) => ({
    entries: {
      ...state.entries,
      [key]: {
        ...read(key),
        ...patch,
        version: read(key).version + Number(advance),
      },
    },
  }));
}
function revoke(url?: string) {
  if (url?.startsWith("blob:")) URL.revokeObjectURL(url);
}
export function clearPhotoInputs() {
  for (const [key, draft] of Object.entries(usePhotoDrafts.getState().entries))
    if (draft.input?.reference)
      write(key, {
        input: {
          ...draft.input,
          phase: "unavailable",
          reference: {
            ...draft.input.reference,
            available: false,
          },
        },
      });
}
export function photoSubmission(key: string): PhotoSubmission | undefined {
  const draft = read(key),
    reference = draft.input?.reference;
  if (!reference?.available || draft.input?.phase !== "ready") return;
  return {
    reference,
    accepted(chat, adopt) {
      const current = read(key);
      if (current.version === draft.version) {
        revoke(current.input?.preview);
        write(key, { text: "", input: undefined });
      }
      if (adopt && key === "new") {
        usePhotoDrafts.setState((state) => {
          const entries = { ...state.entries, [chat]: read(key) };
          delete entries[key];
          return { entries };
        });
        chats.delete(key);
      }
    },
    rejected(code) {
      if (
        code === "reference_unavailable" &&
        read(key).input?.reference?.id === reference.id &&
        read(key).input?.token === draft.input?.token
      )
        write(key, { input: { ...read(key).input!, phase: "unavailable" } });
    },
  };
}

export function usePhotoEdit(key: string, model?: Model) {
  const draft = usePhotoDrafts((state) => state.entries[key] ?? empty);
  return useMemo(() => {
    const owner = async () => {
      if (key !== "new") return key;
      let pending = chats.get(key);
      if (!pending) {
        pending = api<Chat>(
          "/chats",
          model
            ? {
                connection_id: model.connection_id,
                model_id: model.model_id,
              }
            : {},
        );
        chats.set(key, pending);
        void pending.catch(() => {
          if (chats.get(key) === pending) chats.delete(key);
        });
      }
      return (await pending).id;
    };
    const remove = () => {
      const token = read(key).input?.token;
      if (token) {
        uploads.get(token)?.abort();
        uploads.delete(token);
      }
      revoke(read(key).input?.preview);
      write(key, { input: undefined });
    };
    const attach = async (source: File | ImageJob) => {
      remove();
      const token = crypto.randomUUID(),
        controller = new AbortController();
      const input: NonNullable<PhotoDraft["input"]> = {
        token,
        phase: "preparing",
        ...(source instanceof File
          ? { file: source, preview: URL.createObjectURL(source) }
          : {
              job: source,
              preview: `/api/images/jobs/${source.id}/output/png`,
            }),
      };
      uploads.set(token, controller);
      write(key, { active: true, input });
      try {
        if (
          source instanceof File &&
          (!source.size || source.size > 20 * 1024 ** 2)
        )
          throw new Error("Choose a PNG, JPEG or HEIC photo up to 20 MB.");
        const chat = await owner();
        if (controller.signal.aborted) return;
        const response =
          source instanceof File
            ? await uploadPhoto(chat, source, controller.signal)
            : await fetch(`/api/chats/${chat}/image-references/from-job`, {
                method: "POST",
                signal: controller.signal,
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ source_job_id: source.id }),
              });
        if (!response.ok) {
          const body = await response.json().catch(() => ({}));
          throw new ApiError(
            body.error?.code ?? "http_error",
            body.error?.message ?? "Couldn't prepare this photo. Try again.",
          );
        }
        const reference: PhotoReference = await response.json();
        const destination = uploadOwner(token);
        if (destination)
          write(destination, {
            input: { ...input, phase: "ready", reference },
          });
      } catch (error) {
        const destination = uploadOwner(token);
        if (!controller.signal.aborted && destination)
          write(destination, {
            input: {
              ...input,
              phase: "error",
              error:
                error instanceof Error
                  ? error.message
                  : "Photo upload failed. Try again.",
            },
          });
      } finally {
        if (uploads.get(token) === controller) uploads.delete(token);
      }
    };
    return {
      key,
      draft,
      attach,
      setText: (text: string) => write(key, { text }),
      setActive: (active: boolean) => write(key, { active }),
      remove,
      retry: () => {
        const input = read(key).input;
        if (input?.file || input?.job) void attach(input.file ?? input.job!);
      },
      submission: () => photoSubmission(key),
      previewLoaded: () => {
        const input = read(key).input;
        if (input?.phase === "ready" && input.preview?.startsWith("blob:")) {
          revoke(input.preview);
          write(key, { input: { ...input, preview: undefined } }, false);
        }
      },
    };
  }, [key, model, draft]);
}
export type PhotoEditor = ReturnType<typeof usePhotoEdit> & {
  previewURL?: string;
};

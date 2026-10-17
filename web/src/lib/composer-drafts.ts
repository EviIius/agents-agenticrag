export const drafts = new Map<string, string>();
export const imageDrafts = new Map<string, string>();

const listeners = new Map<string, Set<() => void>>();
const owners = new Map<string, object>();
export function subscribeDraft(key: string, listener: () => void) {
  const group = listeners.get(key) ?? new Set<() => void>();
  listeners.set(key, group);
  group.add(listener);
  return () => {
    group.delete(listener);
    if (!group.size) listeners.delete(key);
  };
}
function publishDraft(key: string) {
  for (const listener of listeners.get(key) ?? []) listener();
}
export function writeDraft(key: string, text: string) {
  drafts.set(key, text);
  publishDraft(key);
}
export function editDraft(key: string) {
  // Even an intentional edit back to empty supersedes an in-flight send.
  owners.delete(key);
}
export function beginDraftSend(key: string, text: string, optimistic: boolean) {
  const token = {};
  owners.set(key, token);
  if (optimistic) writeDraft(key, "");
  return { key, text, optimistic, token };
}
export function finishDraftSend(
  send: ReturnType<typeof beginDraftSend>,
  accepted: boolean,
) {
  if (
    owners.get(send.key) !== send.token ||
    drafts.get(send.key) !== (send.optimistic ? "" : send.text)
  )
    return;
  owners.delete(send.key);
  if (accepted) drafts.delete(send.key);
  else drafts.set(send.key, send.text);
  publishDraft(send.key);
}

export type ImageRefinement = {
  job: import("@/lib/image-events").ImageJob;
  position: number;
};
export type ImageComposerCommand = {
  key: string;
  mode: "image" | "chat";
  refinement?: ImageRefinement;
};
export const imageRefinements = new Map<string, ImageRefinement>();

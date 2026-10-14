export const drafts = new Map<string, string>();
export const imageDrafts = new Map<string, string>();

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

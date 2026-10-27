import { useState } from "react";
import { ImagePlus } from "lucide-react";
import type { ImageJob } from "@/lib/image-events";
import { ImageViewer } from "./ImageViewer";

export default function ImagePrompt({
  jobs,
  preview = false,
}: {
  jobs: ImageJob[];
  preview?: boolean;
}) {
  const [frame, setFrame] = useState<HTMLElement>();
  const [broken, setBroken] = useState(false);
  const job = jobs[0],
    edit = job?.mode === "edit";
  const available = edit && job.reference?.available && !broken;
  const photo = {
    id: job?.reference?.id ?? "unavailable",
    prompt: "Photo reference · normalized input",
    url: preview
      ? "/icons/apple-touch-icon.png"
      : `/api/images/jobs/${job?.id}/reference`,
  };
  return (
    <div className="mb-2 text-xs text-fg-2" data-slot="image-prompt-source">
      <p className="flex items-center gap-1">
        <ImagePlus className="size-3" />
        {edit
          ? "Edit photo · Photo reference"
          : job
            ? "Create image"
            : "Image request · Source not recorded"}
        {jobs.length > 1 ? ` · ${jobs.length} images` : ""}
      </p>
      {available && (
        <button
          type="button"
          className="mt-2 block size-20 overflow-hidden rounded-lg border border-line"
          aria-label="View source photo"
          onClick={(event) => setFrame(event.currentTarget)}
        >
          <img
            src={photo.url}
            alt="Source photo used for this edit"
            className="size-full object-contain"
            loading="lazy"
            onError={() => setBroken(true)}
          />
        </button>
      )}
      {edit && !available && (
        <p className="mt-1">Source photo unavailable · edit history kept</p>
      )}
      {frame && available && (
        <ImageViewer
          job={photo}
          jobs={[photo]}
          frame={frame}
          onClose={() => setFrame(undefined)}
        />
      )}
    </div>
  );
}

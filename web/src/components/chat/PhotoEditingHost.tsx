import { useEffect, useLayoutEffect } from "react";
import { usePhotoEdit, type PhotoEditor } from "@/hooks/usePhotoEdit";
import type { Model } from "@/lib/api";
import type { ImageJob } from "@/lib/image-events";

export type PhotoCommand = {
  key: string;
  owner: string;
  source: File | ImageJob;
};
export default function PhotoEditingHost({
  owner,
  model,
  command,
  onApplied,
  onChange,
}: {
  owner: string;
  model?: Model;
  command?: PhotoCommand;
  onApplied: (key: string) => void;
  onChange: (value: PhotoEditor) => void;
}) {
  const editor = usePhotoEdit(owner, model);
  useLayoutEffect(() => onChange(editor), [editor, onChange]);
  useEffect(() => {
    if (command?.owner === owner) {
      void editor.attach(command.source);
      onApplied(command.key);
    }
    // A command owns one upload even while progress changes its controller.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [command?.key, owner]);
  return null;
}

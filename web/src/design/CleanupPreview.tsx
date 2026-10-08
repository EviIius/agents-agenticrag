import { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AudioChip } from "@/components/chat/AudioChip";
import { TranscriptSheet } from "@/components/chat/TranscriptSheet";
import {
  GlossaryEditor,
  type GlossaryPreview,
} from "@/components/settings/GlossaryEditor";
import { Button } from "@/components/ui/button";
import { useUI } from "@/stores/ui";
import type { Attachment, Model, Transcript } from "@/lib/api";
export const cleanupStates = [
  "Cleaning chip",
  "Cleaned chip",
  "Ready to clean",
  "Cleaning transcript",
  "Cleaned transcript",
  "Partial clean-up",
  "Clean-up failed",
  "Clean-up cancelled",
  "Glossary ready",
  "Glossary empty",
  "Glossary loading",
  "Glossary failed",
  "Glossary invalid",
  "Glossary saving",
  "Glossary saved",
];
const model: Model = {
  connection_id: "fake",
  model_id: "fake-chat",
  display_name: "Invented local model",
  context_length: 16384,
  params_defaults: {},
  embedding: false,
  hidden: false,
  chat_capable: true,
};
export function CleanupPreview() {
  const ui = useUI();
  const [query] = useState(() => new QueryClient()),
    [state, setState] = useState("Ready to clean"),
    [open, setOpen] = useState(false);
  const cleaning = state.startsWith("Cleaning");
  const failed = state === "Clean-up failed" || state === "Clean-up cancelled";
  const clean =
    state === "Cleaned chip" ||
    state === "Cleaned transcript" ||
    state === "Partial clean-up";
  const item: Attachment = {
    id: "fake-cleanup",
    kind: "audio",
    filename: "Invented lantern recording.wav",
    mime_type: "audio/wav",
    bytes: 1024,
    audio_available: false,
    transcript: {
      status: "ready",
      channels: "mix",
      duration_seconds: 75,
      word_count: 12,
      token_estimate: 24,
      elapsed_seconds: 1,
      engine_model: "fake-whisper",
      warnings: [],
      correction_count: 0,
      cleanup:
        cleaning || failed || clean
          ? {
              status: cleaning ? "running" : failed ? "failed" : "ready",
              model,
              chunks: 12,
              done: cleaning ? 3 : 12,
              kept_original: state === "Partial clean-up" ? 2 : 0,
              changed_words: 0,
              elapsed_seconds: clean ? 18 : null,
              error: failed
                ? {
                    code: "cleanup_failed",
                    message:
                      state === "Clean-up cancelled"
                        ? "Cancelled"
                        : "the model changed the wording in every section",
                  }
                : null,
            }
          : null,
    },
  };
  const transcript: Transcript = {
    attachment: item,
    text: "invented lantern rises over the orchard we discuss the next harvest",
    raw_text:
      "invented lantern rises over the orchard we discuss the next harvest",
    cleaned_text: clean
      ? "Invented lantern rises over the orchard.\n\nWe discuss the next harvest."
      : null,
    corrections: [],
    segments: [
      {
        start: 0,
        end: 75,
        text: "invented lantern rises over the orchard we discuss the next harvest",
        raw_text:
          "invented lantern rises over the orchard we discuss the next harvest",
        speaker: null,
      },
    ],
  };
  return (
    <QueryClientProvider client={query}>
      <main className="mx-auto max-w-5xl space-y-5 p-4">
        <h1 className="font-serif text-2xl">Clean-up · synthetic preview</h1>
        <div className="flex flex-wrap gap-2">
          {cleanupStates.map((label) => (
            <Button
              key={label}
              variant={state === label ? "default" : "outline"}
              onClick={() => {
                setState(label);
                setOpen(
                  !label.includes("chip") && !label.startsWith("Glossary"),
                );
              }}
            >
              {label}
            </Button>
          ))}
        </div>
        <div className="flex gap-2">
          {(["light", "dark"] as const).map((theme) => (
            <Button
              key={theme}
              variant={ui.theme === theme ? "secondary" : "outline"}
              onClick={() => ui.set({ theme })}
            >
              {theme}
            </Button>
          ))}
        </div>
        <div
          data-slot="cleanup-fixture"
          className="max-w-xl rounded-lg border border-line p-4"
        >
          {state.startsWith("Glossary") ? (
            <GlossaryEditor
              key={state}
              preview={state.slice(9).toLowerCase() as GlossaryPreview}
            />
          ) : (
            <AudioChip
              key={state}
              attachment={item}
              model={model}
              fixture={transcript}
            />
          )}
        </div>
        {open && (
          <TranscriptSheet
            key={state}
            open={open}
            onOpenChange={setOpen}
            attachment={item}
            fixture={transcript}
            model={model}
          />
        )}
      </main>
    </QueryClientProvider>
  );
}

import { useState } from "react";
import { AudioChip, UploadChip } from "@/components/chat/AudioChip";
import { TranscriptSheet } from "@/components/chat/TranscriptSheet";
import {
  RecordingDownloadDialog,
  type DownloadPreview,
} from "@/components/chat/RecordingDownloadDialog";
import { Composer } from "@/components/chat/Composer";
import { SearchActivity } from "@/components/chat/SearchActivity";
import { TranscriptionSettings } from "@/components/settings/TranscriptionSettings";
import { Button } from "@/components/ui/button";
import type {
  Attachment,
  Transcript,
  Model,
  Message,
  TranscriptionStatus,
} from "@/lib/api";
export const fakeRecording: Attachment = {
  id: "design-recording",
  kind: "audio",
  filename: "Synthetic recording.wav",
  mime_type: "audio/wav",
  bytes: 1024,
  transcript: {
    status: "ready",
    channels: "mix",
    duration_seconds: 75,
    word_count: 18,
    token_estimate: 35,
    elapsed_seconds: 1,
    engine_model: "fake-whisper",
    warnings: ["Synthetic warning for the design preview."],
    correction_count: 1,
  },
};
export const fakeTranscript: Transcript = {
  attachment: fakeRecording,
  text: "Fake transcript. This recording is not real. We discussed the next release. Follow up on Friday.",
  raw_text:
    "Fake transcript. This recording is not real. We discussed the next release. Follow up on Friday.",
  segments: [
    {
      start: 0,
      end: 25,
      text: "Fake transcript. This recording is not real.",
      raw_text: "Fake transcript. This recording is not real.",
      speaker: "Speaker 1",
    },
    {
      start: 25,
      end: 75,
      text: "We discussed the next release. Follow up on Friday.",
      raw_text: "We discussed the next release. Follow up on Friday.",
      speaker: "Speaker 2",
    },
  ],
  corrections: [{ found: "Gismo", replaced_with: "GSMOS", count: 1 }],
};
const model: Model = {
  connection_id: "design",
  model_id: "fake-chat",
  display_name: "Fake 16K model",
  context_length: 16384,
  params_defaults: {},
  embedding: false,
  hidden: false,
  chat_capable: true,
};
const message: Message = {
  id: "design-blocked",
  chat_id: "design",
  role: "assistant",
  content: "Synthetic reply",
  status: "complete",
  created_at: "2026-10-03",
  web: {
    source_count: 0,
    plan_fallback: false,
    ranking: "keyword",
    status: "skipped",
    notice: { code: "search_blocked_recording", message: "" },
  },
};
export function TranscriptionPreview() {
  const [open, setOpen] = useState(false);
  const [download, setDownload] = useState<DownloadPreview | null>(null);
  const states: Attachment[] = [
    {
      ...fakeRecording,
      id: "design-queued",
      transcript: { channels: "mix", correction_count: 0, status: "queued" },
    },
    {
      ...fakeRecording,
      id: "design-transcribing",
      transcript: {
        channels: "mix",
        correction_count: 0,
        status: "transcribing",
        started_at: new Date(Date.now() - 42000).toISOString(),
      },
    },
    fakeRecording,
    {
      ...fakeRecording,
      id: "design-large",
      transcript: { ...fakeRecording.transcript!, token_estimate: 30000 },
    },
    {
      ...fakeRecording,
      id: "design-silence",
      transcript: {
        ...fakeRecording.transcript!,
        word_count: 0,
        token_estimate: 0,
      },
    },
    {
      ...fakeRecording,
      id: "design-failed",
      transcript: {
        channels: "mix",
        correction_count: 0,
        status: "failed",
        error: {
          code: "transcription_failed",
          message: "Synthetic unreadable recording",
        },
      },
    },
    {
      ...fakeRecording,
      id: "design-interrupted",
      transcript: {
        channels: "mix",
        correction_count: 0,
        status: "failed",
        error: {
          code: "transcription_interrupted",
          message: "Interrupted because the server restarted",
        },
      },
    },
    {
      ...fakeRecording,
      id: "design-cancelled",
      transcript: { channels: "mix", correction_count: 0, status: "cancelled" },
    },
  ];
  const status: TranscriptionStatus = {
    glossary_terms: 0,
    configured: true,
    ready: true,
    version: "fake-0.1.0",
    checks: [
      {
        name: "Fake engine",
        ok: true,
        blocking: true,
        detail: "Synthetic fixture only",
      },
    ],
  };
  return (
    <section
      id="transcription-preview"
      className="design-card mb-8"
      aria-label="Transcription preview"
    >
      <h2 className="mb-3 text-lg font-medium">
        Recordings · synthetic fixtures · T1
      </h2>
      <p className="mb-5 text-xs text-fg-3">
        Fake engine content. No real recording or transcript is used here.
      </p>
      <UploadChip
        upload={{
          id: "design-upload",
          filename: "Synthetic recording.wav",
          percent: 42,
        }}
        onCancel={() => {}}
      />
      <UploadChip
        upload={{
          id: "design-upload-failed",
          filename: "Synthetic recording.wav",
          percent: 0,
          failed: true,
        }}
        onCancel={() => {}}
      />
      {states.map((item) => (
        <AudioChip
          key={item.id}
          attachment={item}
          model={model}
          fixture={{ ...fakeTranscript, attachment: item }}
          onRemove={() => {}}
        />
      ))}
      <div className="my-6">
        <Composer
          model={model}
          files={[fakeRecording]}
          transcriptionReady
          webBlocked
          onWebChange={() => {}}
          onAttach={() => {}}
          onRemove={() => {}}
        />
      </div>
      <SearchActivity message={message} sources={[]} onRetry={() => {}} />
      <Button variant="outline" onClick={() => setOpen(true)}>
        Preview transcript panel
      </Button>
      <div
        className="my-4 flex flex-wrap gap-2"
        aria-label="Recording download previews"
      >
        {(
          [
            "ready",
            "preparing",
            "failed",
            "sharing",
            "cancelled",
            "share-failed",
            "returned",
          ] as const
        ).map((state) => (
          <Button
            key={state}
            variant="outline"
            onClick={() => setDownload(state)}
          >
            Preview download {state}
          </Button>
        ))}
      </div>
      {download && (
        <RecordingDownloadDialog
          attachment={fakeRecording}
          initial={{ format: "txt" }}
          includeAudio
          preview={download}
          onClose={() => setDownload(null)}
        />
      )}
      <TranscriptSheet
        attachment={fakeRecording}
        fixture={fakeTranscript}
        open={open}
        onOpenChange={setOpen}
      />
      <div className="mt-6 space-y-4">
        <h3 className="font-medium">Ready · fake engine</h3>
        <TranscriptionSettings fixture={status} />
        <h3 className="font-medium">Not set up · fixture</h3>
        <TranscriptionSettings
          fixture={{
            glossary_terms: 0,
            configured: false,
            ready: false,
            checks: [
              {
                name: "Fake engine",
                ok: false,
                blocking: true,
                detail: "Synthetic missing-engine example",
              },
            ],
          }}
        />
      </div>
    </section>
  );
}

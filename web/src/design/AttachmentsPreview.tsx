import { useState } from "react";
import { Composer } from "@/components/chat/Composer";
import { Button } from "@/components/ui/button";
import type { Attachment, Model } from "@/lib/api";
import type { AudioUpload } from "@/components/chat/AudioChip";
import { fakeRecording, fakeTranscript } from "./TranscriptionPreview";
import { useUI } from "@/stores/ui";
const photo =
  "data:image/svg+xml," +
  encodeURIComponent(
    '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300"><rect width="400" height="300" fill="#b8d8cc"/><circle cx="300" cy="60" r="26" fill="#fff4db"/><path d="M0 230 100 140 260 270 400 180V300H0" fill="#586c85"/></svg>',
  );
const base: Model = {
  connection_id: "design",
  model_id: "fake-chat",
  display_name: "Fake text model",
  vision: false,
  chat_capable: true,
  embedding: false,
  hidden: false,
  params_defaults: {},
  context_length: 32768,
  reasoning: { options: ["off", "low", "medium", "xhigh"] },
};
const vision = {
  ...base,
  model_id: "fake-vision",
  display_name: "Fake vision model",
  vision: true,
};
export const attachmentStates = [
  "empty",
  "ready",
  "preparing",
  "HEIC",
  "uploading",
  "reading",
  "warning",
  "no vision model",
  "over budget",
  "too large",
  "unsupported",
  "network",
  "unreadable",
  "unavailable",
  "transcribing",
  "cleaning",
  "1 file",
  "4 files",
  "8 files",
  "Word",
  "JSON",
  "Markdown",
  "queued",
  "cancelled",
  "failed",
  "cleaned",
];
export default function AttachmentsPreview() {
  const [state, setState] = useState(
      new URLSearchParams(location.search).get("state") ?? "empty",
    ),
    [model, setModel] = useState<Model>(vision),
    [web, setWeb] = useState(false),
    [library, setLibrary] = useState(false),
    [think, setThink] = useState<string>(),
    [scope, setScope] =
      useState<import("@/components/chat/LibraryControl").Scope>(null);
  const [removed, setRemoved] = useState<string[]>([]);
  const ui = useUI();
  const files: Attachment[] =
    state === "empty"
      ? []
      : [
          {
            id: "fake-photo",
            kind: "image",
            filename: "Harbor-fake.png",
            mime_type: "image/png",
            bytes: 42000,
            audio_available: true,
          },
          {
            id: "fake-pdf",
            kind: "text",
            filename: "Spring-market-vendor-plan-fake-2026.pdf",
            mime_type: "application/pdf",
            bytes: 18000,
            audio_available: true,
            document: {
              source: "pdf",
              pages: 12,
              token_estimate: state === "over budget" ? 30000 : 8400,
              chars: 25000,
            },
          },
          {
            id: "fake-text",
            kind: "text",
            filename: "Stall-prices-fake.csv",
            mime_type: "text/csv",
            bytes: 18000,
            audio_available: true,
          },
          {
            ...fakeRecording,
            id: "fake-recording",
            filename: "Team-sync-fake.m4a",
            transcript: {
              ...fakeRecording.transcript!,
              ...(state === "transcribing"
                ? {
                    status: "transcribing" as const,
                    started_at: new Date().toISOString(),
                  }
                : state === "cleaning"
                  ? {
                      cleanup: {
                        status: "running" as const,
                        chunks: 8,
                        done: 3,
                        kept_original: 0,
                        changed_words: 0,
                      },
                    }
                  : {}),
            },
          },
        ];
  if (["queued", "cancelled", "failed"].includes(state) && files[3])
    files[3].transcript = {
      ...files[3].transcript!,
      status: state as "queued" | "cancelled" | "failed",
      error:
        state === "failed"
          ? {
              code: "transcription_failed",
              message: "Synthetic engine failure",
            }
          : undefined,
    };
  if (state === "cleaned" && files[3])
    files[3].transcript = {
      ...files[3].transcript!,
      cleanup: {
        status: "ready",
        done: 8,
        chunks: 8,
        kept_original: 0,
        changed_words: 1,
      },
    };
  if (state === "Word")
    files.splice(0, files.length, {
      ...files[1],
      id: "fake-word",
      filename: "Volunteer-list-fake.docx",
      document: {
        source: "docx",
        pages: null,
        chars: 6000,
        token_estimate: 2100,
      },
    });
  if (["JSON", "Markdown"].includes(state))
    files.splice(0, files.length, {
      ...files[2],
      id: "fake-text",
      filename: `Notes-fake.${state === "JSON" ? "json" : "md"}`,
    });
  if (state === "1 file") files.splice(1);
  if (state === "8 files")
    for (let i = 4; i < 8; i++)
      files.push({
        ...files[2],
        id: `fake-${i}`,
        filename: `Notes-${i}-fake.txt`,
      });
  const pending = [
    "preparing",
    "HEIC",
    "uploading",
    "reading",
    "too large",
    "unsupported",
    "network",
    "unreadable",
    "unavailable",
  ].includes(state);
  const uploads: AudioUpload[] = pending
    ? [
        {
          id: "fake-upload",
          filename:
            state === "HEIC"
              ? "Harbor-fake.heic"
              : state === "unsupported"
                ? "Archive-fake.zip"
                : state === "reading"
                  ? "Reading-plan-fake.pdf"
                  : "Picked-photo-fake.png",
          kind: state === "reading" ? "document" : "image",
          percent: state === "reading" ? 100 : 45,
          format: state === "HEIC" ? "HEIC" : undefined,
          phase: ["preparing", "HEIC"].includes(state)
            ? "preparing"
            : state === "reading"
              ? "reading"
              : state === "uploading"
                ? "uploading"
                : "error",
          failed: !["preparing", "HEIC", "reading", "uploading"].includes(
            state,
          ),
          retryable: state === "network",
          reason: (
            {
              "too large": "‘Picked-photo-fake.png’ is over 20 MB.",
              unsupported:
                "Can't attach .zip files. Images, PDF, Word, text and recordings work.",
              network: "‘Picked-photo-fake.png’ didn't finish uploading.",
              unreadable:
                "Couldn't open this image. Export it as a JPEG or PNG and try again.",
              unavailable: "Recordings need the transcription engine.",
            } as Record<string, string>
          )[state],
        },
      ]
    : [];
  const visible = (pending ? [] : files).filter(
    (file) => !removed.includes(file.id),
  );
  const local = Object.fromEntries(
    [...visible.map((f) => ({ id: f.id })), ...uploads].map((item, i) => [
      item.id,
      {
        key: item.id,
        order: i,
        stagger: i,
        ...(item.id.includes("photo") || item.id === "fake-upload"
          ? {
              url: state === "HEIC" ? "data:image/heic;base64,ZmFrZQ==" : photo,
            }
          : {}),
      },
    ]),
  );
  return (
    <div className="design-page">
      <h1 className="mb-4 text-2xl font-serif">
        Attachments · synthetic states
      </h1>
      <div className="mb-6 flex flex-wrap gap-2">
        {attachmentStates.map((name) => (
          <Button
            key={name}
            variant="outline"
            onClick={() => {
              setState(name);
              setRemoved([]);
            }}
          >
            Preview {name}
          </Button>
        ))}
        <Button onClick={() => setModel(model.vision ? base : vision)}>
          Switch Text/Vision
        </Button>
        <Button
          onClick={() =>
            ui.set({ theme: ui.theme === "dark" ? "light" : "dark" })
          }
        >
          Toggle theme
        </Button>
        <Button
          onClick={() =>
            ui.set({
              reduceMotion: ui.reduceMotion === "always" ? "system" : "always",
            })
          }
        >
          Reduce motion
        </Button>
      </div>
      <Composer
        key={state}
        files={visible}
        uploads={uploads.filter((u) => !removed.includes(u.id))}
        attachmentLocal={local}
        attachmentFixtures={{
          transcripts: {
            "fake-recording": {
              ...fakeTranscript,
              attachment:
                files.find((f) => f.kind === "audio") ?? fakeRecording,
            },
          },
          text: {
            "fake-pdf": "Synthetic PDF text. Nothing private.",
            "fake-word": "Synthetic Word text. Nothing private.",
            "fake-text": "item,price\nSynthetic sample,12",
          },
        }}
        model={["warning", "no vision model"].includes(state) ? base : model}
        visionModels={state === "no vision model" ? [base] : [base, vision]}
        onChooseModel={(m) => {
          setModel(m as typeof vision);
          if (state === "warning") setState("ready");
        }}
        onRemove={(id) => setRemoved((old) => [...old, id])}
        onCancelUpload={(id) => setRemoved((old) => [...old, id])}
        onRetryUpload={() => setState("uploading")}
        onSend={async () => true}
        onAttach={() => setState("uploading")}
        images
        previewImages
        transcriptionReady
        attachmentExtensions={{
          text: [".txt", ".csv"],
          document: [".pdf", ".docx"],
        }}
        audioExtensions={[".wav", ".m4a"]}
        web={web}
        onWebChange={(v) => {
          setWeb(v);
          if (v) setLibrary(false);
        }}
        libraryControl={{
          enabled: library,
          scope,
          collections: [
            {
              id: "fake-collection",
              name: "Market notes",
              updated_at: "2026-10-15",
              created_at: "2026-10-15",
            },
          ],
          onToggle: (v) => {
            setLibrary(v);
            if (v) setWeb(false);
          },
          onScope: setScope,
        }}
        thinkValue={think}
        onThinkChange={(v) => setThink(v ?? undefined)}
      />
    </div>
  );
}

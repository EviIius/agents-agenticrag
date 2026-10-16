import { useEffect, useRef, useState } from "react";
import { LiveThread } from "@/components/chat/LiveThread";
import { Composer } from "@/components/chat/Composer";
import DropOverlay from "@/components/chat/DropOverlay";
import { Button } from "@/components/ui/button";
import type { Attachment, Message, Model } from "@/lib/api";
import type { AttachmentLocal } from "@/hooks/useUploads";
import { fakeRecording, fakeTranscript } from "./TranscriptionPreview";
import { useUI } from "@/stores/ui";

export const threadAttachmentStates = [
  "sent-1",
  "sent-2",
  "sent-3",
  "sent-7",
  "mixed",
  "optimistic",
  "history",
  "loading",
  "missing-photo",
  "drop",
  "drop-target",
  "paste",
  "viewer",
  "pdf",
  "text",
  "transcript",
];
const model: Model = {
  connection_id: "design",
  model_id: "fake-vision",
  display_name: "Fake vision model",
  vision: true,
  chat_capable: true,
  embedding: false,
  hidden: false,
  params_defaults: {},
  context_length: 32768,
};
export function fakeThreadPhoto(index: number) {
  return (
    "data:image/svg+xml," +
    encodeURIComponent(
      `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300"><rect width="400" height="300" fill="${index % 2 ? "#b8d8cc" : "#f3c6a5"}"/><circle cx="300" cy="60" r="26" fill="#fff4db"/><path d="M0 230 100 140 260 270 400 180V300H0" fill="#586c85"/></svg>`,
    )
  );
}
export default function AttachmentThreadPreview() {
  const [state, setState] = useState(
    new URLSearchParams(location.search).get("state") ?? "mixed",
  );
  const [confirmed, setConfirmed] = useState(false);
  const [web, setWeb] = useState(false);
  const [draftFiles, setDraftFiles] = useState<Attachment[]>([]);
  const [draftLocal, setDraftLocal] = useState<Record<string, AttachmentLocal>>(
    {},
  );
  const [draftText, setDraftText] = useState<Record<string, string>>({});
  const urls = useRef<string[]>([]);
  useEffect(
    () => () => urls.current.forEach((url) => URL.revokeObjectURL(url)),
    [],
  );
  const scroll = useRef<HTMLDivElement>(null),
    surface = useRef<HTMLElement>(null);
  const ui = useUI();
  const count = state.startsWith("sent-")
    ? Number(state.slice(5))
    : ["mixed", "optimistic", "history"].includes(state)
      ? 2
      : 1;
  const photoFiles: Attachment[] = Array.from(
    { length: count },
    (_, index) => ({
      id: `fake-photo-${index + 1}`,
      kind: "image",
      filename: `Harbor-${index + 1}-fake.png`,
      mime_type: "image/png",
      bytes: 42000,
      audio_available: true,
    }),
  );
  const pdf: Attachment = {
    id: "fake-pdf",
    kind: "text",
    filename: "Spring-market-plan-fake-2026.pdf",
    mime_type: "application/pdf",
    bytes: 18000,
    audio_available: true,
    document: { source: "pdf", pages: 12, token_estimate: 8400, chars: 25000 },
  };
  const text: Attachment = {
    id: "fake-text",
    kind: "text",
    filename: "Stall-prices-fake.csv",
    mime_type: "text/csv",
    bytes: 43,
    audio_available: true,
  };
  const recording = {
    ...fakeRecording,
    id: "fake-recording",
    filename: "Team-sync-fake.m4a",
  };
  const attachments =
    state.startsWith("sent-") ||
    ["viewer", "loading", "missing-photo"].includes(state)
      ? photoFiles
      : ["drop", "drop-target", "paste"].includes(state)
        ? []
        : ["pdf"].includes(state)
          ? [pdf]
          : state === "text"
            ? [text]
            : state === "transcript"
              ? [recording]
              : [...photoFiles, pdf, text, recording];
  const local = Object.fromEntries(
    photoFiles.map((file, i) => [
      file.id,
      {
        key: file.id,
        order: i,
        url: ["loading", "missing-photo"].includes(state)
          ? `/api/attachments/${file.id}`
          : fakeThreadPhoto(i),
      },
    ]),
  );
  const message: Message = {
    id: state === "optimistic" && !confirmed ? "pending-fake" : "fake-sent",
    chat_id: "design",
    role: "user",
    content: "Make one checklist from these synthetic files.",
    status: "complete",
    created_at: "2026-10-01T12:00:00Z",
    attachments,
  };
  useEffect(() => {
    const frame = requestAnimationFrame(() => {
      if (state === "paste") {
        const data = new DataTransfer();
        data.setData("text/plain", "Synthetic long paste fake. ".repeat(200));
        surface.current?.querySelector("textarea")?.dispatchEvent(
          new ClipboardEvent("paste", {
            bubbles: true,
            cancelable: true,
            clipboardData: data,
          }),
        );
      }
      const selector =
        state === "viewer"
          ? ".message-photo"
          : state === "pdf"
            ? '[data-slot="document-chip"] button'
            : state === "text"
              ? ".message-text-file"
              : state === "transcript"
                ? ".attachment-audio-open"
                : null;
      if (selector)
        surface.current?.querySelector<HTMLButtonElement>(selector)?.click();
    });
    return () => cancelAnimationFrame(frame);
  }, [state]);
  return (
    <div className="design-page attachment-thread-preview">
      <h1 className="mb-4 text-2xl font-serif">
        Sent attachments · synthetic states
      </h1>
      <div className="mb-6 flex flex-wrap gap-2">
        {threadAttachmentStates.map((name) => (
          <Button
            key={name}
            variant="outline"
            onClick={() => {
              setState(name);
              setConfirmed(false);
              setDraftFiles([]);
              setDraftLocal({});
            }}
          >
            Preview {name}
          </Button>
        ))}
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
        {state === "optimistic" && !confirmed && (
          <Button onClick={() => setConfirmed(true)}>Confirm send</Button>
        )}
      </div>
      <section
        ref={surface}
        className="app-main attachment-thread-surface"
        data-file-drag={["drop", "drop-target"].includes(state) || undefined}
        data-drop-target={state === "drop-target" || undefined}
      >
        <DropOverlay active={["drop", "drop-target"].includes(state)} />
        <LiveThread
          key={state}
          messages={state === "optimistic" && !confirmed ? [] : [message]}
          all={[message]}
          pending={state === "optimistic" && !confirmed ? message : null}
          attachmentLocal={local}
          attachmentFixtures={{
            text: {
              "fake-pdf": "Synthetic PDF text. Nothing private.",
              "fake-text": "stall,price\nFake stall,40",
            },
            transcripts: {
              "fake-recording": { ...fakeTranscript, attachment: recording },
            },
          }}
          scrollRef={scroll}
          selectedModel={model}
          onAboveBottomChange={() => {}}
          onRegenerate={() => {}}
          onEdit={async () => true}
          onBranch={() => {}}
        />
        <div className="composer-row">
          <Composer
            key={state}
            model={model}
            web={web}
            onWebChange={setWeb}
            starter="Review these synthetic files."
            onSend={async () => true}
            files={draftFiles}
            attachmentLocal={draftLocal}
            attachmentFixtures={{ text: draftText }}
            attachmentExtensions={{
              text: [".txt", ".csv"],
              document: [".pdf", ".docx"],
            }}
            onAttach={(incoming, pasted) => {
              const ids = incoming.map(
                () => "fake-pasted-" + crypto.randomUUID(),
              );
              const added: Attachment[] = incoming.map((file, i) => ({
                id: ids[i],
                kind: file.type.startsWith("image/") ? "image" : "text",
                filename: file.name,
                mime_type: file.type,
                bytes: file.size,
                audio_available: true,
              }));
              setDraftFiles((old) => [...old, ...added]);
              incoming.forEach((file, i) => {
                const url = file.type.startsWith("image/")
                  ? URL.createObjectURL(file)
                  : undefined;
                if (url) urls.current.push(url);
                setDraftLocal((old) => ({
                  ...old,
                  [ids[i]]: {
                    key: ids[i],
                    order: i,
                    url,
                    characters: pasted?.characters,
                  },
                }));
                void file
                  .text()
                  .then((value) =>
                    setDraftText((old) => ({ ...old, [ids[i]]: value })),
                  );
              });
              return ids;
            }}
            onRemove={(id) =>
              setDraftFiles((old) => old.filter((file) => file.id !== id))
            }
            onDiscardPasted={(id) =>
              setDraftFiles((old) => old.filter((file) => file.id !== id))
            }
          />
        </div>
      </section>
    </div>
  );
}

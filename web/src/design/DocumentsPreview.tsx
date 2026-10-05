import { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DocumentChip } from "@/components/chat/DocumentChip";
import DocumentSheet from "@/components/chat/DocumentSheet";
import { UploadChip } from "@/components/chat/AudioChip";
import { Composer } from "@/components/chat/Composer";
import { Button } from "@/components/ui/button";
import { useUI } from "@/stores/ui";
import { errorCopy } from "@/lib/errors";
import type { Attachment } from "@/lib/api";
import { fixtureModels } from "./ProductionFixtures";
const document: Attachment = {
  id: "fake-document",
  kind: "text",
  filename: "Invented orchard.pdf",
  mime_type: "application/pdf",
  bytes: 240,
  audio_available: true,
  document: { source: "pdf", pages: 2, chars: 240, token_estimate: 72 },
};
const text =
  "[Page 1]\nInvented silver orchard report.\n\n[Page 2]\nInvented copper meadow report.";
export const documentStates = [
  "PDF",
  "Word",
  "Overflow",
  "Uploading",
  "Extracting",
  "Upload failure",
  "Review text",
  "Review loading",
  "Review error",
  "document_no_text",
  "document_encrypted",
  "document_unreadable",
  "document_too_large",
  "document_timeout",
];
export function DocumentsPreview() {
  const [client] = useState(
    () => new QueryClient({ defaultOptions: { queries: { retry: false } } }),
  );
  const [state, setState] = useState("PDF");
  const [open, setOpen] = useState(true);
  const item =
    state === "Word"
      ? {
          ...document,
          filename: "Invented orchard.docx",
          document: {
            ...document.document!,
            source: "docx" as const,
            pages: null,
          },
        }
      : state === "Overflow"
        ? {
            ...document,
            document: { ...document.document!, token_estimate: 20_000 },
          }
        : document;
  return (
    <QueryClientProvider client={client}>
      <main className="p-4 sm:p-8">
        <h1 className="mb-4 font-serif text-2xl">
          Documents · synthetic preview
        </h1>
        <div className="mb-4 flex flex-wrap gap-2">
          {documentStates.map((name) => (
            <Button
              key={name}
              variant={state === name ? "default" : "outline"}
              onClick={() => {
                setState(name);
                setOpen(true);
              }}
            >
              {name}
            </Button>
          ))}
          {["light", "dark"].map((theme) => (
            <Button
              key={theme}
              variant="ghost"
              onClick={() =>
                useUI.getState().set({ theme: theme as "light" | "dark" })
              }
            >
              {theme}
            </Button>
          ))}
        </div>
        <section aria-label="Documents preview" className="max-w-xl">
          {state.startsWith("document_") ? (
            <Composer error={errorCopy(state, "")} model={fixtureModels[0]} />
          ) : state.startsWith("Review") ? (
            <DocumentSheet
              key={state}
              attachment={item}
              open={open}
              onOpenChange={setOpen}
              fixture={
                state === "Review text"
                  ? { text }
                  : state === "Review loading"
                    ? "loading"
                    : "error"
              }
            />
          ) : ["Uploading", "Extracting", "Upload failure"].includes(state) ? (
            <UploadChip
              upload={{
                id: "fake-upload",
                filename: "Invented orchard.pdf",
                kind: "document",
                percent: state === "Extracting" ? 100 : 40,
                failed: state === "Upload failure",
                reason: errorCopy("document_unreadable", ""),
              }}
              onCancel={() => setState("PDF")}
            />
          ) : (
            <>
              {state !== "Overflow" && (
                <DocumentChip
                  key={state}
                  attachment={item}
                  model={fixtureModels[0]}
                  fixture={{
                    text:
                      state === "Word"
                        ? "Lantern\tMeadow\nViolet\tCopper"
                        : text,
                  }}
                  onRemove={() => setState("Uploading")}
                />
              )}
              <Composer
                model={fixtureModels[0]}
                context={{
                  used_tokens: item.document?.token_estimate ?? 0,
                  context_length: 16384,
                }}
                files={state === "Overflow" ? [item] : []}
                attachmentExtensions={{
                  text: [".txt", ".swift"],
                  document: [".pdf", ".docx"],
                }}
              />
            </>
          )}
        </section>
      </main>
    </QueryClientProvider>
  );
}

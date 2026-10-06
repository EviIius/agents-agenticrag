import { useState, lazy, Suspense } from "react";
import { Button } from "@/components/ui/button";
import { LibraryControl, type Scope } from "@/components/chat/LibraryControl";
import { SearchActivity } from "@/components/chat/SearchActivity";
import { SourcesSheet } from "@/components/chat/SourcesSheet";
import { CitationPill } from "@/components/chat/CitationPill";
import type { Message, Source } from "@/lib/api";
const Markdown = lazy(() => import("@/components/chat/Markdown"));
export const libraryAnswerStates = [
  "Ready",
  "Searching",
  "Empty scope",
  "Failed",
  "Uncited",
  "Removed file",
  "No embedding",
  "No ready files",
  "Remote model",
  "Collections",
];
export default function LibraryAnswersPreview() {
  const [state, setState] = useState("Ready"),
    [enabled, toggle] = useState(true),
    [scope, setScope] = useState<Scope>(null);
  const source: Source = {
    n: 1,
    url:
      state === "Removed file" ? "" : "/api/library/documents/fake/file#page=2",
    title: "Invented-handbook.pdf",
    site_name: "Invented-handbook.pdf",
    domain: "",
    fetched_at: "2026-10-06",
    kind: "document",
    document_id: state === "Removed file" ? null : "fake",
    page_start: 2,
    page_end: 3,
    cited: true,
    passages: [
      {
        selection_applied: false,
        source_url: "fake",
        ord: 0,
        heading: "Invented expenses",
        text: "The invented daily meal limit is 35 dollars.",
      },
    ],
  };
  const message: Message = {
    id: "fake",
    chat_id: "fake",
    role: "assistant",
    status: state === "Searching" ? "streaming" : "complete",
    content: "The daily meal limit is 35 dollars [1].",
    created_at: "2026-10-06",
    library: {
      status:
        state === "Empty scope"
          ? "skipped"
          : state === "Failed"
            ? "failed"
            : "used",
      source_count: 1,
      passage_count: 1,
      timings: { total: 400 },
      queries: ["Invented meal reimbursement"],
      notice:
        state === "Empty scope"
          ? { code: "library_empty", message: "" }
          : state === "Failed"
            ? {
                code: "library_failed",
                message: "The Library retrieval was unavailable.",
              }
            : state === "Uncited"
              ? { code: "uncited", message: "" }
              : null,
    },
  };
  const reason =
    state === "No embedding"
      ? "Choose an embedding model in Settings › Library"
      : state === "No ready files"
        ? "No ready files in this scope"
        : state === "Remote model"
          ? "Library text can only go to a local model"
          : undefined;
  return (
    <main className="mx-auto max-w-2xl space-y-5 p-6">
      <h1 className="text-xl font-medium">
        Library answers · synthetic preview
      </h1>
      <div className="flex flex-wrap gap-2" aria-label="Library answer states">
        {libraryAnswerStates.map((s) => (
          <Button
            key={s}
            variant="outline"
            aria-pressed={state === s}
            onClick={() => setState(s)}
          >
            {s}
          </Button>
        ))}
      </div>
      <LibraryControl
        enabled={enabled}
        reason={reason}
        scope={scope}
        onScope={setScope}
        onToggle={toggle}
        collections={[
          {
            id: "fake-collection",
            name: "Invented policies",
            created_at: "2026-10-06",
            updated_at: "2026-10-06",
          },
        ]}
      />
      <SearchActivity
        message={message}
        sources={[source]}
        steps={
          state === "Searching"
            ? [{ label: "searching", detail: "", status: "ok" }]
            : undefined
        }
        onRetry={() => setState("Searching")}
      />
      <Suspense fallback={<p>Loading preview…</p>}>
        <Markdown text={message.content} sources={[source]} />
      </Suspense>
      <CitationPill
        sources={[source]}
        sentence="The daily meal limit is 35 dollars."
      />
      <SourcesSheet message={message} sources={[source]} reads={[]} />
    </main>
  );
}

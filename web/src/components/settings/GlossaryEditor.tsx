import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import type { components } from "@/lib/api-types";
type Glossary = components["schemas"]["Glossary"];
export type GlossaryPreview =
  "ready" | "empty" | "loading" | "failed" | "invalid" | "saving" | "saved";
export function GlossaryEditor({ preview }: { preview?: GlossaryPreview }) {
  const fetched = useQuery({
    queryKey: ["glossary"],
    queryFn: () => api<Glossary>("/transcription/glossary"),
    enabled: !preview,
    retry: false,
  });
  const [draft, setDraft] = useState<string | null>(null),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [saved, setSaved] = useState(false);
  const data = preview
    ? {
        text:
          preview === "empty"
            ? ""
            : "Invented Orion = invented orion\nInvented Ember\n",
        terms: preview === "empty" ? [] : ["Invented Orion", "Invented Ember"],
      }
    : fetched.data;
  const text = draft ?? data?.text ?? "";
  const invalid =
    preview === "invalid" ||
    text.includes("\0") ||
    new TextEncoder().encode(text).length > 65536;
  const pending = busy || preview === "saving";
  return (
    <section aria-label="Transcription glossary" className="space-y-3">
      <h3 className="text-sm font-medium">Glossary</h3>
      <p className="text-xs text-fg-2">
        One term per line: CORRECT = wrong form, another wrong form. Lines
        starting with # are comments.
      </p>
      {(!preview && fetched.isPending) || preview === "loading" ? (
        <p role="status">Loading glossary…</p>
      ) : (!preview && fetched.isError) || preview === "failed" ? (
        <p role="alert" className="text-sm text-danger">
          Couldn't load the glossary.{" "}
          <Button variant="link" onClick={() => void fetched.refetch()}>
            Retry glossary
          </Button>
        </p>
      ) : (
        <>
          <label htmlFor="transcription-glossary" className="block text-sm">
            Terms for transcription
          </label>
          <Textarea
            id="transcription-glossary"
            value={text}
            disabled={pending}
            aria-invalid={invalid}
            aria-describedby="glossary-validation"
            className="min-h-40"
            onChange={(event) => {
              setDraft(event.target.value);
              setSaved(false);
              setError("");
            }}
          />
          <p
            id="glossary-validation"
            className={`text-xs ${invalid ? "text-danger" : "text-fg-2"}`}
          >
            {invalid
              ? "Glossary can be up to 64 KB and cannot contain NUL bytes."
              : `${data?.terms.length ?? 0} saved terms`}
          </p>
          {error && (
            <p role="alert" className="text-sm text-danger">
              {error}
            </p>
          )}
          <Button
            variant="outline"
            disabled={pending || invalid || (!preview && text === data?.text)}
            onClick={async () => {
              if (preview) return;
              setBusy(true);
              setError("");
              try {
                const next = await api<Glossary>(
                  "/transcription/glossary",
                  { text },
                  "PUT",
                );
                await fetched.refetch();
                setDraft(next.text);
                setSaved(true);
              } catch {
                setError(
                  "Couldn't save the glossary. Your terms are unchanged. Try again.",
                );
              } finally {
                setBusy(false);
              }
            }}
          >
            {pending ? "Saving glossary…" : "Save glossary"}
          </Button>
          {(saved || preview === "saved") && (
            <p role="status" className="text-sm text-success">
              Glossary saved
            </p>
          )}
        </>
      )}
      <p className="text-xs text-fg-2">
        New terms apply to recordings you add from now on. To apply them to an
        older recording, add it again.
      </p>
    </section>
  );
}

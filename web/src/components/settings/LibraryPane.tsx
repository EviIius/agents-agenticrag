import { useEffect, useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { MoreHorizontal, Upload } from "lucide-react";
import { api, ApiError, type Model } from "@/lib/api";
import type { components } from "@/lib/api-types";
import { failureCopy } from "@/lib/errors";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

type Index = components["schemas"]["LibraryIndex"];
type Document = components["schemas"]["LibraryDocument"];
type Collection = components["schemas"]["LibraryCollectionInfo"];
export type LibraryDialog =
  | { kind: "model"; model: Model | null }
  | { kind: "collection"; collection?: Collection }
  | { kind: "move" | "delete" | "text"; document: Document }
  | { kind: "clear" }
  | { kind: "remove-collection"; collection: Collection };
const size = (bytes: number) =>
  bytes >= 1024 ** 2
    ? `${(bytes / 1024 ** 2).toFixed(1)} MB`
    : `${Math.ceil(bytes / 1024)} KB`;
export function LibraryView({
  data,
  models,
  mutate,
  upload,
  busy = false,
  error = "",
  initialDialog = null,
  readText = (id: string) =>
    api<components["schemas"]["LibraryText"]>(`/library/documents/${id}/text`),
}: {
  data: Index;
  models: Model[];
  mutate: (url: string, body?: unknown, method?: string) => Promise<boolean>;
  upload: (files: File[], collection?: string) => Promise<void>;
  busy?: boolean;
  error?: string;
  initialDialog?: LibraryDialog | null;
  readText?: (id: string) => Promise<components["schemas"]["LibraryText"]>;
}) {
  const [dialog, setDialog] = useState<LibraryDialog | null>(initialDialog),
    [name, setName] = useState(""),
    [confirmation, setConfirmation] = useState(""),
    [collection, setCollection] = useState("unfiled"),
    [text, setText] = useState("");
  const picker = useRef<HTMLInputElement>(null);
  const embeddingModels = models.filter((m) => m.embedding);
  const selected = data.embedding
    ? JSON.stringify([data.embedding.connection_id, data.embedding.model_id])
    : "none";
  const act = async (url: string, body?: unknown, method?: string) => {
    if (await mutate(url, body, method)) setDialog(null);
  };
  const open = (document: Document) => {
    if (document.mime_type === "application/pdf") {
      window.open(
        `/api/library/documents/${document.id}/file`,
        "_blank",
        "noopener,noreferrer",
      );
      return;
    }
    setDialog({ kind: "text", document });
  };
  const textId = dialog?.kind === "text" ? dialog.document.id : null;
  const read = useRef(readText);
  read.current = readText;
  useEffect(() => {
    if (!textId) return;
    let cancelled = false;
    setText("");
    void read
      .current(textId)
      .then((value) => {
        if (!cancelled)
          setText(value.text || "This file has no indexed text yet.");
      })
      .catch(() => {
        if (!cancelled)
          setText("Couldn't open this file. Close and try again.");
      });
    return () => {
      cancelled = true;
    };
  }, [textId]);
  useEffect(() => {
    if (
      collection !== "unfiled" &&
      !data.collections.some((c) => c.id === collection)
    )
      setCollection("unfiled");
  }, [data.collections, collection]);
  return (
    <div className="space-y-5">
      <p className="text-sm text-fg-2">
        Keep files on your Mac for cited answers. Adding files does not send a
        chat request.
      </p>
      {!data.available && (
        <p role="alert">
          Library needs SQLite extension support. Chat is still available.
        </p>
      )}
      <label className="block space-y-2">
        <span>Embedding model</span>
        <Select
          value={selected}
          disabled={busy || !data.available}
          onValueChange={(v) =>
            setDialog({
              kind: "model",
              model:
                embeddingModels.find(
                  (m) => JSON.stringify([m.connection_id, m.model_id]) === v,
                ) ?? null,
            })
          }
        >
          <SelectTrigger
            className="min-h-11 w-full"
            aria-label="Embedding model"
          >
            <SelectValue placeholder="Choose an embedding model" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="none">Choose an embedding model</SelectItem>
            {embeddingModels.map((m) => (
              <SelectItem
                key={JSON.stringify([m.connection_id, m.model_id])}
                value={JSON.stringify([m.connection_id, m.model_id])}
              >
                {m.display_name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </label>
      {!embeddingModels.length && (
        <p className="text-sm text-fg-3">
          Add an embedding model in Ollama, then choose it here.
        </p>
      )}
      {data.embedding && (
        <p className="text-xs text-fg-3">
          {String(data.embedding.dim)} dimensions · Changes require re-indexing
          your files.
        </p>
      )}
      <label className="flex min-h-11 items-center gap-3 text-sm">
        <Switch
          aria-label="Only send library text to local models"
          checked={data.requires_local}
          disabled={busy}
          onCheckedChange={(v) =>
            void mutate("/settings", { "library.requires_local": v }, "PATCH")
          }
        />
        Only send library text to local models
      </label>
      <p className="text-sm text-fg-3">
        Turn on Library beside Web search in the composer to answer from these
        files with citations. Library turns off web search for that message.
      </p>
      <details>
        <summary className="cursor-pointer py-3 text-sm">
          Embedding prefixes
        </summary>
        <div className="space-y-3">
          {(["document", "query"] as const).map((kind) => (
            <label className="block space-y-2" key={kind}>
              <span className="text-sm">
                {kind === "document"
                  ? "Document prefix (requires re-indexing)"
                  : "Query prefix"}
              </span>
              <Input
                aria-label={`${kind} prefix`}
                defaultValue={data[`${kind}_prefix`]}
                key={data[`${kind}_prefix`]}
                maxLength={1000}
                disabled={busy}
                onBlur={(e) => {
                  if (e.target.value !== data[`${kind}_prefix`])
                    void mutate(
                      "/settings",
                      { [`library.${kind}_prefix`]: e.target.value },
                      "PATCH",
                    );
                }}
              />
            </label>
          ))}
          <p className="text-xs text-fg-3">
            Leave empty unless your embedding model requires a prefix.
          </p>
        </div>
      </details>
      <section
        aria-label="Add Library files"
        className="rounded-lg border border-dashed border-line p-4 space-y-3"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          if (!busy && data.available)
            void upload(
              Array.from(e.dataTransfer.files),
              collection === "unfiled" ? undefined : collection,
            );
        }}
      >
        <p className="text-sm text-fg-2">
          Drop PDF, Word, Markdown, text or HTML files here. Up to 100 MB each;
          selectable text only.
        </p>
        <Select value={collection} onValueChange={setCollection}>
          <SelectTrigger
            className="min-h-11 w-full"
            aria-label="Collection for new files"
          >
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="unfiled">Unfiled</SelectItem>
            {data.collections.map((c) => (
              <SelectItem key={c.id} value={c.id}>
                {c.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <input
          type="file"
          ref={picker}
          className="hidden"
          aria-label="Add files to Library"
          accept=".pdf,.docx,.md,.txt,.html"
          multiple
          onChange={(e) => {
            void upload(
              Array.from(e.target.files ?? []),
              collection === "unfiled" ? undefined : collection,
            );
            e.target.value = "";
          }}
        />
        <Button
          disabled={busy || !data.available}
          onClick={() => picker.current?.click()}
        >
          <Upload aria-hidden />
          {busy ? "Working…" : "Add files"}
        </Button>
        {!data.embedding && (
          <p className="text-xs text-fg-3">
            Files wait in the queue until you choose an embedding model.
          </p>
        )}
      </section>
      <section aria-label="Library collections" className="space-y-2">
        <div className="flex flex-wrap items-center gap-3">
          <h3 className="font-medium">Collections</h3>
          <Button
            variant="outline"
            disabled={busy}
            onClick={() => {
              setName("");
              setDialog({ kind: "collection" });
            }}
          >
            New collection
          </Button>
        </div>
        {data.collections.map((c) => (
          <div key={c.id} className="flex items-center justify-between gap-2">
            <span className="min-w-0 break-words">{c.name}</span>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label={`Actions for collection ${c.name}`}
                >
                  <MoreHorizontal />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem
                  className="min-h-11"
                  onSelect={() => {
                    setName(c.name);
                    setDialog({ kind: "collection", collection: c });
                  }}
                >
                  Rename
                </DropdownMenuItem>
                <DropdownMenuItem
                  className="min-h-11 text-danger"
                  onSelect={() =>
                    setDialog({ kind: "remove-collection", collection: c })
                  }
                >
                  Delete collection
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        ))}
      </section>
      <section aria-label="Library files" className="space-y-3">
        <h3 className="font-medium">Files</h3>
        {!data.documents.length && (
          <p className="text-sm text-fg-3">
            No files yet. Add one to start your Library.
          </p>
        )}
        {data.documents.map((d) => (
          <article
            key={d.id}
            className="rounded-lg border border-line p-3 space-y-2"
            aria-label={`Library file ${d.filename}`}
          >
            <div className="flex items-start justify-between gap-2">
              <h4 className="min-w-0 font-medium break-words">{d.filename}</h4>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label={`Actions for ${d.filename}`}
                    disabled={busy}
                  >
                    <MoreHorizontal />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem
                    className="min-h-11"
                    onSelect={() => void open(d)}
                    disabled={!d.chunk_count}
                  >
                    Open
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    className="min-h-11"
                    onSelect={() => {
                      setName(d.collection_id ?? "unfiled");
                      setDialog({ kind: "move", document: d });
                    }}
                  >
                    Move to collection
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    className="min-h-11"
                    disabled={
                      !data.embedding ||
                      ["queued", "extracting", "embedding"].includes(d.status)
                    }
                    onSelect={() =>
                      void mutate(
                        `/library/documents/${d.id}/reindex`,
                        {},
                        "POST",
                      )
                    }
                  >
                    Re-index
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    className="min-h-11 text-danger"
                    onSelect={() => setDialog({ kind: "delete", document: d })}
                  >
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
            <p className="text-xs text-fg-3">
              {d.pages != null ? `${d.pages} pages · ` : ""}
              {d.chunk_count} passages · {size(d.bytes)} ·{" "}
              {data.collections.find((c) => c.id === d.collection_id)?.name ??
                "Unfiled"}{" "}
              · {new Date(d.created_at).toLocaleDateString()}
            </p>
            <p className="text-sm" role="status">
              {d.status === "embedding"
                ? `Embedding ${d.progress_done} of ${d.progress_total}`
                : d.status === "ready"
                  ? "Ready"
                  : d.status === "stale"
                    ? "Needs re-indexing"
                    : d.status === "extracting"
                      ? "Reading text…"
                      : d.status === "queued"
                        ? "Queued"
                        : "Couldn't index this file"}
            </p>
            {d.error && (
              <p className="text-sm text-danger">
                {d.error.code}: {d.error.message}
              </p>
            )}
          </article>
        ))}
      </section>
      <p className="text-sm text-fg-3">
        Original files: {size(data.bytes)} · {data.documents.length} files. Text
        and index storage is additional.
      </p>
      <div className="flex flex-wrap gap-2">
        <Button
          variant="outline"
          disabled={busy || !data.embedding || !data.counts.stale}
          onClick={() => void mutate("/library/reindex", {}, "POST")}
        >
          Re-index library
        </Button>
        <Button
          variant="outline"
          disabled={busy || !data.documents.length}
          onClick={() => {
            setConfirmation("");
            setDialog({ kind: "clear" });
          }}
        >
          Delete all library files
        </Button>
      </div>
      {error && (
        <p role="alert" className="text-sm text-danger">
          {error}
        </p>
      )}
      <Dialog
        open={!!dialog}
        onOpenChange={(v) => {
          if (!busy && !v) setDialog(null);
        }}
      >
        <DialogContent className="max-h-[85dvh] overflow-y-auto">
          <DialogTitle>
            {dialog?.kind === "model"
              ? "Change embedding model?"
              : dialog?.kind === "collection"
                ? dialog.collection
                  ? "Rename collection"
                  : "New collection"
                : dialog?.kind === "move"
                  ? "Move file"
                  : dialog?.kind === "text"
                    ? "File text"
                    : dialog?.kind === "remove-collection"
                      ? "Delete collection?"
                      : dialog?.kind === "clear"
                        ? "Delete all Library files?"
                        : "Delete file?"}
          </DialogTitle>
          <DialogDescription>
            {dialog?.kind === "model"
              ? "Existing files will need re-indexing. The originals and extracted passages stay on your Mac."
              : dialog?.kind === "remove-collection"
                ? "Files become unfiled. Their text and index stay intact."
                : dialog?.kind === "clear" || dialog?.kind === "delete"
                  ? "This removes Library originals and their index. Existing chats and saved citation passages are preserved."
                  : dialog?.kind === "text"
                    ? dialog.document.filename
                    : "Organize your Library files."}
          </DialogDescription>
          {dialog?.kind === "model" && (
            <p className="break-words">
              {dialog.model?.display_name ?? "Remove embedding model"}
            </p>
          )}
          {dialog?.kind === "collection" && (
            <Input
              aria-label="Collection name"
              value={name}
              maxLength={120}
              onChange={(e) => setName(e.target.value)}
            />
          )}
          {dialog?.kind === "move" && (
            <Select value={name} onValueChange={setName}>
              <SelectTrigger
                className="min-h-11 w-full"
                aria-label="Move to collection"
              >
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="unfiled">Unfiled</SelectItem>
                {data.collections.map((c) => (
                  <SelectItem key={c.id} value={c.id}>
                    {c.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
          {dialog?.kind === "clear" && (
            <label className="space-y-2">
              <span className="text-sm">Type DELETE to confirm</span>
              <Input
                aria-label="Type DELETE to confirm"
                value={confirmation}
                onChange={(e) => setConfirmation(e.target.value)}
              />
            </label>
          )}
          {dialog?.kind === "text" && (
            <pre className="max-h-[50dvh] overflow-y-auto whitespace-pre-wrap break-words text-sm font-sans">
              {text || "Loading text…"}
            </pre>
          )}
          {error && (
            <p role="alert" className="text-sm text-danger">
              {error}
            </p>
          )}
          <div className="flex flex-wrap justify-end gap-2">
            <Button
              variant="outline"
              disabled={busy}
              onClick={() => setDialog(null)}
            >
              {dialog?.kind === "text" ? "Close" : "Cancel"}
            </Button>
            {dialog && dialog.kind !== "text" && (
              <Button
                disabled={
                  busy ||
                  (dialog.kind === "clear" && confirmation !== "DELETE") ||
                  (dialog.kind === "collection" && !name.trim())
                }
                onClick={() => {
                  if (dialog.kind === "model")
                    void act("/library/embedding", {
                      embedding: dialog.model
                        ? {
                            connection_id: dialog.model.connection_id,
                            model_id: dialog.model.model_id,
                          }
                        : null,
                    });
                  else if (dialog.kind === "collection")
                    void act(
                      "/library/collections" +
                        (dialog.collection ? `/${dialog.collection.id}` : ""),
                      { name: name.trim() },
                      dialog.collection ? "PATCH" : "POST",
                    );
                  else if (dialog.kind === "move")
                    void act(
                      `/library/documents/${dialog.document.id}`,
                      { collection_id: name === "unfiled" ? null : name },
                      "PATCH",
                    );
                  else if (dialog.kind === "delete")
                    void act(
                      `/library/documents/${dialog.document.id}`,
                      undefined,
                      "DELETE",
                    );
                  else if (dialog.kind === "remove-collection")
                    void act(
                      `/library/collections/${dialog.collection.id}`,
                      undefined,
                      "DELETE",
                    );
                  else void act("/library", { confirmation }, "DELETE");
                }}
              >
                {busy
                  ? "Working…"
                  : dialog.kind === "model"
                    ? "Change model"
                    : ["clear", "delete", "remove-collection"].includes(
                          dialog.kind,
                        )
                      ? "Delete"
                      : "Save"}
              </Button>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export function LibraryFeedback({
  kind,
  retry,
}: {
  kind: "loading" | "error" | "disconnected";
  retry?: () => void;
}) {
  if (kind === "loading") return <p role="status">Loading Library…</p>;
  if (kind === "disconnected")
    return (
      <p role="status" className="text-sm text-fg-3">
        Progress connection interrupted. Reconnecting…
      </p>
    );
  return (
    <p role="alert">
      Couldn't load Library.{" "}
      <Button variant="outline" onClick={retry}>
        Retry
      </Button>
    </p>
  );
}

export default function LibraryPane({
  request = api,
  queryScope = [],
  models,
}: {
  request?: typeof api;
  queryScope?: string[];
  models: Model[];
}) {
  const query = useQueryClient(),
    key = ["library", ...queryScope];
  const state = useQuery({
    queryKey: key,
    queryFn: () => request<Index>("/library"),
  });
  const [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [connected, setConnected] = useState(true);
  const cursor = state.data?.event_id;
  useEffect(() => {
    if (request !== api || cursor === undefined) return;
    const stream = new EventSource(`/api/library/events?after=${cursor}`);
    let frame = 0;
    const refresh = () => {
      if (!frame)
        frame = requestAnimationFrame(() => {
          frame = 0;
          void query.invalidateQueries({
            queryKey: ["library", ...queryScope],
          });
        });
    };
    for (const event of [
      "library.changed",
      "document.queued",
      "document.extracting",
      "document.embedding",
      "document.ready",
      "document.failed",
    ])
      stream.addEventListener(event, refresh);
    stream.onopen = () => setConnected(true);
    stream.onerror = () => setConnected(false);
    return () => {
      stream.close();
      cancelAnimationFrame(frame);
    };
    // The initial cursor is retained for this subscription. EventSource resumes
    // with Last-Event-ID; snapshots must not recreate the stream on each event.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [request, cursor === undefined, query, JSON.stringify(queryScope)]);
  const mutate = async (url: string, body?: unknown, method?: string) => {
    setBusy(true);
    setError("");
    try {
      await request(url, body, method);
      await query.invalidateQueries({ queryKey: key });
      await query.invalidateQueries({ queryKey: ["bootstrap"] });
      return true;
    } catch (e) {
      setError(e instanceof ApiError ? e.message : failureCopy(e));
      return false;
    } finally {
      setBusy(false);
    }
  };
  const upload = async (files: File[], collection?: string) => {
    setBusy(true);
    setError("");
    const failures: string[] = [];
    try {
      for (const file of files) {
        if (file.size > 100 * 1024 ** 2) {
          failures.push("Library files can be up to 100 MB.");
          continue;
        }
        const form = new FormData();
        form.append("file", file);
        if (collection) form.append("collection_id", collection);
        try {
          await request("/library/documents", form);
        } catch (e) {
          failures.push(e instanceof ApiError ? e.message : failureCopy(e));
        }
      }
      await query.invalidateQueries({ queryKey: key });
      setError(failures.join(" "));
    } finally {
      setBusy(false);
    }
  };
  if (state.isPending) return <LibraryFeedback kind="loading" />;
  if (state.isError)
    return <LibraryFeedback kind="error" retry={() => void state.refetch()} />;
  return (
    <>
      {!connected && <LibraryFeedback kind="disconnected" />}
      <LibraryView
        data={state.data}
        models={models}
        busy={busy}
        error={error}
        mutate={mutate}
        upload={upload}
      />
    </>
  );
}

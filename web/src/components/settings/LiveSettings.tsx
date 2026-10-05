import { BackupPane } from "./BackupPane";
import { ModelRename } from "./ModelRename";
import { failureCopy, failureDetail } from "@/lib/errors";
import config from "../../../../shared/config.json";
import { LegacyImportDialog } from "./LegacyImportDialog";
import { lazy, Suspense, useState, useEffect, useRef } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router";
import { useUI } from "@/stores/ui";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import {
  AlertDialog,
  AlertDialogTrigger,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogCancel,
  AlertDialogAction,
} from "@/components/ui/alert-dialog";
import {
  Collapsible,
  CollapsibleTrigger,
  CollapsibleContent,
} from "@/components/ui/collapsible";
import { TranscriptionSettings } from "./TranscriptionSettings";
import { LiveChatSettings } from "./LiveChatSettings";
import { OllamaSearchKey } from "./OllamaSearchKey";
import { Textarea } from "@/components/ui/textarea";
import { api, type Bootstrap, type Model } from "@/lib/api";
import type { components } from "@/lib/api-types";
const PresetsPane = lazy(() => import("./PresetsPane"));
export function LiveSettingsPane({
  pane,
  bootstrap,
  models,
  onModelAction,
  request = api,
  queryScope = [],
}: {
  request?: typeof api;
  queryScope?: string[];
  pane: string;
  bootstrap?: Bootstrap;
  models: Model[];
  onModelAction?: (model: Model) => Promise<void>;
}) {
  const query = useQueryClient();
  const loadingStarted = useRef(0);
  const [elapsed, setElapsed] = useState(0);
  const [name, setName] = useState("Ollama on this Mac"),
    [url, setUrl] = useState("http://127.0.0.1:11434"),
    [loading, setLoading] = useState<string | null>(null),
    [brave, setBrave] = useState("");
  useEffect(() => {
    if (!loading) return;
    setElapsed(0);
    const timer = setInterval(
      () =>
        setElapsed(Math.floor((Date.now() - loadingStarted.current) / 1000)),
      1000,
    );
    return () => clearInterval(timer);
  }, [loading]);
  const all = useQuery({
    queryKey: ["models", ...queryScope, "all"],
    queryFn: () => request<Model[]>("/models?include_hidden=true"),
    enabled: pane === "Models" || pane === "Search",
  });
  const status = useQuery({
    queryKey: ["search-status", ...queryScope],
    queryFn: () =>
      request<components["schemas"]["SearchStatus"][]>("/search/status"),
    enabled: pane === "Search",
  });
  const update = async (endpoint: string, body: unknown, method?: string) => {
    try {
      await request(endpoint, body, method);
      await query.invalidateQueries();
      toast.success("Saved");
      return true;
    } catch (e) {
      toast.error(failureCopy(e), { description: failureDetail(e) });
      return false;
    }
  };
  if (pane === "Presets")
    return (
      <Suspense fallback={<p role="status">Loading presets…</p>}>
        <PresetsPane
          bootstrap={bootstrap}
          request={request}
          queryScope={queryScope}
        />
      </Suspense>
    );
  if (pane === "Transcription")
    return <TranscriptionSettings bootstrap={bootstrap} />;
  if (pane === "Connections")
    return (
      <>
        <p className="text-sm text-fg-2">Ollama runs locally on your Mac.</p>
        {bootstrap?.connections.map((c) => (
          <div key={c.id} className="rounded-lg border border-line p-4">
            <p className="mb-3 text-xs text-fg-2">
              <span
                className={c.reachable ? "text-success" : "text-fg-3"}
                aria-hidden
              >
                {c.reachable ? "●" : "○"}
              </span>{" "}
              {!c.enabled
                ? "Disabled"
                : c.reachable === false
                  ? "Offline"
                  : c.reachable
                    ? "Connected"
                    : "Status unknown"}
              {c.model_count != null ? ` · ${c.model_count} models` : ""}
              {c.latency_ms != null ? ` · ${Math.round(c.latency_ms)} ms` : ""}
            </p>
            <Input
              aria-label={"Connection name for " + c.name}
              defaultValue={c.name}
              onBlur={(e) => {
                if (e.target.value !== c.name)
                  void update(
                    "/connections/" + c.id,
                    { name: e.target.value },
                    "PATCH",
                  );
              }}
            />
            <Input
              className="my-2"
              aria-label={"URL for " + c.name}
              defaultValue={c.base_url}
              onBlur={(e) => {
                if (e.target.value !== c.base_url)
                  void update(
                    "/connections/" + c.id,
                    { base_url: e.target.value },
                    "PATCH",
                  );
              }}
            />
            <div className="my-3 grid grid-cols-2 gap-3">
              <label className="text-xs text-fg-2">
                Concurrent requests
                <Input
                  aria-label={"Concurrency for " + c.name}
                  type="number"
                  min={1}
                  max={8}
                  defaultValue={c.max_concurrent}
                  onBlur={(e) =>
                    void update(
                      "/connections/" + c.id,
                      { max_concurrent: Number(e.target.value) },
                      "PATCH",
                    )
                  }
                />
              </label>
              <label className="text-xs text-fg-2">
                Keep loaded
                <Input
                  aria-label={"Keep alive for " + c.name}
                  defaultValue={c.keep_alive}
                  onBlur={(e) =>
                    void update(
                      "/connections/" + c.id,
                      { keep_alive: e.target.value },
                      "PATCH",
                    )
                  }
                />
              </label>
            </div>
            <p className="mb-3 text-xs text-fg-3">
              Concurrency changes apply when the connection is idle.
            </p>
            <div className="flex flex-wrap gap-2">
              <Button
                variant="outline"
                onClick={() =>
                  void update(
                    "/connections/" + c.id,
                    { enabled: !c.enabled },
                    "PATCH",
                  )
                }
              >
                {c.enabled ? "Disable" : "Enable"}
              </Button>
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button variant="ghost">Remove</Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Remove connection?</AlertDialogTitle>
                    <AlertDialogDescription>
                      Your chats will be kept.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction
                      onClick={() =>
                        update("/connections/" + c.id, undefined, "DELETE")
                      }
                    >
                      Remove
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
          </div>
        ))}
        <label className="block text-sm">
          Name
          <Input value={name} onChange={(e) => setName(e.target.value)} />
        </label>
        <label className="block text-sm">
          Runtime URL
          <Input value={url} onChange={(e) => setUrl(e.target.value)} />
        </label>
        <Button
          onClick={() =>
            void update("/connections", { name, base_url: url, kind: "ollama" })
          }
        >
          Add connection
        </Button>
      </>
    );
  if (pane === "Models")
    return (
      <>
        <label className="block space-y-2 text-sm">
          <span>Model for new chats</span>
          <Select
            value={String(bootstrap?.settings.new_chat_model ?? "last_used")}
            onValueChange={(value) =>
              void update("/settings", { new_chat_model: value }, "PATCH")
            }
          >
            <SelectTrigger aria-label="Model for new chats">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="last_used">Last used model</SelectItem>
              <SelectItem value="fixed">Always use a model</SelectItem>
            </SelectContent>
          </Select>
        </label>
        {bootstrap?.settings.new_chat_model === "fixed" && (
          <label className="block space-y-2 text-sm">
            <span>Default model</span>
            <Select
              value={JSON.stringify([
                bootstrap.settings.default_connection_id,
                bootstrap.settings.default_model_id,
              ])}
              onValueChange={(value) => {
                const [connection_id, model_id] = JSON.parse(value);
                void update(
                  "/settings",
                  {
                    default_connection_id: connection_id,
                    default_model_id: model_id,
                  },
                  "PATCH",
                );
              }}
            >
              <SelectTrigger aria-label="Default model">
                <SelectValue placeholder="Choose model" />
              </SelectTrigger>
              <SelectContent>
                {models.map((m) => (
                  <SelectItem
                    key={m.connection_id + m.model_id}
                    value={JSON.stringify([m.connection_id, m.model_id])}
                  >
                    {m.display_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </label>
        )}
        <label className="block space-y-2 text-sm">
          <span>Helper model</span>
          <p className="text-xs text-fg-3">
            Plans web searches and writes chat titles.
          </p>
          <Select
            value={
              bootstrap?.settings.utility_model
                ? JSON.stringify(bootstrap.settings.utility_model)
                : "current"
            }
            onValueChange={(value) =>
              void update(
                "/settings",
                {
                  utility_model: value === "current" ? null : JSON.parse(value),
                },
                "PATCH",
              )
            }
          >
            <SelectTrigger aria-label="Helper model">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="current">Current chat model</SelectItem>
              {models.map((m) => (
                <SelectItem
                  key={m.connection_id + m.model_id}
                  value={JSON.stringify({
                    connection_id: m.connection_id,
                    model_id: m.model_id,
                  })}
                >
                  {m.display_name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </label>
        <label className="flex min-h-11 items-center justify-between gap-3 text-sm">
          <span>Generate chat titles</span>
          <Switch
            aria-label="Generate chat titles"
            checked={Boolean(bootstrap?.settings.auto_title)}
            onCheckedChange={(value) =>
              void update("/settings", { auto_title: value }, "PATCH")
            }
          />
        </label>
        <label className="flex min-h-11 items-center justify-between gap-3 text-sm">
          <span>Include current date</span>
          <Switch
            aria-label="Include current date"
            checked={Boolean(bootstrap?.settings.include_current_date)}
            onCheckedChange={(value) =>
              void update("/settings", { include_current_date: value }, "PATCH")
            }
          />
        </label>
        <label className="block space-y-2 text-sm">
          <span>Default system prompt</span>
          <Textarea
            aria-label="Default system prompt"
            defaultValue={String(
              bootstrap?.settings.default_system_prompt ?? "",
            )}
            onBlur={(event) =>
              void update(
                "/settings",
                { default_system_prompt: event.target.value },
                "PATCH",
              )
            }
          />
        </label>
        {(all.data ?? models).map((m) => (
          <div
            key={m.connection_id + m.model_id}
            className="rounded-lg border border-line p-4"
          >
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 className="font-medium break-words">{m.display_name}</h3>
              <ModelRename
                model={m}
                onSave={(display_name) =>
                  update(
                    "/models/prefs",
                    {
                      connection_id: m.connection_id,
                      model_id: m.model_id,
                      display_name,
                    },
                    "PUT",
                  )
                }
              />
            </div>
            <p className="mt-2 text-xs text-fg-3 break-all">{m.model_id}</p>
            <p className="my-3 text-xs text-fg-3 break-all">
              {m.params} · {m.quant} ·{" "}
              {m.size_bytes ? (m.size_bytes / 1e9).toFixed(1) + " GB" : ""} ·{" "}
              {(m.context_length ?? 0) / 1024}K context · configured limit{" "}
              {(m.context_limit ?? m.context_max ?? 0) / 1024}K ·{" "}
              {m.loaded ? "Loaded" : "Not loaded"}
              {m.vision ? " · Vision" : ""}
              {m.reasoning ? " · Reasoning" : ""}
            </p>
            <div className="flex gap-2">
              <Button
                variant="outline"
                disabled={
                  loading !== null || !m.chat_capable || (m.hidden && !m.loaded)
                }
                onClick={() => {
                  loadingStarted.current = Date.now();
                  setLoading(m.connection_id + ":" + m.model_id);
                  void (
                    onModelAction
                      ? onModelAction(m)
                      : update(m.loaded ? "/models/unload" : "/models/load", {
                          connection_id: m.connection_id,
                          model_id: m.model_id,
                        })
                  ).finally(() => {
                    void query.invalidateQueries({
                      queryKey: ["models", ...queryScope, "all"],
                    });
                    setLoading(null);
                  });
                }}
              >
                {loading === m.connection_id + ":" + m.model_id
                  ? `${m.loaded ? "Ejecting" : "Loading"}… ${elapsed}s`
                  : m.loaded
                    ? "Eject"
                    : "Load"}
              </Button>
              <Button
                variant="ghost"
                onClick={() =>
                  void update(
                    "/models/prefs",
                    {
                      connection_id: m.connection_id,
                      model_id: m.model_id,
                      hidden: !m.hidden,
                    },
                    "PUT",
                  )
                }
              >
                {m.hidden ? "Show" : "Hide"}
              </Button>
            </div>
            {m.chat_capable && (
              <Collapsible className="mt-3">
                <CollapsibleTrigger asChild>
                  <Button variant="outline">Parameters and context</Button>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <LiveChatSettings
                    key={JSON.stringify([m.connection_id, m.model_id])}
                    model={m}
                    defaultsOnly
                    onSave={(_, params) =>
                      update(
                        "/models/prefs",
                        {
                          connection_id: m.connection_id,
                          model_id: m.model_id,
                          params,
                        },
                        "PUT",
                      )
                    }
                    onDefaults={(params) =>
                      update(
                        "/models/prefs",
                        {
                          connection_id: m.connection_id,
                          model_id: m.model_id,
                          params,
                        },
                        "PUT",
                      )
                    }
                    onContext={(context_length) =>
                      update(
                        "/models/prefs",
                        {
                          connection_id: m.connection_id,
                          model_id: m.model_id,
                          context_length,
                        },
                        "PUT",
                      )
                    }
                  />
                </CollapsibleContent>
              </Collapsible>
            )}
          </div>
        ))}
      </>
    );
  if (pane === "Search")
    return (
      <>
        <p className="text-sm text-fg-2">
          Providers are tried in this order. Page fetches stay bounded.
        </p>
        {((bootstrap?.settings["web.provider_order"] as string[]) ?? []).map(
          (provider, i) => (
            <div
              className="rounded-lg border border-line p-3"
              key={provider}
              draggable
              onDragStart={(e) =>
                e.dataTransfer.setData("text/plain", provider)
              }
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                const from = e.dataTransfer.getData("text/plain"),
                  order = [
                    ...(bootstrap?.settings["web.provider_order"] as string[]),
                  ];
                if (!order.includes(from)) return;
                order.splice(order.indexOf(from), 1);
                order.splice(i, 0, from);
                void update(
                  "/settings",
                  { "web.provider_order": order },
                  "PATCH",
                );
              }}
            >
              <div className="flex flex-wrap items-center gap-2">
                <span className="min-w-0 flex-1 capitalize">
                  {provider === "ddgs"
                    ? "DuckDuckGo"
                    : provider === "ollama"
                      ? "Ollama Search"
                      : provider === "exa"
                        ? "Exa"
                        : provider}
                </span>
                <span className="text-xs text-fg-3">
                  {status.data?.find((s) => s.provider === provider)?.reachable
                    ? "Ready"
                    : "Unavailable"}
                </span>
                <Button
                  variant="outline"
                  onClick={() =>
                    void request<components["schemas"]["SearchTestResult"]>(
                      "/search/test",
                      { provider },
                    ).then((r) =>
                      toast(
                        r.ok
                          ? `${r.ms.toFixed(0)} ms · ${r.results.map((x) => x.title).join(" · ")}`
                          : r.error,
                      ),
                    )
                  }
                >
                  Test
                </Button>
                <Button
                  variant="ghost"
                  aria-label={`Move ${provider} earlier in the search order`}
                  disabled={i === 0}
                  onClick={() => {
                    const order = [
                      ...(bootstrap?.settings[
                        "web.provider_order"
                      ] as string[]),
                    ];
                    [order[i - 1], order[i]] = [order[i]!, order[i - 1]!];
                    void update(
                      "/settings",
                      { "web.provider_order": order },
                      "PATCH",
                    );
                  }}
                >
                  ↑
                </Button>
              </div>
              {provider === "searxng" && (
                <Input
                  aria-label="SearXNG URL"
                  defaultValue={String(
                    bootstrap?.settings["web.searxng_url"] ?? "",
                  )}
                  onBlur={(e) =>
                    void update(
                      "/settings",
                      { "web.searxng_url": e.target.value },
                      "PATCH",
                    )
                  }
                />
              )}
              {provider === "ollama" && (
                <OllamaSearchKey
                  hasKey={Boolean(
                    bootstrap?.settings["web.has_ollama_api_key"],
                  )}
                  onSave={(key) =>
                    update("/settings", { "web.ollama_api_key": key }, "PATCH")
                  }
                  onRemove={() =>
                    update("/settings", { "web.ollama_api_key": null }, "PATCH")
                  }
                />
              )}
              {provider === "exa" && (
                <p className="mt-2 text-sm text-fg-2">
                  Free keyless fallback. Rate limits apply.
                </p>
              )}
            </div>
          ),
        )}
        <label className="block text-sm">
          Brave API key{" "}
          {bootstrap?.settings["web.has_brave_api_key"] ? "· Key saved" : ""}
          <Input
            type="password"
            value={brave}
            onChange={(e) => setBrave(e.target.value)}
          />
        </label>
        <Button
          variant="outline"
          onClick={() => {
            void update(
              "/settings",
              { "web.brave_api_key": brave || null },
              "PATCH",
            );
            setBrave("");
          }}
        >
          Save key
        </Button>
        <label className="flex min-h-11 items-center gap-3 text-sm">
          <Switch
            checked={Boolean(bootstrap?.settings["web.default_on"])}
            onCheckedChange={(value) =>
              void update("/settings", { "web.default_on": value }, "PATCH")
            }
          />
          Search on for new chats
        </label>
        <label className="block text-sm">
          Sources per answer
          <Select
            value={String(bootstrap?.settings["web.max_sources"] ?? 6)}
            onValueChange={(v) =>
              void update(
                "/settings",
                { "web.max_sources": Number(v) },
                "PATCH",
              )
            }
          >
            <SelectTrigger aria-label="Sources per answer">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {[4, 6, 8].map((n) => (
                <SelectItem key={n} value={String(n)}>
                  {n}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </label>
        <label className="block text-sm">
          Ranking model
          <Select
            value={
              bootstrap?.settings["web.embedding"]
                ? JSON.stringify(bootstrap.settings["web.embedding"])
                : "off"
            }
            onValueChange={(v) =>
              void update(
                "/settings",
                { "web.embedding": v === "off" ? null : JSON.parse(v) },
                "PATCH",
              )
            }
          >
            <SelectTrigger aria-label="Ranking model">
              <SelectValue placeholder="Off" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="off">Off · keyword ranking</SelectItem>
              {(all.data ?? [])
                .filter((m) => m.embedding)
                .map((m) => (
                  <SelectItem
                    key={m.connection_id + m.model_id}
                    value={JSON.stringify({
                      connection_id: m.connection_id,
                      model_id: m.model_id,
                    })}
                  >
                    {m.display_name}
                  </SelectItem>
                ))}
            </SelectContent>
          </Select>
        </label>
        <label className="block text-sm">
          Keep fetched pages for
          <Select
            value={String(bootstrap?.settings["web.page_cache_days"] ?? 7)}
            onValueChange={(v) =>
              void update(
                "/settings",
                { "web.page_cache_days": Number(v) },
                "PATCH",
              )
            }
          >
            <SelectTrigger aria-label="Keep fetched pages for">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {[1, 7, 30].map((n) => (
                <SelectItem key={n} value={String(n)}>
                  {n} days
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </label>
        <label className="block text-sm">
          Blocked sites
          <Textarea
            defaultValue={(
              (bootstrap?.settings["web.blocked_domains"] as string[]) ?? []
            ).join("\n")}
            onBlur={(e) =>
              void update(
                "/settings",
                {
                  "web.blocked_domains": e.target.value
                    .split("\n")
                    .map((x) => x.trim())
                    .filter(Boolean),
                },
                "PATCH",
              )
            }
          />
        </label>
      </>
    );
  if (pane === "Shortcuts")
    return (
      <dl className="space-y-3 text-sm">
        <div>Enter · Send on desktop</div>
        <div>⌘/Ctrl Enter · Send</div>
        <div>Shift Enter · New line</div>
        <div>↑ in an empty composer · Edit last message</div>
        <div>Esc in the composer · Stop generating</div>
        <div>⌘/Ctrl K · Command palette</div>
        <div>⌘/Ctrl , · Settings</div>
        <div>⌘/Ctrl Shift O · New chat</div>
        <div>⌘/Ctrl B · Toggle sidebar</div>
        <div>⌘/Ctrl Shift . · Chat controls</div>
        <div>⌘/Ctrl / · Shortcuts</div>
      </dl>
    );
  if (pane === "About")
    return (
      <>
        <p>
          {config.APP_NAME} {bootstrap?.version}
        </p>
        <p className="text-sm break-all">Data folder: {bootstrap?.data_dir}</p>
        <ul className="space-y-2 text-sm text-fg-2">
          {bootstrap?.connections.map((connection) => (
            <li key={connection.id} className="break-all">
              {connection.name} · {connection.base_url} ·{" "}
              {connection.reachable ? "Connected" : "Offline"}
            </li>
          ))}
        </ul>
        <p className="text-sm text-fg-2">
          Private chat and web search, hosted on your Mac. Access from your
          phone through Tailscale.
        </p>
      </>
    );
  if (pane === "Data") return <DataPane />;
  return null;
}

export function DataPane({ preview = false }: { preview?: boolean }) {
  const query = useQueryClient();
  const navigate = useNavigate();
  const set = useUI((ui) => ui.set);
  const [open, setOpen] = useState(false);
  const [confirmation, setConfirmation] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  return (
    <div className="space-y-5">
      <p className="text-sm text-fg-2">
        Export every chat and branch, including citations, as one JSON file.
        Attachment files are stored separately on your Mac.
      </p>
      <Button asChild variant="outline">
        <a
          href={preview ? "#data-preview" : "/api/chats/export"}
          target="_blank"
          rel="noopener noreferrer"
          onClick={preview ? (event) => event.preventDefault() : undefined}
        >
          Export all chats
        </a>
      </Button>
      <BackupPane
        fixture={
          preview
            ? { last_at: "2026-10-05T03:30:00", count: 7, bytes: 43000000 }
            : undefined
        }
      />
      <LegacyImportDialog preview={preview ? "ready" : undefined} />
      <AlertDialog
        open={open}
        onOpenChange={(value) => {
          setOpen(value);
          setConfirmation("");
          setError("");
        }}
      >
        <AlertDialogTrigger asChild>
          <Button variant="outline">Delete all chats</Button>
        </AlertDialogTrigger>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete all chats?</AlertDialogTitle>
            <AlertDialogDescription>
              This removes all conversations, branches, citations and their
              attachment files. Type DELETE to confirm.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <Input
            aria-label="Type DELETE to confirm"
            value={confirmation}
            onChange={(event) => setConfirmation(event.target.value)}
            disabled={busy}
          />
          {error && (
            <p role="alert" className="text-sm text-danger">
              {error}
            </p>
          )}
          <AlertDialogFooter>
            <AlertDialogCancel disabled={busy}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              disabled={confirmation !== "DELETE" || busy}
              onClick={async (event) => {
                event.preventDefault();
                if (preview) {
                  setOpen(false);
                  return;
                }
                setBusy(true);
                setError("");
                try {
                  await api("/chats", { confirmation }, "DELETE");
                  setOpen(false);
                  set({ settings: false, sidebar: false, panel: false });
                  query.removeQueries({ queryKey: ["chat"] });
                  await query.invalidateQueries({ queryKey: ["chats"] });
                  await query.invalidateQueries({ queryKey: ["folders"] });
                  await query.invalidateQueries({ queryKey: ["folder-chats"] });
                  navigate("/");
                  toast("Chats deleted");
                } catch (failure) {
                  setError(
                    failure instanceof Error
                      ? failure.message
                      : "Chats could not be deleted.",
                  );
                } finally {
                  setBusy(false);
                }
              }}
            >
              {busy ? "Deleting…" : "Delete chats"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

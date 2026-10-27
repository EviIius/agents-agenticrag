import { useState, useEffect, useRef, type ComponentProps } from "react";
import {
  Brain,
  Check,
  ChevronDown,
  Eye,
  LoaderCircle,
  Wrench,
  X,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import {
  Drawer,
  DrawerContent,
  DrawerTitle,
  DrawerDescription,
  DrawerHeader,
  DrawerClose,
} from "@/components/ui/drawer";
import { modelLabel } from "@/lib/chat-presentation";
import { modelRows } from "@/lib/model-groups";
import { useUI } from "@/stores/ui";
import { useMediaQuery } from "@/hooks/useMediaQuery";
function GridElement(props: ComponentProps<"div">) {
  return <div {...props} role="grid" aria-label="Models" />;
}
function CellElement(props: ComponentProps<"div">) {
  return <div {...props} role="gridcell" />;
}
function GridSearch(props: ComponentProps<"input">) {
  return <input {...props} aria-haspopup="grid" />;
}
// cmdk fixes listbox/option roles after spreading props. Its asChild slot lets
// this richer picker use a grid: action buttons are cells, never option descendants.
function ModelGrid({ children, ...props }: ComponentProps<typeof CommandList>) {
  return (
    <CommandList {...props} asChild>
      <GridElement>{children}</GridElement>
    </CommandList>
  );
}
function ModelChoice({
  children,
  ...props
}: ComponentProps<typeof CommandItem>) {
  return (
    <CommandItem {...props} asChild>
      <CellElement>{children}</CellElement>
    </CommandItem>
  );
}
export type PickerState =
  "ready" | "loading" | "offline" | "empty" | "loading-model";
export function ModelPicker({
  state = "ready",
  models,
  current,
  onChoose,
  connections,
  onModelAction,
  loadingModel,
}: {
  loadingModel?: string | null;
  state?: PickerState;
  models?: import("@/lib/api").Model[];
  current?: import("@/lib/api").Model;
  connections?: import("@/lib/api").Bootstrap["connections"];
  onChoose?: (model: import("@/lib/api").Model) => void;
  onModelAction?: (model: import("@/lib/api").Model) => Promise<void>;
}) {
  const [open, setOpen] = useState(false);
  const [filter, setFilter] = useState("All");
  const [search, setSearch] = useState("");
  const [expanded, setExpanded] = useState<string[]>([]);
  const [more, setMore] = useState(false);
  const list = useRef<HTMLDivElement>(null);
  const measure = () => {
    const node = list.current;
    setMore(
      !!node && node.scrollHeight - node.clientHeight - node.scrollTop > 2,
    );
  };
  useEffect(() => {
    const frame = requestAnimationFrame(measure);
    const observer = new ResizeObserver(measure);
    if (list.current) {
      observer.observe(list.current);
      if (list.current.firstElementChild)
        observer.observe(list.current.firstElementChild);
    }
    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
    };
  }, [open, filter, search, expanded, models]);
  const matches = (model: import("@/lib/api").Model) =>
    filter === "All" ||
    (filter === "Loaded" && model.loaded === true) ||
    (filter === "Vision" && model.vision === true) ||
    (filter === "Reasoning" && !!model.reasoning) ||
    (filter === "Tools" && model.tools === true);
  const available = models?.filter(
    (model) =>
      matches(model) &&
      (modelLabel(model) + " " + model.model_id + " " + model.connection_id)
        .toLocaleLowerCase()
        .includes(search.toLocaleLowerCase()),
  );

  useEffect(() => {
    const show = () => setOpen(true);
    window.addEventListener("workbench:choose-model", show);
    return () => window.removeEventListener("workbench:choose-model", show);
  }, []);
  const [busy, setBusy] = useState<string | null>(null),
    [elapsed, setElapsed] = useState(0);
  const started = useRef(0);
  useEffect(() => {
    if (!busy && !loadingModel) return;
    if (loadingModel) started.current = Date.now();
    setElapsed(0);
    const timer = setInterval(
      () => setElapsed(Math.floor((Date.now() - started.current) / 1000)),
      1000,
    );
    return () => clearInterval(timer);
  }, [busy, loadingModel]);
  const phone = useMediaQuery("(max-width: 639px)");
  const previousLoad = useRef(loadingModel);
  const [loadedPulse, setLoadedPulse] = useState<string | null>(null);
  useEffect(() => {
    const loaded = previousLoad.current;
    previousLoad.current = loadingModel;
    if (
      loaded &&
      !loadingModel &&
      models?.some(
        (model) =>
          model.connection_id + model.model_id === loaded &&
          model.loaded === true,
      )
    ) {
      setLoadedPulse(loaded);
    }
  }, [loadingModel, models]);
  useEffect(() => {
    if (!loadedPulse) return;
    const timer = setTimeout(() => setLoadedPulse(null), 200);
    return () => clearTimeout(timer);
  }, [loadedPulse]);
  const trigger = (
    <Button
      variant="ghost"
      className="h-11 min-w-0 max-w-full gap-2 px-2"
      aria-label="Choose model"
      title={
        current?.loaded === false ? "Not loaded · loads on send" : undefined
      }
      onClick={() => setOpen(true)}
    >
      <span
        data-slot="model-status"
        data-loaded-fresh={
          loadedPulse ===
            (current?.connection_id ?? "") + (current?.model_id ?? "") ||
          undefined
        }
        className="text-success"
        aria-hidden
      >
        {loadingModel ===
        (current?.connection_id ?? "") + (current?.model_id ?? "") ? (
          <LoaderCircle data-activity="spin" className="size-4" />
        ) : current?.loaded == null ? (
          ""
        ) : current.loaded ? (
          "●"
        ) : (
          "○"
        )}
      </span>
      <span className="truncate font-medium">
        {current ? modelLabel(current) : "Choose model"}
      </span>
      {loadingModel && (
        <span role="status" className="text-xs text-fg-2">
          Loading… {elapsed}s
        </span>
      )}
      <span className="hidden text-xs text-fg-3 sm:block">
        {connections?.find(
          (connection) => connection.id === current?.connection_id,
        )?.name ?? ""}
      </span>
      <ChevronDown className="size-3 shrink-0" />
    </Button>
  );
  const content = (
    <Command
      shouldFilter={false}
      className={`min-h-0 flex-1 ${phone ? "model-picker-command overflow-y-auto scroll-pt-14" : ""}`}
    >
      <CommandInput
        asChild
        value={search}
        onValueChange={setSearch}
        placeholder="Search models…"
        aria-label="Search models"
        className={phone ? "pr-14" : undefined}
      >
        <GridSearch />
      </CommandInput>
      {models && state !== "loading" && (
        <div
          role="group"
          aria-label="Filter models"
          className="flex shrink-0 flex-wrap gap-1 border-b border-line px-2 py-1"
        >
          {["All", "Loaded", "Vision", "Reasoning", "Tools"].map((label) => (
            <Button
              key={label}
              variant={filter === label ? "secondary" : "ghost"}
              size="sm"
              className="min-h-11 px-2"
              aria-pressed={filter === label}
              onClick={() => setFilter(label)}
            >
              {label}
            </Button>
          ))}
        </div>
      )}
      <div
        className={`relative flex min-h-0 flex-col ${phone ? "shrink-0" : "flex-1"}`}
      >
        <ModelGrid ref={list} onScroll={measure} className="min-h-0 flex-1">
          {models && state !== "loading" && !available?.length && (
            <div role="row">
              <p role="gridcell" className="p-4 text-sm text-fg-2">
                No matching models.
              </p>
            </div>
          )}
          <>
            {models && state !== "loading" ? (
              Array.from(
                new Set(models.map((model) => model.connection_id)),
              ).map((id) => (
                <div
                  key={id}
                  role="rowgroup"
                  className="p-1"
                  aria-label={
                    connections?.find((connection) => connection.id === id)
                      ?.name ?? "Ollama"
                  }
                >
                  <div role="row">
                    <div
                      role="columnheader"
                      className="px-2 py-1.5 text-xs font-medium text-fg-2"
                    >
                      {connections?.find((connection) => connection.id === id)
                        ?.name ?? "Ollama"}
                    </div>
                  </div>
                  {modelRows(
                    (available ?? []).filter(
                      (model) => model.connection_id === id,
                    ),
                    current,
                    expanded,
                    !!search,
                  ).map(
                    ({ model, key: familyKey, count: variants, primary }) => (
                      <div
                        key={model.connection_id + model.model_id}
                        role="row"
                        className="flex min-w-0 items-center gap-1"
                      >
                        <ModelChoice
                          data-slot="model-choice"
                          value={
                            model.display_name +
                            " " +
                            model.model_id +
                            " " +
                            model.connection_id
                          }
                          data-active-model={
                            current?.model_id === model.model_id &&
                            current?.connection_id === model.connection_id
                          }
                          disabled={!!loadingModel}
                          onSelect={() => {
                            onChoose?.(model);
                            setOpen(false);
                          }}
                          className="group min-h-16 min-w-0 flex-1 gap-2"
                        >
                          <span
                            aria-hidden
                            className={
                              model.loaded ? "text-success" : "text-fg-2"
                            }
                          >
                            {model.loaded == null
                              ? ""
                              : model.loaded
                                ? "●"
                                : "○"}
                          </span>
                          <div className="min-w-0 flex-1">
                            <span className="flex flex-wrap items-center gap-2 break-words">
                              {modelLabel(model)}
                              {model.reasoning && (
                                <span className="inline-flex items-center gap-1 text-xs text-fg-2">
                                  <Brain
                                    aria-hidden
                                    className="size-3 shrink-0"
                                  />
                                  Thinks
                                </span>
                              )}
                              {model.vision && (
                                <span className="inline-flex items-center gap-1 text-xs text-fg-2">
                                  <Eye
                                    aria-hidden
                                    className="size-3 shrink-0"
                                  />
                                  Sees
                                </span>
                              )}
                              {model.tools && (
                                <span className="inline-flex items-center gap-1 text-xs text-fg-2">
                                  <Wrench
                                    aria-hidden
                                    className="size-3 shrink-0"
                                  />
                                  Tools
                                </span>
                              )}
                            </span>
                            {model.display_name !== model.model_id && (
                              <p className="meta break-all">{model.model_id}</p>
                            )}
                            <p className="meta">
                              {[
                                model.params,
                                model.quant,
                                model.context_length
                                  ? `${(model.context_length / 1024).toFixed(0)}K context`
                                  : null,
                                model.loaded == null
                                  ? "Status unknown"
                                  : model.loaded
                                    ? "Loaded"
                                    : "Not loaded",
                              ]
                                .filter(Boolean)
                                .join(" · ")}
                            </p>
                          </div>
                          {current?.model_id === model.model_id &&
                            current?.connection_id === model.connection_id && (
                              <Check
                                className="model-selected-mark size-4 shrink-0 text-brand"
                                role="img"
                                aria-label="Selected for chat"
                              />
                            )}
                        </ModelChoice>
                        <div
                          role="gridcell"
                          aria-label="Model actions"
                          className="flex shrink-0 flex-col items-center gap-1"
                        >
                          {primary && variants > 1 && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="min-h-11 shrink-0"
                              aria-label={`Variants for ${model.family}`}
                              aria-expanded={expanded.includes(familyKey)}
                              onKeyDown={(event) => {
                                if (event.key === "Enter" || event.key === " ")
                                  event.stopPropagation();
                              }}
                              onClick={(event) => {
                                event.preventDefault();
                                event.stopPropagation();
                                setExpanded((old) =>
                                  old.includes(familyKey)
                                    ? old.filter((key) => key !== familyKey)
                                    : [...old, familyKey],
                                );
                              }}
                            >
                              {variants} variants
                              <ChevronDown className="size-3" />
                            </Button>
                          )}
                          {onModelAction && (
                            <Button
                              variant="ghost"
                              size="sm"
                              data-slot="model-action"
                              className="min-h-11 shrink-0 px-2"
                              disabled={busy !== null || !!loadingModel}
                              aria-label={`${model.loaded ? "Eject" : "Load"} ${modelLabel(model)}`}
                              onKeyDown={(event) => {
                                if (event.key === "Enter" || event.key === " ")
                                  event.stopPropagation();
                              }}
                              onClick={async (event) => {
                                event.preventDefault();
                                event.stopPropagation();
                                started.current = Date.now();
                                setBusy(model.connection_id + model.model_id);
                                try {
                                  await onModelAction(model);
                                } finally {
                                  setBusy(null);
                                }
                              }}
                            >
                              {busy === model.connection_id + model.model_id
                                ? `${elapsed}s`
                                : model.loaded
                                  ? "Eject"
                                  : "Load"}
                            </Button>
                          )}
                        </div>
                      </div>
                    ),
                  )}
                </div>
              ))
            ) : state === "loading" ? (
              <div role="row">
                <div
                  role="gridcell"
                  aria-label="Loading models"
                  className="space-y-3 p-4"
                >
                  <div className="skeleton h-10" />
                  <div className="skeleton h-10" />
                </div>
              </div>
            ) : state === "empty" ? (
              <div role="row">
                <p role="gridcell" className="p-4 text-fg-2">
                  No models on this connection.
                </p>
              </div>
            ) : state === "offline" ? (
              <div role="row">
                <div role="gridcell" className="p-4 text-danger">
                  Offline ·{" "}
                  <Button variant="outline" onClick={() => setOpen(false)}>
                    Retry
                  </Button>
                </div>
              </div>
            ) : null}
            {models &&
              connections
                ?.filter(
                  (connection) =>
                    connection.enabled && connection.reachable === false,
                )
                .map((connection) => (
                  <div key={connection.id} role="row">
                    <p role="gridcell" className="p-3 text-sm text-fg-3">
                      {connection.name} · Offline · Check the connection in
                      Settings
                    </p>
                  </div>
                ))}
            {state === "loading-model" && (
              <div role="row">
                <p
                  role="gridcell"
                  className="flex items-center gap-2 p-4 text-fg-2"
                >
                  <LoaderCircle data-activity="spin" className="size-4" />
                  Loading {current?.display_name ?? "model"}… {elapsed} s
                </p>
              </div>
            )}
          </>
        </ModelGrid>
        {more && (
          <div
            data-slot="model-list-fade"
            className="pointer-events-none absolute inset-x-0 bottom-0 h-6 bg-gradient-to-t from-surface to-transparent"
            aria-hidden
          />
        )}
      </div>
      <div className="shrink-0 border-t border-line p-2">
        <Button
          variant="ghost"
          className="min-h-11 w-full justify-start"
          onClick={() => {
            setOpen(false);
            useUI.getState().set({ settings: true, settingsPane: "Models" });
          }}
        >
          Manage models…
        </Button>
      </div>
    </Command>
  );
  if (phone)
    return (
      <>
        <div className="min-w-0">{trigger}</div>
        <Drawer open={open} onOpenChange={setOpen}>
          <DrawerContent>
            <DrawerHeader className="model-picker-heading">
              <DrawerTitle>Choose model</DrawerTitle>
              <DrawerDescription>Local models on your Mac</DrawerDescription>
            </DrawerHeader>
            {content}
            <DrawerClose asChild>
              <Button
                variant="ghost"
                size="icon"
                aria-label="Close model picker"
                className="model-picker-close-compact icon-button absolute right-3 top-6 z-20"
              >
                <X />
              </Button>
            </DrawerClose>
            <DrawerClose asChild>
              <Button variant="ghost" className="model-picker-close-footer m-3">
                Close
              </Button>
            </DrawerClose>
          </DrawerContent>
        </Drawer>
      </>
    );
  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>{trigger}</PopoverTrigger>
      <PopoverContent
        aria-label="Choose model"
        align="start"
        className="flex max-h-[calc(var(--radix-popover-content-available-height)-var(--spacing))] w-[min(420px,calc(100vw-32px))] flex-col overflow-hidden p-0"
      >
        {content}
      </PopoverContent>
    </Popover>
  );
}

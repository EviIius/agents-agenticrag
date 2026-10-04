import { useState, useEffect, useRef } from "react";
import {
  Brain,
  Check,
  ChevronDown,
  Eye,
  LoaderCircle,
  Wrench,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
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
import { useMediaQuery } from "@/hooks/useMediaQuery";
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
  const trigger = (
    <Button
      variant="ghost"
      className="h-11 min-w-0 max-w-full gap-2 px-2"
      aria-label="Choose model"
      onClick={() => setOpen(true)}
    >
      <span className="text-success" aria-hidden>
        {loadingModel ===
        (current?.connection_id ?? "") + (current?.model_id ?? "") ? (
          <LoaderCircle className="size-4 animate-spin" />
        ) : current?.loaded == null ? (
          ""
        ) : current.loaded ? (
          "●"
        ) : (
          "○"
        )}
      </span>
      <span className="truncate font-medium">
        {current?.display_name ?? "Choose model"}
      </span>
      {loadingModel && (
        <span role="status" className="text-xs text-fg-2">
          Loading… {elapsed}s
        </span>
      )}
      <span className="hidden text-xs text-fg-3 sm:block">Ollama</span>
      <ChevronDown className="size-3 shrink-0" />
    </Button>
  );
  const content = (
    <Command className="min-h-0 flex-1">
      <CommandInput placeholder="Search models…" aria-label="Search models" />
      <CommandList className="min-h-0 flex-1">
        <CommandEmpty>No matching models.</CommandEmpty>
        <>
          {models && state !== "loading" ? (
            Array.from(new Set(models.map((model) => model.connection_id))).map(
              (id) => (
                <CommandGroup
                  key={id}
                  heading={
                    connections?.find((connection) => connection.id === id)
                      ?.name ?? "Ollama"
                  }
                >
                  {models
                    .filter((model) => model.connection_id === id)
                    .map((model) => (
                      <CommandItem
                        key={model.connection_id + model.model_id}
                        value={model.display_name + " " + model.connection_id}
                        data-active-model={
                          current?.model_id === model.model_id &&
                          current?.connection_id === model.connection_id
                        }
                        disabled={!!loadingModel}
                        onSelect={() => {
                          onChoose?.(model);
                          setOpen(false);
                        }}
                        className="group min-h-16 gap-2"
                      >
                        <span
                          aria-hidden
                          className={
                            model.loaded ? "text-success" : "text-fg-2"
                          }
                        >
                          {model.loaded == null ? "" : model.loaded ? "●" : "○"}
                        </span>
                        <div className="min-w-0 flex-1">
                          <span className="flex flex-wrap items-center gap-2 break-words">
                            {model.display_name}
                            {model.reasoning && (
                              <Brain
                                aria-label="Supports reasoning"
                                className="size-4 shrink-0"
                              />
                            )}
                            {model.vision && (
                              <Eye
                                aria-label="Accepts images"
                                className="size-4 shrink-0"
                              />
                            )}
                            {model.tools && (
                              <Wrench
                                aria-label="Supports tools"
                                className="size-4 shrink-0"
                              />
                            )}
                          </span>
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
                        {onModelAction && (
                          <Button
                            variant="outline"
                            size="sm"
                            className="min-h-11 shrink-0 px-2"
                            disabled={busy !== null || !!loadingModel}
                            aria-label={`${model.loaded ? "Eject" : "Load"} ${model.display_name}`}
                            onKeyDown={(event) => event.stopPropagation()}
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
                        {current?.model_id === model.model_id &&
                          current?.connection_id === model.connection_id && (
                            <Check
                              className="model-selected-mark size-4 shrink-0 text-brand"
                              role="img"
                              aria-label="Selected for chat"
                            />
                          )}
                      </CommandItem>
                    ))}
                </CommandGroup>
              ),
            )
          ) : state === "loading" ? (
            <div aria-label="Loading models" className="space-y-3 p-4">
              <div className="skeleton h-10" />
              <div className="skeleton h-10" />
            </div>
          ) : state === "empty" ? (
            <p className="p-4 text-fg-2">No models on this connection.</p>
          ) : state === "offline" ? (
            <div className="p-4 text-danger">
              Offline ·{" "}
              <Button variant="outline" onClick={() => setOpen(false)}>
                Retry
              </Button>
            </div>
          ) : null}
          {models &&
            connections
              ?.filter(
                (connection) =>
                  connection.enabled && connection.reachable === false,
              )
              .map((connection) => (
                <CommandGroup key={connection.id} heading={connection.name}>
                  <p className="p-3 text-sm text-fg-3">
                    Offline · Check the connection in Settings
                  </p>
                </CommandGroup>
              ))}
          {state === "loading-model" && (
            <p className="flex items-center gap-2 p-4 text-fg-2">
              <LoaderCircle className="size-4 animate-spin" />
              Loading {current?.display_name ?? "model"}… {elapsed} s
            </p>
          )}
        </>
      </CommandList>
      <p className="shrink-0 border-t border-line p-3 text-xs text-fg-2">
        {`${models?.length ?? 0} models · capabilities reported by Ollama`}
        <span className="mt-1 block">
          Load selects the model for this chat.
        </span>
      </p>
    </Command>
  );
  if (phone)
    return (
      <>
        <div className="min-w-0">{trigger}</div>
        <Drawer open={open} onOpenChange={setOpen}>
          <DrawerContent>
            <DrawerHeader>
              <DrawerTitle>Choose model</DrawerTitle>
              <DrawerDescription>Local models on your Mac</DrawerDescription>
            </DrawerHeader>
            {content}
            <DrawerClose asChild>
              <Button variant="ghost" className="m-3">
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
        align="start"
        className="flex max-h-(--radix-popover-content-available-height) w-[min(420px,calc(100vw-32px))] flex-col overflow-hidden p-0"
      >
        {content}
      </PopoverContent>
    </Popover>
  );
}

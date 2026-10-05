import { useRef, useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  api,
  ApiError,
  type Bootstrap,
  type Model,
  type Preset,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  ChatControlsUnavailable,
  LiveChatSettings,
} from "@/components/settings/LiveChatSettings";
import PresetsPane from "@/components/settings/PresetsPane";
import { ModelRename } from "@/components/settings/ModelRename";
import { ModelPicker } from "@/components/app/ModelPicker";
import { fixtureModels } from "./ProductionFixtures";
import { useUI } from "@/stores/ui";
const seed: Preset = {
  id: "fake-preset",
  name: "Synthetic Focus",
  params: { temperature: 0.65 },
  system_prompt: "Invented preview instruction.",
  position: 0,
  created_at: "2026-10-05T12:00:00Z",
  updated_at: "2026-10-05T12:00:00Z",
};
export function EverydayPreview() {
  const [client] = useState(
      () => new QueryClient({ defaultOptions: { queries: { retry: false } } }),
    ),
    [area, setArea] = useState("Controls"),
    [model, setModel] = useState<Model>({
      ...fixtureModels[0],
      display_name: "Synthetic Display",
    }),
    [defaultId, setDefault] = useState<string | null>(null);
  const records = useRef<Preset[]>([seed]);
  const request: typeof api = async <T,>(
    url: string,
    body?: unknown,
    method?: string,
  ): Promise<T> => {
    const data = body as Partial<Preset> | undefined;
    if (url === "/presets" && !body) {
      if (area === "Preset error")
        throw new ApiError("synthetic_error", "Synthetic fixture unavailable");
      if (area === "Preset loading") return new Promise<T>(() => {});
      return (area === "Empty presets" ? [] : records.current) as T;
    }
    if (url === "/presets" && data) {
      if (
        records.current.some(
          (p) => p.name.toLowerCase() === data.name?.toLowerCase(),
        )
      )
        throw new ApiError("preset_name_taken", "Synthetic duplicate");
      const item = { ...seed, ...data, id: crypto.randomUUID() };
      records.current = [...records.current, item];
      return item as T;
    }
    if (url.startsWith("/presets/")) {
      const id = url.split("/").at(-1);
      if (method === "DELETE") {
        records.current = records.current.filter((p) => p.id !== id);
        if (defaultId === id) setDefault(null);
      } else
        records.current = records.current.map((p) =>
          p.id === id ? { ...p, ...data } : p,
        );
      return records.current.find((p) => p.id === id) as T;
    }
    if (url === "/settings") {
      setDefault(
        (body as { default_preset_id: string | null }).default_preset_id,
      );
      return {} as T;
    }
    throw Error("Unexpected synthetic endpoint");
  };
  const bootstrap: Bootstrap = {
    app_name: "Synthetic preview",
    version: "fake",
    data_dir: "Synthetic only",
    connections: [],
    features: { web_search: false },
    settings: { default_preset_id: defaultId },
  };
  return (
    <QueryClientProvider client={client}>
      <main className="design-page">
        <h1 className="mb-4 font-serif text-2xl">
          Everyday chat · synthetic preview
        </h1>
        <div className="mb-5 flex flex-wrap gap-2">
          {[
            "Controls",
            "Controls loading",
            "Controls error",
            "Presets",
            "Empty presets",
            "Preset error",
            "Preset loading",
            "Model rename",
          ].map((name) => (
            <Button
              key={name}
              variant={area === name ? "default" : "outline"}
              onClick={() => setArea(name)}
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
        <section
          className="max-w-xl rounded-lg border border-line bg-surface"
          aria-label="Everyday preview"
        >
          {area === "Controls loading" || area === "Controls error" ? (
            <ChatControlsUnavailable
              failed={area === "Controls error"}
              retry={() => {}}
            />
          ) : area === "Controls" ? (
            <LiveChatSettings
              model={model}
              request={request}
              queryScope={["everyday"]}
              onSave={async () => true}
              onDefaults={async () => true}
              onContext={async (length) => {
                setModel((m) => ({ ...m, context_length: length }));
                return true;
              }}
            />
          ) : area === "Model rename" ? (
            <div className="space-y-4 p-5">
              <ModelPicker
                models={[model]}
                current={model}
                onChoose={() => {}}
              />
              <ModelRename
                model={model}
                onSave={async (name) => {
                  setModel((m) => ({ ...m, display_name: name ?? m.model_id }));
                  return true;
                }}
              />
            </div>
          ) : (
            <div className="space-y-4 p-5">
              <PresetsPane
                key={area}
                bootstrap={bootstrap}
                request={request}
                queryScope={["everyday", area]}
              />
            </div>
          )}
        </section>
      </main>
    </QueryClientProvider>
  );
}

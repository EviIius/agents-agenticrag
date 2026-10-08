import { useState } from "react";
import { toast } from "sonner";
import { CommandPalette } from "@/components/app/CommandPalette";
import {
  LegacyImportDialog,
  type ImportPreview,
} from "@/components/settings/LegacyImportDialog";
import { Button } from "@/components/ui/button";
import { showUpdateToast } from "@/lib/pwa";
import type { Chat } from "@/lib/api";
const chats: Chat[] = [
  {
    id: "design-polish",
    title: "Synthetic example chat",
    title_source: "user",
    web_enabled: false,
    library_enabled: false,
    pinned: false,
    params: {},
    created_at: "2026-10-03",
    updated_at: "2026-10-03",
    snippet: "Fake fixture. No real chat content.",
  },
];
export function PolishPreview() {
  const [state, setState] = useState<
    "ready" | "empty" | "loading" | "error" | null
  >(null);
  const [importState, setImportState] = useState<ImportPreview>("ready");
  const action = () => toast("Synthetic command · no live action");
  return (
    <section className="my-8 space-y-4" aria-label="Phase 3 previews">
      <h2 className="text-xl font-medium">Polish · synthetic previews</h2>
      <div className="flex flex-wrap gap-2">
        {(["ready", "empty", "loading", "error"] as const).map((state) => (
          <Button variant="outline" key={state} onClick={() => setState(state)}>
            Preview palette {state}
          </Button>
        ))}
        <Button
          variant="outline"
          onClick={() =>
            showUpdateToast(() => toast("Synthetic update · no reload"))
          }
        >
          Preview app update
        </Button>
      </div>
      <div className="space-y-3 rounded-lg border border-line p-4">
        <h3 className="text-sm font-medium">
          Legacy import · synthetic states
        </h3>
        <div className="flex flex-wrap gap-2">
          {(
            [
              "ready",
              "loading",
              "missing",
              "status-error",
              "importing",
              "failed",
            ] as const
          ).map((value) => (
            <Button
              key={value}
              variant="outline"
              onClick={() => setImportState(value)}
            >
              Import preview {value}
            </Button>
          ))}
        </div>
        <LegacyImportDialog key={importState} preview={importState} />
      </div>
      <CommandPalette
        open={state !== null}
        onOpenChange={(open) => {
          if (!open) setState(null);
        }}
        onChat={action}
        previewChats={state === "ready" ? chats : []}
        previewState={
          state === "loading" || state === "error" || state === "empty"
            ? state
            : undefined
        }
        actions={{
          newChat: action,
          switchModel: action,
          toggleSearch: action,
          chatSettings: action,
          settings: action,
          toggleTheme: action,
          shortcuts: action,
        }}
      />
    </section>
  );
}

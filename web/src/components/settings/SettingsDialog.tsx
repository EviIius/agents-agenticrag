import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useUI } from "@/stores/ui";
import type { ThemePreference } from "@/lib/theme";
import { toast } from "sonner";
const basePanes = [
  "Connections",
  "Models",
  "Appearance",
  "Data",
  "Shortcuts",
  "About",
] as const;
export function SettingsDialog({
  renderPane,
  searchEnabled = false,
}: {
  renderPane?: (pane: string) => import("react").ReactNode;
  searchEnabled?: boolean;
}) {
  const panes: string[] = searchEnabled
    ? [...basePanes.slice(0, 2), "Search", ...basePanes.slice(2)]
    : [...basePanes];
  const ui = useUI();
  const pane = ui.settingsPane;
  const setPane = (settingsPane: string) => ui.set({ settingsPane });
  return (
    <Dialog
      open={ui.settings}
      onOpenChange={(settings) => ui.set({ settings })}
    >
      <DialogContent className="settings-dialog flex max-h-[min(640px,90dvh)] max-w-[920px] sm:max-w-[920px] flex-col overflow-y-auto p-6 sm:w-[calc(100vw-48px)]">
        <DialogTitle>Settings</DialogTitle>
        <DialogDescription>
          {renderPane
            ? "Local models · your preferences"
            : "Workbench · foundation preview"}
        </DialogDescription>
        <div className="mt-4 flex min-h-0 flex-1 flex-col gap-6 sm:flex-row">
          <nav
            aria-label="Settings sections"
            className="flex shrink-0 flex-wrap gap-1 sm:w-40 sm:flex-col"
          >
            {panes.map((name) => (
              <Button
                key={name}
                variant="ghost"
                onClick={() => setPane(name)}
                className={`min-h-11 justify-start ${pane === name ? "bg-surface-2" : ""}`}
                aria-current={pane === name ? "page" : undefined}
              >
                {name}
              </Button>
            ))}
          </nav>
          <section
            aria-label={pane}
            className="min-w-0 flex-1 space-y-5 overflow-y-auto pb-6"
          >
            <h2 className="text-lg font-medium">{pane}</h2>
            {pane !== "Appearance" && renderPane ? (
              renderPane(pane)
            ) : pane === "Appearance" ? (
              <>
                <fieldset>
                  <legend className="mb-2 font-medium">Theme</legend>
                  <div className="flex gap-2">
                    {(["system", "light", "dark"] as ThemePreference[]).map(
                      (theme) => (
                        <Button
                          key={theme[0].toUpperCase() + theme.slice(1)}
                          variant={theme === ui.theme ? "default" : "outline"}
                          className="min-h-11 capitalize"
                          aria-pressed={theme === ui.theme}
                          onClick={() => ui.set({ theme })}
                        >
                          {theme[0].toUpperCase() + theme.slice(1)}
                        </Button>
                      ),
                    )}
                  </div>
                </fieldset>
                <fieldset>
                  <legend className="mb-2 font-medium">Answer font</legend>
                  <div className="flex gap-2">
                    {(["serif", "sans"] as const).map((answerFont) => (
                      <Button
                        key={answerFont}
                        variant={
                          answerFont === ui.answerFont ? "secondary" : "outline"
                        }
                        className="min-h-11 capitalize"
                        aria-pressed={answerFont === ui.answerFont}
                        onClick={() => ui.set({ answerFont })}
                      >
                        {answerFont === "serif"
                          ? "Serif · Newsreader"
                          : "Sans · Geist"}
                      </Button>
                    ))}
                  </div>
                </fieldset>
                <fieldset>
                  <legend className="mb-2 font-medium">Text size</legend>
                  <div className="flex gap-2">
                    {(["S", "M", "L"] as const).map((textSize) => (
                      <Button
                        key={textSize}
                        variant={
                          textSize === ui.textSize ? "secondary" : "outline"
                        }
                        className="min-h-11 min-w-11"
                        aria-pressed={textSize === ui.textSize}
                        onClick={() => ui.set({ textSize })}
                      >
                        {textSize}
                      </Button>
                    ))}
                  </div>
                </fieldset>
                <label className="block space-y-2">
                  <span className="font-medium">Reduce motion</span>
                  <Select
                    value={ui.reduceMotion}
                    onValueChange={(value) =>
                      ui.set({ reduceMotion: value as "system" | "always" })
                    }
                  >
                    <SelectTrigger
                      className="h-11 w-full"
                      aria-label="Reduce motion"
                    >
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="system">Follow system</SelectItem>
                      <SelectItem value="always">Always</SelectItem>
                    </SelectContent>
                  </Select>
                </label>
                <label className="block space-y-2">
                  <span className="font-medium">
                    What should Workbench call you?
                  </span>
                  <Input
                    className="h-11"
                    value={ui.name}
                    onChange={(event) => ui.set({ name: event.target.value })}
                    placeholder="Your name (optional)"
                  />
                </label>
              </>
            ) : pane === "Connections" ? (
              <>
                <p className="text-fg-2">Fake runtime · fixture connection</p>
                <p className="text-fg-2">
                  Connect Ollama in Settings › Connections.
                </p>
              </>
            ) : pane === "Models" ? (
              <>
                <p>fake-chat · fake-reasoning · fake-vision</p>
                <p className="text-fg-2">
                  Your real models will appear in Phase 1. The standard Llama
                  70B variant will be hidden; the 16K variant will be kept.
                </p>
              </>
            ) : pane === "Shortcuts" ? (
              <dl className="space-y-4">
                <div>
                  <dt>New chat</dt>
                  <dd>⌘ / Ctrl + Shift + O</dd>
                </div>
                <div>
                  <dt>Search chats</dt>
                  <dd>⌘ / Ctrl + K</dd>
                </div>
                <div>
                  <dt>Settings</dt>
                  <dd>⌘ / Ctrl + ,</dd>
                </div>
              </dl>
            ) : pane === "Data" ? (
              <>
                <p className="text-fg-2">
                  Import and export arrive in Phase 3. Existing app data is
                  preserved in the legacy backup.
                </p>
                <Button disabled variant="outline">
                  Import legacy chats · Phase 3
                </Button>
              </>
            ) : (
              <>
                <p>Workbench 1.0.0-alpha.0</p>
                <p className="text-fg-2">Foundation preview · Fake runtime</p>
                <Button
                  variant="outline"
                  onClick={() =>
                    toast("Foundation preview · no live model connection")
                  }
                >
                  Connection summary
                </Button>
              </>
            )}
          </section>
        </div>
      </DialogContent>
    </Dialog>
  );
}

import config from "../../../../shared/config.json";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "@/components/ui/dialog";
import { X } from "lucide-react";
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
import { useCallback, useEffect, useRef } from "react";
function centerActiveTab(nav: HTMLElement) {
  const selected = nav.querySelector<HTMLElement>('[aria-current="page"]');
  if (selected && nav.scrollWidth > nav.clientWidth)
    nav.scrollTo({
      left:
        selected.offsetLeft -
        nav.offsetLeft -
        (nav.clientWidth - selected.offsetWidth) / 2,
      behavior: "instant",
    });
}
const basePanes = [
  "Connections",
  "Models",
  "Presets",
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
    ? [
        ...basePanes.slice(0, 3),
        "Search",
        "Transcription",
        ...basePanes.slice(3),
      ]
    : [...basePanes.slice(0, 3), "Transcription", ...basePanes.slice(3)];
  const ui = useUI();
  const pane = ui.settingsPane;
  const navigation = useRef<HTMLElement>(null);
  const bindNavigation = useCallback((element: HTMLElement | null) => {
    navigation.current = element;
    if (element) centerActiveTab(element);
  }, []);
  useEffect(() => {
    if (!ui.settings || !navigation.current) return;
    centerActiveTab(navigation.current);
  }, [pane, ui.settings]);
  const setPane = (settingsPane: string) => ui.set({ settingsPane });
  return (
    <Dialog
      open={ui.settings}
      onOpenChange={(settings) => ui.set({ settings })}
    >
      <DialogContent
        showCloseButton={false}
        className="settings-dialog flex max-h-[min(640px,90dvh)] max-w-[920px] sm:max-w-[920px] flex-col overflow-hidden p-6 sm:w-[calc(100vw-48px)]"
      >
        <header className="flex shrink-0 items-center justify-between gap-3">
          <DialogTitle>Settings</DialogTitle>
          <DialogClose asChild>
            <Button variant="ghost" size="icon" aria-label="Close settings">
              <X />
            </Button>
          </DialogClose>
        </header>
        <DialogDescription>Local models · your preferences</DialogDescription>
        <div className="mt-4 flex min-h-0 flex-1 flex-col gap-6 sm:flex-row">
          <nav
            ref={bindNavigation}
            aria-label="Settings sections"
            className="flex shrink-0 gap-1 overflow-x-auto px-2 py-1 sm:w-40 sm:flex-col sm:px-0"
          >
            {panes.map((name) => (
              <Button
                key={name === "Search" ? "Web search" : name}
                variant="ghost"
                onClick={() => setPane(name)}
                className={`min-h-11 shrink-0 justify-start ${pane === name ? "bg-brand-soft text-brand" : ""}`}
                aria-current={pane === name ? "page" : undefined}
              >
                {name === "Search" ? "Web search" : name}
              </Button>
            ))}
          </nav>
          <section
            key={pane}
            aria-label={pane === "Search" ? "Web search" : pane}
            className="settings-pane min-h-0 min-w-0 flex-1 space-y-5 overflow-y-auto pb-6"
          >
            <h2 className="text-lg font-medium">
              {pane === "Search" ? "Web search" : pane}
            </h2>
            {pane === "Appearance" ? (
              <>
                <fieldset>
                  <legend className="mb-2 font-medium">Theme</legend>
                  <div className="flex flex-wrap gap-2">
                    {(["system", "light", "dark"] as ThemePreference[]).map(
                      (theme) => (
                        <Button
                          key={theme[0].toUpperCase() + theme.slice(1)}
                          variant={theme === ui.theme ? "default" : "outline"}
                          data-slot="segmented-choice"
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
                  <div className="flex flex-wrap gap-2">
                    {(["serif", "sans"] as const).map((answerFont) => (
                      <Button
                        key={answerFont}
                        variant={
                          answerFont === ui.answerFont ? "secondary" : "outline"
                        }
                        data-slot="segmented-choice"
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
                  <div className="flex flex-wrap gap-2">
                    {(["S", "M", "L"] as const).map((textSize) => (
                      <Button
                        key={textSize}
                        variant={
                          textSize === ui.textSize ? "secondary" : "outline"
                        }
                        data-slot="segmented-choice"
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
                    What should {config.APP_NAME} call you?
                  </span>
                  <Input
                    className="h-11"
                    value={ui.name}
                    onChange={(event) => ui.set({ name: event.target.value })}
                    placeholder="Your name (optional)"
                  />
                </label>
              </>
            ) : (
              renderPane?.(pane)
            )}
          </section>
        </div>
      </DialogContent>
    </Dialog>
  );
}

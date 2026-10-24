import { Button } from "@/components/ui/button";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import { resolvedAppearance } from "@/lib/appearance";
import type { GreetingMode } from "@/lib/greetings";
import { PALETTES } from "@/lib/palettes";
import { useUI } from "@/stores/ui";

/** TH1 · Each swatch renders in its own palette, in the mode it would open in. */
export function PalettePicker() {
  const ui = useUI();
  const systemDark = useMediaQuery("(prefers-color-scheme: dark)");
  return (
    <fieldset>
      <legend className="mb-2 font-medium">Palette</legend>
      <div className="palette-grid">
        {PALETTES.map((palette) => (
          <button
            key={palette.id}
            type="button"
            className="palette-option"
            aria-pressed={palette.id === ui.palette}
            data-palette-option={palette.id}
            onClick={() => ui.set({ palette: palette.id })}
          >
            <span
              className="palette-sample"
              data-palette={palette.id}
              data-theme={resolvedAppearance(ui.theme, palette.id, systemDark)}
              aria-hidden="true"
            >
              <span className="palette-sample-bubble" />
              <span className="palette-sample-text" />
              <span className="palette-sample-text" />
              <span className="palette-sample-link" />
              <span className="palette-sample-send" />
            </span>
            <span className="palette-name">{palette.name}</span>
            <span className="palette-blurb">{palette.description}</span>
          </button>
        ))}
      </div>
      <p className="mt-3 text-xs text-fg-3">
        The Home Screen icon may keep its previous appearance. Changing the
        palette still updates the app.
      </p>
    </fieldset>
  );
}

const GREETING_LABELS: Record<GreetingMode, string> = {
  languages: "Five languages",
  surprise: "Surprise me",
  english: "English only",
};

export function GreetingChoice() {
  const ui = useUI();
  return (
    <fieldset>
      <legend className="mb-2 font-medium">New-chat greeting</legend>
      <div className="flex flex-wrap gap-2">
        {(Object.keys(GREETING_LABELS) as GreetingMode[]).map((greeting) => (
          <Button
            key={greeting}
            variant={greeting === ui.greeting ? "secondary" : "outline"}
            data-slot="segmented-choice"
            className="min-h-11"
            aria-pressed={greeting === ui.greeting}
            onClick={() => ui.set({ greeting })}
          >
            {GREETING_LABELS[greeting]}
          </Button>
        ))}
      </div>
      <p className="mt-2 text-xs text-fg-3">
        Plays once when you start a new chat, then settles on English. Reduce
        motion shows the English line only.
      </p>
    </fieldset>
  );
}

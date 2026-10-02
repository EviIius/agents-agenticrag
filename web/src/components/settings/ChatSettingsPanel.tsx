import { useState } from "react";
import { X } from "lucide-react";
import { Slider } from "@/components/ui/slider";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { IconButton } from "@/components/app/IconButton";
import { useUI } from "@/stores/ui";
import { toast } from "sonner";
function NumericControl({
  label,
  max,
  initial,
  step = 1,
}: {
  label: string;
  max: number;
  initial: number;
  step?: number;
}) {
  const [defaulted, setDefaulted] = useState(true);
  const [value, setValue] = useState(initial);
  return (
    <fieldset className="mb-6">
      <legend className="mb-2 text-sm font-medium">{label}</legend>
      <label className="mb-3 flex min-h-11 items-center gap-2 text-xs text-fg-2">
        <input
          type="checkbox"
          checked={defaulted}
          onChange={(event) => setDefaulted(event.target.checked)}
        />
        Default · {defaulted ? "Model default" : "Custom value"}
      </label>
      <div className="flex items-center gap-4">
        <Slider
          aria-label={label}
          min={0}
          max={max}
          step={step}
          value={[value]}
          disabled={defaulted}
          onValueChange={(values) => setValue(values[0] ?? 0)}
        />
        <Input
          type="number"
          min={0}
          max={max}
          step={step}
          disabled={defaulted}
          aria-label={`${label} value`}
          className="h-11 w-24"
          value={value}
          onChange={(event) =>
            setValue(Math.min(max, Math.max(0, Number(event.target.value))))
          }
        />
      </div>
    </fieldset>
  );
}
export function ChatSettingsPanel({ drawer = false }: { drawer?: boolean }) {
  const { set } = useUI();
  const [reset, setReset] = useState(0);
  return (
    <section className="p-5" aria-label="Chat settings controls">
      {!drawer && (
        <header className="mb-6 flex items-center justify-between">
          <h2 className="text-base font-medium">Chat settings</h2>
          <IconButton
            label="Close chat settings"
            onClick={() => set({ panel: false })}
          >
            <X />
          </IconButton>
        </header>
      )}
      <p className="mb-6 text-xs text-fg-2">
        Design preview · open the main app to save settings and send them to a
        model.
      </p>
      <label htmlFor="system-prompt" className="mb-2 block font-medium">
        System prompt
      </label>
      <Textarea
        id="system-prompt"
        placeholder="Optional instructions…"
        className="mb-6 min-h-24"
      />
      <div key={reset}>
        <h3 className="mb-3 font-medium">Sampling</h3>
        <NumericControl label="Temperature" max={2} initial={0.7} step={0.1} />
        <NumericControl label="Top P" max={1} initial={0.9} step={0.05} />
        <h3 className="mb-3 font-medium">Length & context</h3>
        <NumericControl label="Output limit" max={32768} initial={4096} />
        <NumericControl label="Context window" max={65536} initial={16384} />
      </div>
      <footer className="flex flex-col gap-2">
        <Button variant="ghost" onClick={() => setReset(reset + 1)}>
          Reset to model defaults
        </Button>
        <Button
          variant="outline"
          onClick={() => toast("Fake runtime · defaults preview")}
        >
          Save as defaults for fake-chat
        </Button>
      </footer>
    </section>
  );
}

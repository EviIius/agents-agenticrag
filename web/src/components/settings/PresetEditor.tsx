import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { api, type Params, type Preset } from "@/lib/api";
import { failureCopy } from "@/lib/errors";
import {
  SamplingFields,
  samplingDraft,
  samplingParams,
  samplingValid,
} from "./SamplingFields";
export default function PresetEditor({
  preset,
  params = {},
  prompt = null,
  onClose,
  onSaved,
  request = api,
}: {
  preset?: Preset;
  params?: Params;
  prompt?: string | null;
  onClose: () => void;
  onSaved: () => void;
  request?: typeof api;
}) {
  const [name, setName] = useState(preset?.name ?? ""),
    [system, setSystem] = useState(preset?.system_prompt ?? prompt ?? ""),
    [useDefault, setDefault] = useState(
      (preset ? preset.system_prompt : prompt) == null,
    ),
    [values, setValues] = useState(samplingDraft(preset?.params ?? params)),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false);
  const save = async () => {
    setBusy(true);
    setError("");
    try {
      await request(
        preset ? `/presets/${preset.id}` : "/presets",
        {
          name: name.trim(),
          system_prompt: useDefault ? null : system,
          params: samplingParams(values),
        },
        preset ? "PATCH" : "POST",
      );
      onSaved();
      onClose();
    } catch (e) {
      setError(failureCopy(e));
    } finally {
      setBusy(false);
    }
  };
  return (
    <Dialog
      open
      onOpenChange={(open) => {
        if (!open && !busy) onClose();
      }}
    >
      <DialogContent className="flex max-h-[90dvh] flex-col overflow-hidden">
        <DialogHeader>
          <DialogTitle>{preset ? "Edit preset" : "Save as preset"}</DialogTitle>
          <DialogDescription>
            Copies the system prompt and sampling values. Unset values use your
            saved model defaults. Reasoning and context stay with the model.
          </DialogDescription>
        </DialogHeader>
        <div className="min-h-0 overflow-y-auto">
          <label className="mb-4 block text-sm">
            Name
            <Input
              aria-label="Preset name"
              maxLength={80}
              value={name}
              onChange={(e) => {
                setName(e.target.value);
                setError("");
              }}
            />
          </label>
          <label className="mb-3 flex min-h-11 items-center gap-2 text-sm">
            <Switch
              aria-label="Use default preset system prompt"
              checked={useDefault}
              onCheckedChange={setDefault}
            />
            Use default system prompt
          </label>
          <Textarea
            className="mb-5"
            aria-label="Preset system prompt"
            disabled={useDefault}
            value={system}
            onChange={(e) => setSystem(e.target.value)}
          />
          <SamplingFields
            prefix="preset"
            values={values}
            onChange={setValues}
          />
        </div>
        {error && (
          <p role="alert" className="text-sm text-danger">
            {error}
          </p>
        )}
        <div className="flex justify-end gap-2 border-t border-line pt-3">
          <Button variant="ghost" disabled={busy} onClick={onClose}>
            Cancel
          </Button>
          <Button
            disabled={busy || !name.trim() || !samplingValid(values)}
            onClick={() => void save()}
          >
            {busy ? "Saving…" : "Save preset"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

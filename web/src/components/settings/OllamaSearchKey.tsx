import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export function OllamaSearchKey({
  hasKey,
  onSave,
  onRemove,
}: {
  hasKey: boolean;
  onSave: (key: string) => Promise<boolean>;
  onRemove: () => Promise<boolean>;
}) {
  const [key, setKey] = useState("");
  const [saving, setSaving] = useState(false);
  return (
    <div className="mt-3 space-y-3">
      <p className="text-sm text-fg-2">
        Search uses your free Ollama account. Your chat model runs on this Mac.
        Usage limits apply.
      </p>
      <a
        className="text-sm underline"
        href="https://ollama.com/settings/keys"
        target="_blank"
        rel="noopener noreferrer"
      >
        Create an Ollama API key
      </a>
      <label className="block text-sm">
        Ollama search API key {hasKey ? "· Key saved" : ""}
        <Input
          type="password"
          autoComplete="off"
          value={key}
          onChange={(e) => setKey(e.target.value)}
        />
      </label>
      <div className="flex flex-wrap gap-2">
        <Button
          variant="outline"
          disabled={saving || !key.trim()}
          onClick={async () => {
            setSaving(true);
            try {
              if (await onSave(key.trim())) setKey("");
            } finally {
              setSaving(false);
            }
          }}
        >
          Save Ollama key
        </Button>
        <Button
          variant="ghost"
          disabled={saving || !hasKey}
          onClick={async () => {
            setSaving(true);
            try {
              await onRemove();
            } finally {
              setSaving(false);
            }
          }}
        >
          Remove Ollama key
        </Button>
      </div>
    </div>
  );
}

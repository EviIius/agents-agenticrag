import { lazy, Suspense, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowUp, ArrowDown } from "lucide-react";
import { api, type Bootstrap, type Preset } from "@/lib/api";
import { failureCopy } from "@/lib/errors";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogCancel,
  AlertDialogAction,
} from "@/components/ui/alert-dialog";
const PresetEditor = lazy(() => import("./PresetEditor"));
export default function PresetsPane({
  bootstrap,
  request = api,
  queryScope = [],
}: {
  bootstrap?: Bootstrap;
  request?: typeof api;
  queryScope?: string[];
}) {
  const query = useQueryClient(),
    presets = useQuery({
      queryKey: ["presets", ...queryScope],
      queryFn: () => request<Preset[]>("/presets"),
    });
  const [editing, setEditing] = useState<Preset | null | undefined>(),
    [removing, setRemoving] = useState<Preset>(),
    [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  const mutate = async (url: string, body: unknown, method: string) => {
    setBusy(true);
    setError("");
    try {
      await request(url, body, method);
      await query.invalidateQueries({ queryKey: ["presets", ...queryScope] });
      await query.invalidateQueries({ queryKey: ["bootstrap"] });
      return true;
    } catch (e) {
      setError(failureCopy(e));
      return false;
    } finally {
      setBusy(false);
    }
  };
  const move = async (p: Preset, index: number) => {
    const list = [...(presets.data ?? [])],
      old = list.findIndex((v) => v.id === p.id);
    list.splice(old, 1);
    list.splice(index, 0, p);
    setBusy(true);
    setError("");
    try {
      for (const [position, item] of list.entries())
        await request(`/presets/${item.id}`, { position }, "PATCH");
      await query.invalidateQueries({ queryKey: ["presets", ...queryScope] });
    } catch (e) {
      setError(failureCopy(e));
    } finally {
      setBusy(false);
    }
  };
  return (
    <>
      <h2 className="text-lg font-medium">Presets</h2>
      <p className="text-sm text-fg-2">
        Copy a system prompt and sampling values into a chat. Existing chats
        keep their own copy.
      </p>
      <Button onClick={() => setEditing(null)}>New preset</Button>
      {presets.isPending && <p role="status">Loading presets…</p>}
      {presets.isError && (
        <p role="alert">
          Couldn't load presets.{" "}
          <Button variant="ghost" onClick={() => void presets.refetch()}>
            Retry
          </Button>
        </p>
      )}
      {presets.data?.length === 0 && (
        <p className="text-sm text-fg-3">No presets yet.</p>
      )}
      {presets.data?.map((p, i) => (
        <article
          key={p.id}
          aria-label={`Preset ${p.name}`}
          className="space-y-3 rounded-lg border border-line p-4"
        >
          <h3 className="font-medium break-words">{p.name}</h3>
          <p className="text-xs text-fg-3">
            {Object.keys(p.params ?? {}).length} sampling{" "}
            {Object.keys(p.params ?? {}).length === 1 ? "value" : "values"} ·{" "}
            {p.system_prompt === null
              ? "Default system prompt"
              : "Custom system prompt"}
          </p>
          <label className="flex min-h-11 items-center gap-2 text-sm">
            <Switch
              aria-label={`Use ${p.name} for new chats`}
              disabled={busy}
              checked={bootstrap?.settings.default_preset_id === p.id}
              onCheckedChange={(checked) =>
                void mutate(
                  "/settings",
                  { default_preset_id: checked ? p.id : null },
                  "PATCH",
                )
              }
            />
            Use for new chats
          </label>
          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              disabled={busy}
              onClick={() => setEditing(p)}
            >
              Edit / rename
            </Button>
            <Button
              variant="ghost"
              disabled={busy}
              onClick={() => setRemoving(p)}
            >
              Delete
            </Button>
            <Button
              variant="ghost"
              size="icon"
              aria-label={`Move ${p.name} up`}
              disabled={busy || i === 0}
              onClick={() => void move(p, i - 1)}
            >
              <ArrowUp />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              aria-label={`Move ${p.name} down`}
              disabled={busy || i === (presets.data?.length ?? 0) - 1}
              onClick={() => void move(p, i + 1)}
            >
              <ArrowDown />
            </Button>
          </div>
        </article>
      ))}
      {error && (
        <p role="alert" className="text-sm text-danger">
          {error}
        </p>
      )}
      {editing !== undefined && (
        <Suspense fallback={<p role="status">Opening preset editor…</p>}>
          <PresetEditor
            preset={editing ?? undefined}
            request={request}
            onClose={() => setEditing(undefined)}
            onSaved={() =>
              void query.invalidateQueries({
                queryKey: ["presets", ...queryScope],
              })
            }
          />
        </Suspense>
      )}
      <AlertDialog
        open={!!removing}
        onOpenChange={(open) => {
          if (!open && !busy) setRemoving(undefined);
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete preset?</AlertDialogTitle>
            <AlertDialogDescription>
              Deletes {removing?.name}. Existing chats keep their copied
              settings. If this is your default preset, new chats return to
              model defaults.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={busy}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              disabled={busy}
              onClick={async (e) => {
                e.preventDefault();
                if (
                  removing &&
                  (await mutate(`/presets/${removing.id}`, undefined, "DELETE"))
                )
                  setRemoving(undefined);
              }}
            >
              Delete preset
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}

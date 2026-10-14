import { useRef, useState } from "react";
import { Link } from "react-router";
import {
  LoaderCircle,
  ArrowLeft,
  Play,
  Undo2,
  Redo2,
  MoreHorizontal,
  CircleAlert,
  PanelLeftOpen,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { IconButton } from "@/components/app/IconButton";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useUI } from "@/stores/ui";
import { useStudio } from "./store";
export function StudioTopBar({
  problems,
  run,
  action,
  outline,
  minimap,
  retry,
  running = false,
}: {
  problems: number;
  run: () => void;
  action: (name: string) => void;
  outline: boolean;
  minimap: boolean;
  retry: () => void;
  running?: boolean;
}) {
  const name = useStudio((s) => s.draft.name),
    status = useStudio((s) => s.saveState),
    past = useStudio((s) => s.past.length),
    future = useStudio((s) => s.future.length),
    edit = useStudio((s) => s.edit),
    undo = useStudio((s) => s.undo),
    redo = useStudio((s) => s.redo);
  const [editing, setEditing] = useState(false),
    [value, setValue] = useState(name);
  const ui = useUI();
  const cancelled = useRef(false);
  const rename = () => {
    if (cancelled.current) return;
    if (value.trim()) edit((d) => ({ ...d, name: value.trim() }), "name");
    setEditing(false);
  };
  return (
    <header className="wf-topbar">
      <IconButton
        className="wf-sidebar-open"
        label="Open sidebar"
        onClick={() => ui.set({ sidebar: true })}
      >
        <PanelLeftOpen />
      </IconButton>
      <Link to="/workflows" aria-label="Back to Workflows" className="wf-back">
        <ArrowLeft className="size-4" />
        <span>Workflows</span>
      </Link>
      <span className="wf-crumb-separator">/</span>
      {editing ? (
        <input
          autoFocus
          aria-label="Workflow name"
          className="wf-title-input wf-workflow-name"
          value={value}
          maxLength={80}
          onChange={(e) => setValue(e.target.value)}
          onBlur={rename}
          onKeyDown={(e) => {
            if (e.key === "Enter") rename();
            if (e.key === "Escape") {
              cancelled.current = true;
              setEditing(false);
            }
          }}
        />
      ) : (
        <Button
          className="wf-workflow-name"
          variant="ghost"
          onClick={() => {
            cancelled.current = false;
            setValue(name);
            setEditing(true);
          }}
        >
          {name}
        </Button>
      )}
      <span className="wf-save-status" data-state={status} role="status">
        <span className="wf-status-dot" />
        {status === "saved" ? (
          "Saved"
        ) : status === "saving" ? (
          "Saving…"
        ) : status === "conflict" ? (
          "Changed elsewhere"
        ) : (
          <Button variant="ghost" onClick={retry}>
            Couldn't save · Retry
          </Button>
        )}
      </span>
      <div className="flex-1" />
      {problems > 0 && (
        <Button
          variant="ghost"
          className="wf-problem-count"
          aria-label={`${problems} workflow problems`}
          onClick={() => action("problems")}
        >
          <CircleAlert className="size-4" />
          {problems}
        </Button>
      )}
      <IconButton
        className="wf-undo"
        label="Undo"
        disabled={!past}
        onClick={undo}
      >
        <Undo2 />
      </IconButton>
      <IconButton
        className="wf-undo"
        label="Redo"
        disabled={!future}
        onClick={redo}
      >
        <Redo2 />
      </IconButton>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <IconButton label="Workflow menu">
            <MoreHorizontal />
          </IconButton>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={() => action("view")}>
            {outline ? "Canvas view" : "Outline view"}
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => action("settings")}>
            Workflow settings
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => action("versions")}>
            Versions
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => action("problems")}>
            Problems
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => action("minimap")}>
            {minimap ? "Hide minimap" : "Show minimap"}
          </DropdownMenuItem>
          <DropdownMenuItem onClick={undo} disabled={!past}>
            Undo
          </DropdownMenuItem>
          <DropdownMenuItem onClick={redo} disabled={!future}>
            Redo
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => action("json")}>
            View JSON
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => action("export")}>
            Export JSON
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => action("import")}>
            Import JSON
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => action("duplicate")}>
            Duplicate
          </DropdownMenuItem>
          <DropdownMenuItem
            className="text-danger"
            onClick={() => action("delete")}
          >
            Delete
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      <Button
        className="wf-run-button"
        title={problems ? `Fix ${problems} problems to run` : "Run workflow"}
        onClick={run}
      >
        {running ? (
          <LoaderCircle className="size-4 activity-spin" />
        ) : (
          <Play className="size-4" />
        )}
        Run
      </Button>
    </header>
  );
}

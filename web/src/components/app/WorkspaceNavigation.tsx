import { createContext, useContext } from "react";
import { useWorkflowActivity } from "@/stores/workflow-activity";
import { Link, useLocation } from "react-router";
import { Images, Workflow } from "lucide-react";
import { IconButton } from "./IconButton";

export const WorkspaceContext = createContext<{
  chatPath: string;
  modelKey?: string;
}>({ chatPath: "/" });
export const useWorkspace = () => useContext(WorkspaceContext);

export function WorkspaceNavigation({
  collapsed = false,
  close,
}: {
  collapsed?: boolean;
  close?: () => void;
}) {
  const { pathname } = useLocation();
  const navigation = useWorkspace();
  const paused = useWorkflowActivity((s) => s.pausedCount > 0);
  return (
    <nav aria-label="Workspace" className="mb-4 space-y-1">
      {[
        { path: "/workflows", label: "Workflows", Icon: Workflow },
        { path: "/images", label: "Images", Icon: Images },
      ].map(({ path, label, Icon }) => {
        const active = pathname === path || pathname.startsWith(path + "/");
        const style = active
          ? "border-brand bg-surface-3"
          : "border-transparent hover:bg-surface-2";
        const link = (
          <Link
            to={path}
            aria-label={label}
            state={navigation}
            onClick={close}
            aria-current={active ? "page" : undefined}
            className={`flex min-h-11 items-center gap-3 rounded-md border-l-2 px-3 text-sm font-medium lg:min-h-10 ${style}`}
          >
            <Icon className="size-4 shrink-0" />
            {!collapsed && label}
            {path === "/workflows" && paused && (
              <span
                className="size-1.5 rounded-full bg-warning"
                role="img"
                aria-label="A workflow is waiting for you"
              />
            )}
          </Link>
        );
        return collapsed ? (
          <IconButton
            key={path}
            label={label}
            asChild
            className={`border-l-2 ${style}`}
          >
            {link}
          </IconButton>
        ) : (
          <div key={path}>{link}</div>
        );
      })}
    </nav>
  );
}

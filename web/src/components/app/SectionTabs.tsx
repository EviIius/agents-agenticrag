import { Link } from "react-router";

export function SectionTabs({
  active,
  chatPath = "/",
  modelKey,
}: {
  active: "chat" | "workflows";
  chatPath?: string;
  modelKey?: string;
}) {
  return (
    <nav
      aria-label="Workspace"
      className="flex shrink-0 gap-1 border-b border-line px-4"
    >
      {(["chat", "workflows"] as const).map((section) => (
        <Link
          key={section}
          to={section === "chat" ? chatPath : "/workflows"}
          state={section === "workflows" ? { chatPath, modelKey } : undefined}
          aria-current={active === section ? "page" : undefined}
          className={`flex min-h-11 items-center border-b-2 px-4 text-sm font-medium ${active === section ? "border-brand text-brand" : "border-transparent text-fg-2 hover:text-fg"}`}
        >
          {section === "chat" ? "Chat" : "Workflows"}
        </Link>
      ))}
    </nav>
  );
}

import { useState, Suspense, lazy } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { FoldersGroup } from "@/components/app/FoldersGroup";
import { ChatList } from "@/components/app/ChatList";
import { ChatMenu } from "@/components/app/ChatMenu";
import { BackupPane } from "@/components/settings/BackupPane";
import type { FolderAction } from "@/components/app/FolderDialog";
import { Button } from "@/components/ui/button";
import { useUI } from "@/stores/ui";
import type { Chat, Folder } from "@/lib/api";
const FolderDialog = lazy(() => import("@/components/app/FolderDialog"));
const folder: Folder = {
  id: "fake-folder",
  name: "Invented Orchard",
  count: 1,
  position: 0,
  created_at: "2026-10-05",
  updated_at: "2026-10-05",
};
const chat: Chat = {
  id: "fake-folder-chat",
  title: "Invented lantern chat",
  title_source: "user",
  folder_id: folder.id,
  folder_name: folder.name,
  created_at: "2026-10-05",
  updated_at: "2026-10-05",
  pinned: false,
  params: {},
  web_enabled: false,
  library_enabled: false,
  research_enabled: false,
};
export const organizationStates = [
  "Folders",
  "Empty folders",
  "Loading folders",
  "Folder error",
  "Empty folder",
  "Loading chats",
  "Chat error",
  "Folder menu",
  "Search result",
  "Move menu",
  "Create folder",
  "Rename folder",
  "Delete folder",
  "Save error",
  "Saving",
  "Backup ready",
  "No backup",
  "Backup warning",
  "Backup loading",
  "Backup error",
  "Backing up",
];
export function OrganizationPreview() {
  const [client] = useState(
    () => new QueryClient({ defaultOptions: { queries: { retry: false } } }),
  );
  const [state, setState] = useState("Folders"),
    [action, setAction] = useState<FolderAction | null>(null);
  const ui = useUI();
  const menu = (chat: Chat) => (
    <ChatMenu
      chat={chat}
      ui={ui}
      mutate={async () => true}
      setAction={() => {}}
      folders={[folder]}
      onFolderAction={setAction}
    />
  );
  return (
    <QueryClientProvider client={client}>
      <main className="p-4 sm:p-8">
        <h1 className="mb-4 font-serif text-2xl">
          Organization · synthetic preview
        </h1>
        <div className="mb-4 flex flex-wrap gap-2">
          {organizationStates.map((name) => (
            <Button
              key={name}
              variant={name === state ? "default" : "outline"}
              onClick={() => {
                setState(name);
                setAction(
                  name === "Create folder"
                    ? { kind: "create" }
                    : name === "Rename folder" ||
                        name === "Save error" ||
                        name === "Saving"
                      ? { kind: "rename", folder }
                      : name === "Delete folder"
                        ? { kind: "delete", folder }
                        : null,
                );
              }}
            >
              {name}
            </Button>
          ))}
        </div>
        <div className="mb-6 flex gap-2">
          {["light", "dark"].map((theme) => (
            <Button
              key={theme}
              variant="outline"
              onClick={() => ui.set({ theme: theme as "light" | "dark" })}
            >
              {theme}
            </Button>
          ))}
        </div>
        <div
          data-slot="organization-fixture"
          className="max-w-xl rounded-xl border border-line bg-sidebar-bg p-3"
        >
          {state.startsWith("Backup") ||
          state === "No backup" ||
          state === "Backing up" ? (
            <BackupPane
              key={state}
              fixture={
                state === "Backup loading"
                  ? "loading"
                  : state === "Backup error"
                    ? "error"
                    : state === "Backing up"
                      ? "busy"
                      : state === "No backup"
                        ? { last_at: null, count: 0, bytes: 0 }
                        : {
                            last_at: "2026-10-05T03:30:00",
                            count: 7,
                            bytes: 43000000,
                            warning:
                              state === "Backup warning"
                                ? "Backup skipped: not enough free disk space. Free space and try again."
                                : null,
                          }
              }
            />
          ) : state === "Search result" || state === "Move menu" ? (
            <ChatList
              chats={[chat]}
              search={state === "Search result" ? "lantern" : ""}
              menu={menu}
              onOpen={() => {}}
              hasNext={false}
              onNext={() => {}}
            />
          ) : (
            <FoldersGroup
              key={state}
              folders={state === "Empty folders" ? [] : [folder]}
              loading={state === "Loading folders"}
              failed={state === "Folder error"}
              retry={() => {}}
              onAction={setAction}
              menu={menu}
              onOpen={() => {}}
              fixture={
                state === "Loading chats"
                  ? "loading"
                  : state === "Chat error"
                    ? "error"
                    : state === "Empty folder"
                      ? []
                      : [chat]
              }
            />
          )}
        </div>
        {action && (
          <Suspense fallback={null}>
            <FolderDialog
              key={state}
              action={action}
              onClose={() => setAction(null)}
              preview
              fixture={
                state === "Saving"
                  ? "busy"
                  : state === "Save error"
                    ? "error"
                    : undefined
              }
            />
          </Suspense>
        )}
      </main>
    </QueryClientProvider>
  );
}

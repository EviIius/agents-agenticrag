import { useState } from "react";
import { ChatTitle } from "@/components/app/ChatTitle";
import { OfflineNotice } from "@/components/app/OfflineNotice";
import { HistoryList } from "@/components/app/HistoryList";
import { useUI } from "@/stores/ui";
export function RefinementPreview() {
  const [title, setTitle] = useState("Synthetic inline title");
  const [search, setSearch] = useState("");
  const ui = useUI();
  return (
    <section
      className="design-card mb-8"
      aria-label="Visual refinement previews"
    >
      <h2 className="mb-5 text-lg font-medium">
        4D · title, history loading and offline
      </h2>
      <header className="topbar mb-5">
        <ChatTitle
          title={title}
          onRename={async (next) => {
            setTitle(next);
            return true;
          }}
        />
      </header>
      <div className="mb-5 max-w-sm">
        <HistoryList
          search={search}
          setSearch={setSearch}
          history={{
            isLoading: true,
            hasNextPage: false,
            isFetchingNextPage: false,
            fetchNextPage: async () => {},
          }}
          historyItems={[]}
          menu={() => null}
          ui={ui}
        />
      </div>
      <OfflineNotice
        detail="TypeError: Synthetic offline fixture"
        onRetry={() => {}}
      />
    </section>
  );
}

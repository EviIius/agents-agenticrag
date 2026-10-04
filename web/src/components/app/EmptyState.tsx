import { useEffect, useState, type ReactNode } from "react";
import { useUI } from "@/stores/ui";
let hasEntered = false;
export function EmptyState({
  ui,
  composer,
}: {
  ui: ReturnType<typeof useUI.getState>;
  composer: ReactNode;
}) {
  const [fresh, setFresh] = useState(!hasEntered);
  useEffect(() => {
    hasEntered = true;
    const timer = setTimeout(() => {
      setFresh(false);
    }, 400);
    return () => clearTimeout(timer);
  }, []);
  return (
    <section className="empty-chat" data-empty-fresh={fresh || undefined}>
      <h1 className="greeting">
        {new Date().getHours() < 12
          ? "Good morning"
          : new Date().getHours() < 18
            ? "Good afternoon"
            : "Good evening"}
        {ui.name ? `, ${ui.name}` : ""}
      </h1>
      {composer}
      <p className="mt-4 text-center text-xs text-fg-3">
        Your models. Your Mac.
      </p>
    </section>
  );
}

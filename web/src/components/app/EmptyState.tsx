import type { ReactNode } from "react";
import { AnimatedGreeting } from "./AnimatedGreeting";
export function EmptyState({ composer }: { composer: ReactNode }) {
  return (
    <section className="empty-chat">
      <AnimatedGreeting />
      {composer}
      <p className="mt-4 text-center text-xs text-fg-3">
        Your models. Your Mac.
      </p>
    </section>
  );
}

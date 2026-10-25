import type { ReactNode } from "react";
import { AnimatedGreeting } from "./AnimatedGreeting";
import { PaletteScene } from "./PaletteScene";
export function EmptyState({ composer }: { composer: ReactNode }) {
  return (
    <section className="empty-chat">
      <PaletteScene />
      <AnimatedGreeting />
      {composer}
      <p className="mt-4 text-center text-xs text-fg-3">
        Your models. Your Mac.
      </p>
    </section>
  );
}

import { useEffect, useState } from "react";
import { useReducedMotion } from "@/hooks/useReducedMotion";

export default function DropOverlay({ active }: { active: boolean }) {
  const [visible, setVisible] = useState(active);
  const reduced = useReducedMotion();
  useEffect(() => {
    if (active) {
      setVisible(true);
      return;
    }
    const timer = setTimeout(() => setVisible(false), reduced ? 0 : 120);
    return () => clearTimeout(timer);
  }, [active, reduced]);
  if (!visible && !active) return null;
  return (
    <div
      className="attachment-drop"
      data-slot="drop-overlay"
      data-state={active ? "open" : "closed"}
      role="status"
      aria-hidden={!active}
    >
      <div className="attachment-drop-card">
        <div className="attachment-drop-fan" aria-hidden>
          <span className="attachment-badge" data-tone="input">
            IMG
          </span>
          <span className="attachment-badge" data-tone="review">
            PDF
          </span>
          <span className="attachment-badge" data-tone="input">
            TXT
          </span>
        </div>
        <h2>Drop to attach</h2>
        <p>Images, PDF, Word, text and recordings · up to 8 files</p>
      </div>
    </div>
  );
}

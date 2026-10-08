import { useState } from "react";

/** Retain only presentation data while Radix completes an exit. Logical close is immediate. */
export function useOverlaySession<T>(value: T | null, identity = "") {
  const open = value !== null;
  const [snapshot, setSnapshot] = useState({
    value,
    identity,
    open,
    sequence: 0,
  });
  if (
    open !== snapshot.open ||
    (open && (value !== snapshot.value || identity !== snapshot.identity))
  ) {
    const next = {
      value: value ?? snapshot.value,
      identity: open ? identity : snapshot.identity,
      open,
      sequence:
        snapshot.sequence +
        (open && (!snapshot.open || identity !== snapshot.identity) ? 1 : 0),
    };
    setSnapshot(next);
    return next;
  }
  return snapshot;
}

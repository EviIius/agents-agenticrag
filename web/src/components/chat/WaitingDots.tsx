export function WaitingDots() {
  return (
    <div
      role="status"
      data-slot="waiting-dots"
      className="flex min-h-12 items-center gap-1.5"
    >
      <span className="sr-only">Generating response</span>
      {[0, 1, 2].map((dot) => (
        <span
          key={dot}
          aria-hidden="true"
          className="size-1.5 rounded-full bg-fg-3"
        />
      ))}
    </div>
  );
}

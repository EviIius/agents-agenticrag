export function AtelierMark({ think = false }: { think?: boolean }) {
  return (
    <svg
      className="atelier-mark"
      data-loop={think ? "think" : "draw"}
      viewBox="0 0 24 24"
      width="18"
      height="18"
      aria-hidden="true"
    >
      <path
        className="mark-base"
        d="M5.6 19.4 12 4.6l6.4 14.8"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.6"
        strokeLinecap="round"
        strokeLinejoin="round"
        opacity="0.22"
      />
      <path
        className="mark-a"
        d="M5.6 19.4 12 4.6l6.4 14.8"
        pathLength="40"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle
        className="mark-dot"
        cx="12"
        cy="16.3"
        r="1.7"
        fill="currentColor"
      />
    </svg>
  );
}

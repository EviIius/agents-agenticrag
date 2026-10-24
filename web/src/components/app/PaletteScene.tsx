import type { CSSProperties } from "react";
import { paletteById } from "@/lib/palettes";
import { useUI } from "@/stores/ui";

/** [left %, size px, rise s, delay s, sway px]. Fixed so every render is the same. */
const BUBBLES = [
  [7, 18, 15, -1, 14],
  [16, 34, 21, -7, -18],
  [27, 12, 12, -4, 10],
  [39, 24, 18, -12, -12],
  [52, 16, 14, -9, 16],
  [63, 40, 24, -3, -22],
  [74, 14, 13, -10, 12],
  [85, 28, 19, -15, -14],
  [94, 10, 11, -6, 8],
] as const;

/**
 * TH1 · Aero's scene behind the new chat: sky, sun and lens flare (or aurora at
 * night), clouds, a glass skyline over water, green hills and rising bubbles.
 * Decorative only. Colours come from aero.css; motion from motion.css, which the
 * reduced-motion rules stop. Renders nothing for palettes without glass.
 */
export function PaletteScene() {
  const glass = useUI((s) => paletteById(s.palette).glass);
  if (!glass) return null;
  return (
    <div className="aero-scene" aria-hidden="true">
      <div className="aero-rays" />
      <div className="aero-sun" />
      <div className="aero-flare" />
      <div className="aero-aurora" />
      <div className="aero-cloud aero-cloud-a" />
      <div className="aero-cloud aero-cloud-b" />
      <svg
        className="aero-skyline"
        viewBox="0 0 1200 240"
        preserveAspectRatio="xMidYMax slice"
      >
        <defs>
          <linearGradient id="aero-glass" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" className="aero-stop-top" />
            <stop offset="0.6" className="aero-stop-mid" />
            <stop offset="1" className="aero-stop-low" />
          </linearGradient>
          <pattern
            id="aero-windows"
            width="12"
            height="9"
            patternUnits="userSpaceOnUse"
          >
            <rect width="12" height="1.4" className="aero-window" />
          </pattern>
          <g id="aero-towers">
            <path d="M40 240V140a23 23 0 0 1 46 0v100z" />
            <path d="M96 240V94q0-4 4-4h26q4 0 4 4v146z" />
            <path d="M142 240V86l24-58 24 58v154z" />
            <path d="M204 240V146q0-10 10-10h50q10 0 10 10v94z" />
            <path d="M288 240v-86c0-34 18-62 40-62s40 28 40 62v86z" />
            <path d="M384 240V58a20 20 0 0 1 40 0v182z" />
            <path d="M438 240V128h18v-26h30v26h18v112z" />
            <path d="M520 240v-60q0-12 12-12h96q12 0 12 12v60z" />
            <path d="M652 240V104l52-22v158z" />
            <path d="M716 240v-70a54 54 0 0 1 108 0v70z" />
            <path d="M836 240V70h40v170z" />
            <path d="M888 240v-120q30-40 60 0v120z" />
            <path d="M960 240V112a24 24 0 0 1 48 0v128z" />
            <path d="M1020 240V96l18-40 18 40v144z" />
            <path d="M1068 240v-80q0-8 8-8h52q8 0 8 8v80z" />
            <path d="M1146 240V120a22 22 0 0 1 44 0v120z" />
          </g>
        </defs>
        <use href="#aero-towers" fill="url(#aero-glass)" />
        <use href="#aero-towers" fill="url(#aero-windows)" />
        <use href="#aero-towers" className="aero-tower-edge" />
        <path className="aero-spire" d="M856 70V34" />
        <path
          className="aero-rail"
          d="M0 204C220 174 420 226 640 200S1000 172 1200 190"
        />
      </svg>
      <div className="aero-water">
        <svg
          className="aero-reflection"
          viewBox="0 0 1200 240"
          preserveAspectRatio="xMidYMin slice"
        >
          <use
            href="#aero-towers"
            fill="url(#aero-glass)"
            transform="matrix(1 0 0 -1 0 240)"
          />
        </svg>
      </div>
      <div className="aero-hill aero-hill-back" />
      <div className="aero-hill aero-hill-front" />
      {BUBBLES.map(([x, size, rise, delay, sway]) => (
        <span
          key={x}
          className="aero-bubble"
          style={
            {
              "--x": `${x}%`,
              "--size": `${size}px`,
              "--rise-dur": `${rise}s`,
              "--rise-delay": `${delay}s`,
              "--sway": `${sway}px`,
            } as CSSProperties
          }
        />
      ))}
    </div>
  );
}

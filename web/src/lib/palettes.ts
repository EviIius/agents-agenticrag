/**
 * TH1 · Palettes. Colours live in styles/palettes.css; this file holds what
 * the code needs to know about each one: its name, which modes it offers, and
 * its motion personality (greeting style, theme reveal, status words, icon).
 */
export const PALETTE_IDS = [
  "cobalt",
  "lime",
  "paper",
  "ember",
  "orchid",
  "midnight",
  "mono",
  "aero",
] as const;
export type PaletteId = (typeof PALETTE_IDS)[number];
export type GreetingStyle =
  "rise" | "roll" | "type" | "glow" | "bloom" | "decode" | "fade" | "bubble";
export type Palette = {
  id: PaletteId;
  name: string;
  description: string;
  /** Midnight offers dark only; the theme choice is ignored while it is on. */
  modes: readonly ("light" | "dark")[];
  greeting: GreetingStyle;
  /** "circle" spreads the new theme from the tap point; "fade" crossfades. */
  reveal: "circle" | "fade";
  /** Playful status words while a model works. Cobalt keeps the original 36. */
  words: readonly string[] | null;
  /** Aero only: glass materials and a full scene behind the new chat (styles/aero.css). */
  glass?: boolean;
};

export const PALETTES: readonly Palette[] = [
  {
    id: "cobalt",
    name: "Cobalt",
    description: "Warm paper white with a cobalt accent. The original.",
    modes: ["light", "dark"],
    greeting: "rise",
    reveal: "circle",
    words: null,
  },
  {
    id: "lime",
    name: "Lime",
    description: "Off-white pages, black text, a lime-green accent.",
    modes: ["light", "dark"],
    greeting: "roll",
    reveal: "circle",
    words: [
      "Zesting",
      "Squeezing",
      "Sprouting",
      "Fizzing",
      "Ripening",
      "Peeling",
      "Muddling",
      "Zipping",
      "Juicing",
      "Popping",
      "Buzzing",
      "Pruning",
      "Sparkling",
      "Shaking it up",
      "Tasting",
      "Growing",
    ],
  },
  {
    id: "paper",
    name: "Paper",
    description: "Cream pages and warm ink, set in Newsreader throughout.",
    modes: ["light", "dark"],
    greeting: "type",
    reveal: "circle",
    words: [
      "Inking",
      "Drafting",
      "Annotating",
      "Leafing through",
      "Typesetting",
      "Blotting",
      "Underlining",
      "Folding",
      "Penciling",
      "Proofreading",
      "Binding",
      "Dog-earing",
      "Margin-noting",
      "Copying out",
      "Turning pages",
      "Sharpening the nib",
    ],
  },
  {
    id: "ember",
    name: "Ember",
    description: "Warm white with a burnt-orange glow.",
    modes: ["light", "dark"],
    greeting: "glow",
    reveal: "circle",
    words: [
      "Kindling",
      "Stoking",
      "Smoldering",
      "Forging",
      "Tempering",
      "Glowing",
      "Simmering",
      "Toasting",
      "Searing",
      "Banking the coals",
      "Fanning",
      "Hammering",
      "Annealing",
      "Warming up",
      "Catching",
      "Sparking",
    ],
  },
  {
    id: "orchid",
    name: "Orchid",
    description: "Soft lavender greys with a violet accent.",
    modes: ["light", "dark"],
    greeting: "bloom",
    reveal: "circle",
    words: [
      "Blooming",
      "Unfurling",
      "Budding",
      "Pollinating",
      "Cultivating",
      "Misting",
      "Grafting",
      "Arranging",
      "Petal-counting",
      "Tending",
      "Pressing flowers",
      "Repotting",
      "Opening up",
      "Rooting",
      "Leafing",
      "Nurturing",
    ],
  },
  {
    id: "midnight",
    name: "Midnight",
    description: "True black for OLED screens, with an electric-blue accent.",
    modes: ["dark"],
    greeting: "decode",
    reveal: "circle",
    words: [
      "Stargazing",
      "Orbiting",
      "Charting constellations",
      "Drifting",
      "Moonwalking",
      "Dreaming",
      "Tracing comets",
      "Listening to static",
      "Counting stars",
      "Night-flying",
      "Eclipsing",
      "Signalling",
      "Calibrating the dish",
      "Waxing",
      "Waning",
      "Scanning the sky",
    ],
  },
  {
    id: "mono",
    name: "Mono",
    description: "Black, white and greys. Nothing else.",
    modes: ["light", "dark"],
    greeting: "fade",
    reveal: "fade",
    words: [
      "Thinking",
      "Reading",
      "Considering",
      "Working",
      "Checking",
      "Composing",
      "Weighing",
      "Outlining",
      "Comparing",
      "Writing",
      "Reviewing",
      "Settling",
    ],
  },
  {
    id: "aero",
    name: "Aero",
    description:
      "Glass, sky and water: the bright 2000s future, with glossy controls and a skyline.",
    modes: ["light", "dark"],
    greeting: "bubble",
    reveal: "circle",
    glass: true,
    words: [
      "Syncing",
      "Hydrating",
      "Photosynthesizing",
      "Buffering",
      "Defragmenting",
      "Polishing the glass",
      "Catching rays",
      "Bubbling up",
      "Refreshing",
      "Rendering reflections",
      "Breezing through",
      "Charging",
      "Shimmering",
      "Streaming",
      "Updating the future",
      "Connecting",
    ],
  },
];

export function isPaletteId(value: unknown): value is PaletteId {
  return (PALETTE_IDS as readonly unknown[]).includes(value);
}

export function paletteById(id: PaletteId): Palette {
  return PALETTES.find((palette) => palette.id === id) ?? PALETTES[0];
}

export const PALETTE_STORAGE_KEY = "workbench-palette";

export function readPalette(): PaletteId {
  try {
    const value = localStorage.getItem(PALETTE_STORAGE_KEY);
    return isPaletteId(value) ? value : "cobalt";
  } catch {
    return "cobalt";
  }
}

/** Home Screen and tab icons. Cobalt keeps the original paths. */
export function paletteIcons(id: PaletteId) {
  const base = id === "cobalt" ? "/icons" : `/icons/${id}`;
  return {
    svg: `${base}/mark.svg`,
    touch: `${base}/apple-touch-icon.png`,
    manifest:
      id === "cobalt"
        ? "/manifest.webmanifest"
        : `/manifests/${id}.webmanifest`,
  };
}

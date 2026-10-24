import type { GreetingStyle } from "./palettes";

export type DayPart = "morning" | "afternoon" | "evening";
export type GreetingMode = "languages" | "surprise" | "english";
export const GREETING_MODES: readonly GreetingMode[] = [
  "languages",
  "surprise",
  "english",
];

/** Same boundaries as the original greeting: before noon, before 6 pm, after. */
export function dayPart(hour: number): DayPart {
  return hour < 12 ? "morning" : hour < 18 ? "afternoon" : "evening";
}

/** `lang` is a BCP 47 tag so the right serif fallback is used for each script. */
export const GREETINGS = {
  en: ["Good morning", "Good afternoon", "Good evening"],
  es: ["Buenos días", "Buenas tardes", "Buenas noches"],
  fr: ["Bonjour", "Bon après-midi", "Bonsoir"],
  ja: ["おはよう", "こんにちは", "こんばんは"],
  ko: ["좋은 아침", "좋은 오후", "좋은 저녁"],
  it: ["Buongiorno", "Buon pomeriggio", "Buonasera"],
  de: ["Guten Morgen", "Guten Tag", "Guten Abend"],
  pt: ["Bom dia", "Boa tarde", "Boa noite"],
  zh: ["早上好", "下午好", "晚上好"],
  hi: ["सुप्रभात", "नमस्ते", "शुभ संध्या"],
} as const satisfies Record<string, readonly [string, string, string]>;
export type GreetingLang = keyof typeof GREETINGS;

/** J13: Spanish, French, Japanese, Korean, Italian, then English. */
export const DEFAULT_LANGUAGES: readonly GreetingLang[] = [
  "es",
  "fr",
  "ja",
  "ko",
  "it",
];

export type GreetingWord = { lang: GreetingLang; text: string };

export function greetingText(lang: GreetingLang, hour: number) {
  return GREETINGS[lang][
    ["morning", "afternoon", "evening"].indexOf(dayPart(hour))
  ];
}

/** The words to show, always ending in English. */
export function greetingRun(
  mode: GreetingMode,
  hour: number,
  random: () => number = Math.random,
): GreetingWord[] {
  const pool = (Object.keys(GREETINGS) as GreetingLang[]).filter(
    (lang) => lang !== "en",
  );
  let langs: GreetingLang[] = [];
  if (mode === "languages") langs = [...DEFAULT_LANGUAGES];
  if (mode === "surprise") {
    const shuffled = [...pool];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    langs = shuffled.slice(0, DEFAULT_LANGUAGES.length);
  }
  return [...langs, "en" as const].map((lang) => ({
    lang,
    text: greetingText(lang, hour),
  }));
}

/** Split into user-perceived characters, so accents and Hangul stay whole. */
export function graphemes(text: string): string[] {
  if (typeof Intl !== "undefined" && "Segmenter" in Intl) {
    const segmenter = new Intl.Segmenter(undefined, {
      granularity: "grapheme",
    });
    return Array.from(segmenter.segment(text), (part) => part.segment);
  }
  return Array.from(text);
}

/**
 * Timing for one word. Every word gets the same slot, so five languages and the
 * English landing, name fade and final glow stay under 4.5 s.
 */
export const GREETING_TIMING = {
  slot: 700,
  exit: 120,
  name: 200,
  glow: 700,
  /** How long one character's entrance lasts, per style (matches motion.css). */
  char: {
    rise: 300,
    roll: 320,
    type: 1,
    glow: 300,
    bloom: 320,
    decode: 240,
    fade: 200,
    bubble: 320,
  } satisfies Record<GreetingStyle, number>,
  /** The latest a character may start, so long words compress their stagger. */
  spread: {
    rise: 220,
    roll: 240,
    type: 300,
    glow: 220,
    bloom: 200,
    decode: 0,
    fade: 0,
    bubble: 220,
  } satisfies Record<GreetingStyle, number>,
  step: {
    rise: 18,
    roll: 28,
    type: 42,
    glow: 18,
    bloom: 26,
    decode: 0,
    fade: 0,
    bubble: 24,
  } satisfies Record<GreetingStyle, number>,
  decode: 320,
};

/** Start delay in ms for each character. Bloom opens from the middle out. */
export function charDelays(count: number, style: GreetingStyle): number[] {
  if (count === 0) return [];
  const step = Math.min(
    GREETING_TIMING.step[style],
    count > 1 ? GREETING_TIMING.spread[style] / (count - 1) : 0,
  );
  const middle = (count - 1) / 2;
  return Array.from({ length: count }, (_, i) =>
    Math.round((style === "bloom" ? Math.abs(i - middle) : i) * step),
  );
}

/** When the last character has finished entering. */
export function enterDuration(count: number, style: GreetingStyle) {
  if (style === "decode") return GREETING_TIMING.decode;
  return Math.max(0, ...charDelays(count, style)) + GREETING_TIMING.char[style];
}

/** Total time of a run, for tests and the 4.5 s budget. */
export function runDuration(run: GreetingWord[], style: GreetingStyle) {
  if (run.length <= 1) return 0;
  const last = run.at(-1)!;
  return (
    (run.length - 1) * GREETING_TIMING.slot +
    Math.max(
      enterDuration(graphemes(last.text).length, style) + GREETING_TIMING.name,
      style === "glow" ? GREETING_TIMING.glow : 0,
    )
  );
}

const GLYPHS = "▚▞▖▗▘▝░▒<>/\\|=+*#%01";
/**
 * Midnight's decode: characters left of `progress` (0–1) are resolved, the rest
 * show random glyphs. Spaces stay spaces so the word keeps its shape.
 */
export function scramble(
  chars: string[],
  progress: number,
  random: () => number = Math.random,
): string[] {
  const resolved = Math.floor(
    chars.length * Math.min(1, Math.max(0, progress)),
  );
  return chars.map((char, i) =>
    i < resolved || char.trim() === ""
      ? char
      : GLYPHS[Math.floor(random() * GLYPHS.length)],
  );
}

/** What a screen reader hears: the final English greeting. */
export function greetingLabel(hour: number, name: string) {
  return `${greetingText("en", hour)}${name ? `, ${name}` : ""}`;
}

import { describe, expect, it } from "vitest";
import {
  DEFAULT_LANGUAGES,
  GREETINGS,
  charDelays,
  dayPart,
  graphemes,
  greetingLabel,
  greetingRun,
  runDuration,
  scramble,
} from "./greetings";
import { PALETTES } from "./palettes";

describe("Greeting run", () => {
  it("keeps the original day boundaries", () => {
    expect(dayPart(0)).toBe("morning");
    expect(dayPart(11)).toBe("morning");
    expect(dayPart(12)).toBe("afternoon");
    expect(dayPart(17)).toBe("afternoon");
    expect(dayPart(18)).toBe("evening");
  });
  it("plays the five default languages and always lands on English", () => {
    const run = greetingRun("languages", 9);
    expect(run.map((word) => word.lang)).toEqual([...DEFAULT_LANGUAGES, "en"]);
    expect(run.at(-1)?.text).toBe("Good morning");
    expect(greetingRun("english", 20)).toEqual([
      { lang: "en", text: "Good evening" },
    ]);
  });
  it("draws five different languages for Surprise me", () => {
    let seed = 0.13;
    const random = () => (seed = (seed * 9301 + 0.49297) % 1);
    const run = greetingRun("surprise", 14, random);
    const langs = run.map((word) => word.lang);
    expect(langs).toHaveLength(6);
    expect(new Set(langs).size).toBe(6);
    expect(langs.at(-1)).toBe("en");
  });
  it("stays inside the 4.5 s budget for every palette, language and time of day", () => {
    for (const palette of PALETTES)
      for (const hour of [9, 14, 20]) {
        const langs = Object.keys(GREETINGS) as (keyof typeof GREETINGS)[];
        const longest = langs
          .filter((lang) => lang !== "en")
          .map((lang) => ({ lang, text: GREETINGS[lang][0] }));
        const run = [
          ...longest.slice(0, 5),
          { lang: "en" as const, text: greetingRun("english", hour)[0].text },
        ];
        expect(runDuration(run, palette.greeting)).toBeLessThanOrEqual(4500);
      }
  });
  it("labels the heading with the English line and the name", () => {
    expect(greetingLabel(9, "Jake")).toBe("Good morning, Jake");
    expect(greetingLabel(20, "")).toBe("Good evening");
  });
});

describe("Characters", () => {
  it("keeps accents and Hangul syllables whole", () => {
    expect(graphemes("días")).toHaveLength(4);
    expect(graphemes("좋은 아침")).toHaveLength(5);
  });
  it("compresses the stagger for long words and opens bloom from the middle", () => {
    expect(Math.max(...charDelays(30, "rise"))).toBeLessThanOrEqual(220);
    const bloom = charDelays(5, "bloom");
    expect(bloom[2]).toBe(0);
    expect(bloom[0]).toBe(bloom[4]);
    expect(charDelays(4, "fade")).toEqual([0, 0, 0, 0]);
  });
  it("decodes left to right and keeps spaces", () => {
    const chars = graphemes("Good evening");
    const half = scramble(chars, 0.5, () => 0);
    expect(half.slice(0, 6).join("")).toBe("Good e");
    expect(half[4]).toBe(" ");
    expect(scramble(chars, 1).join("")).toBe("Good evening");
  });
});

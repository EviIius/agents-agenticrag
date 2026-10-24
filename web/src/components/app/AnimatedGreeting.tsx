import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { useUI } from "@/stores/ui";
import { useReducedMotion } from "@/hooks/useReducedMotion";
import { paletteById, type GreetingStyle } from "@/lib/palettes";
import {
  GREETING_TIMING,
  charDelays,
  enterDuration,
  graphemes,
  greetingLabel,
  greetingRun,
  scramble,
  type GreetingLang,
} from "@/lib/greetings";

/** Plays once per fresh new chat; returning within a minute shows it still. */
const QUIET_MS = 60_000;
let lastPlayed = 0;

function Word({
  text,
  lang,
  style,
  leaving,
  animate,
}: {
  text: string;
  lang: GreetingLang;
  style: GreetingStyle;
  leaving: boolean;
  animate: boolean;
}) {
  const chars = useMemo(() => graphemes(text), [text]);
  const delays = useMemo(
    () => charDelays(chars.length, style),
    [chars.length, style],
  );
  const decoding = animate && style === "decode";
  const [shown, setShown] = useState(() =>
    decoding ? scramble(chars, 0) : chars,
  );
  useEffect(() => {
    if (!decoding) return;
    let frame = 0;
    const start = performance.now();
    const tick = (now: number) => {
      const progress = (now - start) / GREETING_TIMING.decode;
      setShown(progress >= 1 ? chars : scramble(chars, progress));
      if (progress < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [chars, decoding]);
  if (!animate)
    return (
      <span className="greet-word" lang={lang}>
        {text}
      </span>
    );
  return (
    <span
      className="greet-word"
      lang={lang}
      data-leaving={leaving || undefined}
    >
      {(decoding ? shown : chars).map((char, i) => (
        <span className="greet-cell" key={i}>
          <span
            className="greet-char"
            style={{ "--d": `${delays[i] ?? 0}ms` } as CSSProperties}
          >
            {char}
          </span>
        </span>
      ))}
      {style === "type" && <span className="greet-caret" />}
    </span>
  );
}

/**
 * TH2 · The new-chat greeting. Rolls through a few languages in the palette's
 * style, then lands on English with the user's name. Screen readers hear only
 * the final English line. Reduced motion shows that line at once.
 */
export function AnimatedGreeting({
  replay = 0,
  always = false,
}: {
  /** A new value plays the greeting again (design pages). */
  replay?: number;
  /** Skip the one-minute quiet period (design pages). */
  always?: boolean;
}) {
  const name = useUI((s) => s.name);
  const mode = useUI((s) => s.greeting);
  const style = paletteById(useUI((s) => s.palette)).greeting;
  const reduced = useReducedMotion();
  const [hour] = useState(() => new Date().getHours());
  // A new `replay` value picks a new run (and a new surprise set).
  const run = useMemo(() => greetingRun(mode, hour), [mode, hour, replay]);
  const last = run.length - 1;
  const [state, setState] = useState(() => ({
    replay,
    mode,
    animate:
      !reduced && last > 0 && (always || Date.now() - lastPlayed > QUIET_MS),
    step: 0,
    leaving: false,
    landed: false,
  }));
  if (state.replay !== replay || state.mode !== mode)
    setState({
      replay,
      mode,
      animate: !reduced && last > 0,
      step: 0,
      leaving: false,
      landed: false,
    });
  else if (reduced && state.animate)
    setState({ ...state, animate: false, leaving: false, landed: true });
  const animate = state.animate && !reduced;
  const step = animate ? Math.min(state.step, last) : last;
  useEffect(() => {
    if (!animate) return;
    lastPlayed = Date.now();
    const timers: ReturnType<typeof setTimeout>[] = [];
    if (step < last) {
      timers.push(
        setTimeout(
          () => setState((s) => ({ ...s, leaving: true })),
          GREETING_TIMING.slot - GREETING_TIMING.exit,
        ),
        setTimeout(
          () => setState((s) => ({ ...s, step: s.step + 1, leaving: false })),
          GREETING_TIMING.slot,
        ),
      );
    } else {
      timers.push(
        setTimeout(
          () => setState((s) => ({ ...s, landed: true })),
          enterDuration(graphemes(run[last].text).length, style),
        ),
      );
    }
    return () => timers.forEach(clearTimeout);
  }, [animate, step, last, run, style]);
  const word = run[step];
  const showName = !!name && (!animate || step === last);
  return (
    <h1
      className="greeting"
      data-motion="ambient"
      data-style={style}
      data-animate={animate || undefined}
      data-landed={!animate || state.landed || undefined}
      aria-label={greetingLabel(hour, name)}
    >
      <span className="greeting-line" aria-hidden="true">
        <Word
          key={`${state.replay}-${step}`}
          text={word.text}
          lang={word.lang}
          style={style}
          leaving={animate && state.leaving}
          animate={animate}
        />
        {showName && (
          <span
            className="greeting-name"
            style={
              {
                "--d": `${animate ? enterDuration(graphemes(word.text).length, style) : 0}ms`,
              } as CSSProperties
            }
          >
            , {name}
          </span>
        )}
      </span>
    </h1>
  );
}
